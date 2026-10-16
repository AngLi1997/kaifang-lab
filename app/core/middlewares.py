"""请求级中间件：后台任务调度与 HTTP 审计日志。"""

import json
import re
from datetime import datetime
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.dependency import AuthControl
from app.models.admin import AuditLog, User

from .bgtask import BgTasks


class SimpleBaseMiddleware:
    """纯 ASGI 中间件基类，为 HTTP 请求提供 `before_request`/`after_request` 钩子。"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        response = await self.before_request(request) or self.app
        await response(request.scope, request.receive, send)
        await self.after_request(request)

    async def before_request(self, request: Request):  # pylint: disable=unused-argument
        """请求处理前调用；返回值作为实际处理请求的 ASGI 应用，返回 `None` 时使用 `self.app`。"""
        return self.app

    async def after_request(self, request: Request):  # pylint: disable=unused-argument
        """响应发送后调用。"""
        return None


class BackGroundTaskMiddleware(SimpleBaseMiddleware):
    """为每个请求创建后台任务容器，并在响应发送后执行其中的任务。"""

    async def before_request(self, request):
        """在请求上下文中创建后台任务容器。"""
        await BgTasks.init_bg_tasks_obj()

    async def after_request(self, request):
        """执行请求期间登记的后台任务。"""
        await BgTasks.execute_tasks()


class HttpAuditLogMiddleware(BaseHTTPMiddleware):
    """把匹配 `methods` 且不在 `exclude_paths` 中的请求写入 `AuditLog`。"""

    def __init__(self, app, methods: list[str], exclude_paths: list[str]):
        super().__init__(app)
        self.methods = methods
        self.exclude_paths = exclude_paths
        self.audit_log_paths = ["/api/v1/auditlog/list"]
        self.max_body_size = 1024 * 1024  # 1MB 响应体大小限制

    async def get_request_args(self, request: Request) -> dict:
        """合并查询参数与 JSON 或表单请求体；上传文件只记录文件名。"""
        args = {}
        # 获取查询参数
        for key, value in request.query_params.items():
            args[key] = value

        # 获取请求体
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                args.update(body)
            except json.JSONDecodeError:
                try:
                    body = await request.form()
                    # args.update(body)
                    for k, v in body.items():
                        if hasattr(v, "filename"):  # 文件上传行为
                            args[k] = v.filename
                        elif isinstance(v, list) and v and hasattr(v[0], "filename"):
                            args[k] = [file.filename for file in v]
                        else:
                            args[k] = v
                except Exception:  # pylint: disable=broad-exception-caught
                    # 无法解析的请求体不记录参数，审计日志不能中断请求
                    pass

        return args

    async def get_response_body(self, request: Request, response: Response) -> Any:
        """读取响应体用于记录；流式响应读取后会重新填充 `body_iterator`。"""
        # 检查Content-Length
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return {"code": 0, "msg": "Response too large to log", "data": None}

        if hasattr(response, "body"):
            body = response.body
        else:
            body_chunks = []
            async for chunk in response.body_iterator:
                if not isinstance(chunk, bytes):
                    chunk = chunk.encode(response.charset)
                body_chunks.append(chunk)

            response.body_iterator = self._async_iter(body_chunks)
            body = b"".join(body_chunks)

        if any(request.url.path.startswith(path) for path in self.audit_log_paths):
            try:
                data = self.lenient_json(body)
                # 只保留基本信息，去除详细的响应内容
                if isinstance(data, dict):
                    data.pop("response_body", None)
                    if "data" in data and isinstance(data["data"], list):
                        for item in data["data"]:
                            item.pop("response_body", None)
                return data
            except Exception:  # pylint: disable=broad-exception-caught
                # 审计日志列表的响应无法裁剪时不记录响应体
                return None

        return self.lenient_json(body)

    def lenient_json(self, v: Any) -> Any:
        """尽量把字符串或字节解析为 JSON，失败时原样返回。"""
        if isinstance(v, (str, bytes)):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                pass
        return v

    async def _async_iter(self, items: list[bytes]) -> AsyncGenerator[bytes, None]:
        for item in items:
            yield item

    async def get_request_log(self, request: Request, response: Response) -> dict:
        """
        根据request和response对象获取对应的日志记录数据
        """
        data: dict = {"path": request.url.path, "status": response.status_code, "method": request.method}
        # 路由信息
        app: FastAPI = request.app
        for route in app.routes:
            if (
                isinstance(route, APIRoute)
                and route.path_regex.match(request.url.path)
                and request.method in route.methods
            ):
                data["module"] = ",".join(route.tags)
                data["summary"] = route.summary
        # 获取用户信息
        try:
            token = request.headers.get("token")
            user_obj = None
            if token:
                user_obj: User = await AuthControl.is_authed(token)
            data["user_id"] = user_obj.id if user_obj else 0
            data["username"] = user_obj.username if user_obj else ""
        except Exception:  # pylint: disable=broad-exception-caught
            # 鉴权失败的请求同样要记录，用户信息置空
            data["user_id"] = 0
            data["username"] = ""
        return data

    async def before_request(self, request: Request):
        """在请求体被下游消费前保存请求参数。"""
        request_args = await self.get_request_args(request)
        request.state.request_args = request_args

    async def after_request(self, request: Request, response: Response, process_time: int):
        """为需要审计的请求写入一条 `AuditLog`。"""
        if request.method in self.methods:
            for path in self.exclude_paths:
                if re.search(path, request.url.path, re.I) is not None:
                    return
            data: dict = await self.get_request_log(request=request, response=response)
            data["response_time"] = process_time

            data["request_args"] = request.state.request_args
            data["response_body"] = await self.get_response_body(request, response)
            await AuditLog.create(**data)

        return response

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time: datetime = datetime.now()
        await self.before_request(request)
        response = await call_next(request)
        end_time: datetime = datetime.now()
        process_time = int((end_time.timestamp() - start_time.timestamp()) * 1000)
        await self.after_request(request, response, process_time)
        return response

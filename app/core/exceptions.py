"""应用异常类型与 FastAPI 全局异常处理器。"""

from fastapi.exceptions import (
    HTTPException,
    RequestValidationError,
    ResponseValidationError,
)
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from tortoise.exceptions import DoesNotExist, IntegrityError


class SettingNotFound(Exception):
    """无法导入应用配置时抛出。"""


async def does_not_exist_handler(req: Request, exc: DoesNotExist) -> JSONResponse:
    """将 ORM 查询不到对象转换为 404 响应。"""
    content = {
        "code": 404,
        "msg": f"Object has not found, exc: {exc}, query_params: {req.query_params}",
    }
    return JSONResponse(content=content, status_code=404)


async def integrity_handler(_: Request, exc: IntegrityError) -> JSONResponse:
    """将数据库完整性错误转换为 500 响应。"""
    content = {
        "code": 500,
        "msg": f"IntegrityError，{exc}",
    }
    return JSONResponse(content=content, status_code=500)


async def http_exc_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """将 `HTTPException` 转换为统一的 `code`/`msg`/`data` 响应。"""
    content = {"code": exc.status_code, "msg": exc.detail, "data": None}
    return JSONResponse(content=content, status_code=exc.status_code)


async def request_validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """将请求参数校验失败转换为 422 响应。"""
    content = {"code": 422, "msg": f"RequestValidationError, {exc}"}
    return JSONResponse(content=content, status_code=422)


async def response_validation_handler(_: Request, exc: ResponseValidationError) -> JSONResponse:
    """将响应模型校验失败转换为 500 响应。"""
    content = {"code": 500, "msg": f"ResponseValidationError, {exc}"}
    return JSONResponse(content=content, status_code=500)

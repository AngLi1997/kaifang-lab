"""统一的 JSON 响应类型。"""

from typing import Any, Optional

from fastapi.responses import JSONResponse


class Success(JSONResponse):
    """成功响应，响应体为 `code`/`msg`/`data` 以及额外关键字字段。"""

    def __init__(
        self,
        code: int = 200,
        msg: Optional[str] = "OK",
        data: Optional[Any] = None,
        **kwargs,
    ):
        content = {"code": code, "msg": msg, "data": data}
        content.update(kwargs)
        super().__init__(content=content, status_code=code)


class Fail(JSONResponse):
    """失败响应，HTTP 状态码与 `code` 一致。"""

    def __init__(
        self,
        code: int = 400,
        msg: Optional[str] = None,
        data: Optional[Any] = None,
        **kwargs,
    ):
        content = {"code": code, "msg": msg, "data": data}
        content.update(kwargs)
        super().__init__(content=content, status_code=code)


class SuccessExtra(JSONResponse):
    """带分页信息（`total`/`page`/`page_size`）的成功响应。"""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        code: int = 200,
        msg: Optional[str] = None,
        data: Optional[Any] = None,
        total: int = 0,
        page: int = 1,
        page_size: int = 20,
        **kwargs,
    ):
        content = {
            "code": code,
            "msg": msg,
            "data": data,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
        content.update(kwargs)
        super().__init__(content=content, status_code=code)

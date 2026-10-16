"""API 管理相关的请求结构。"""

from pydantic import BaseModel, Field

from app.models.enums import MethodType


class BaseApi(BaseModel):
    """API 记录的公共字段。"""

    path: str = Field(..., description="API路径", example="/api/v1/user/list")
    summary: str = Field("", description="API简介", example="查看用户列表")
    method: MethodType = Field(..., description="API方法", example="GET")
    tags: str = Field(..., description="API标签", example="User")


class ApiCreate(BaseApi):
    """创建 API 记录的请求体。"""


class ApiUpdate(BaseApi):
    """更新 API 记录的请求体。"""

    id: int

"""登录与 JWT 相关的数据结构。"""

from datetime import datetime

from pydantic import BaseModel, Field


class CredentialsSchema(BaseModel):
    """用户名密码登录请求体。"""

    username: str = Field(..., description="用户名称", example="admin")
    password: str = Field(..., description="密码", example="123456")


class JWTOut(BaseModel):
    """登录成功的响应数据。"""

    access_token: str
    username: str


class JWTPayload(BaseModel):
    """访问令牌的载荷。"""

    user_id: int
    username: str
    is_superuser: bool
    exp: datetime

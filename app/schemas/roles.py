"""角色管理相关的数据结构。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BaseRole(BaseModel):
    """角色的完整字段。"""

    id: int
    name: str
    desc: str = ""
    users: Optional[list] = []
    menus: Optional[list] = []
    apis: Optional[list] = []
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class RoleCreate(BaseModel):
    """创建角色的请求体。"""

    name: str = Field(example="管理员")
    desc: str = Field("", example="管理员角色")


class RoleUpdate(BaseModel):
    """更新角色的请求体。"""

    id: int = Field(example=1)
    name: str = Field(example="管理员")
    desc: str = Field("", example="管理员角色")


class RoleUpdateMenusApis(BaseModel):
    """更新角色菜单与 API 权限的请求体。"""

    id: int
    menu_ids: list[int] = []
    api_infos: list[dict] = []

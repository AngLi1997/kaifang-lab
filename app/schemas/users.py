"""用户管理相关的数据结构。"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    """用户的完整字段。"""

    id: int
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    roles: Optional[list] = []


class UserCreate(BaseModel):
    """创建用户的请求体。"""

    email: EmailStr = Field(example="admin@qq.com")
    username: str = Field(example="admin")
    password: str = Field(example="123456")
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role_ids: Optional[List[int]] = []
    dept_id: Optional[int] = Field(0, description="部门ID")

    def create_dict(self):
        """返回显式设置且不含 `role_ids` 的建表字段。"""
        return self.model_dump(exclude_unset=True, exclude={"role_ids"})


class UserUpdate(BaseModel):
    """更新用户的请求体。"""

    id: int
    email: EmailStr
    username: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role_ids: Optional[List[int]] = []
    dept_id: Optional[int] = 0


class UpdatePassword(BaseModel):
    """修改密码的请求体。"""

    old_password: str = Field(description="旧密码")
    new_password: str = Field(description="新密码")

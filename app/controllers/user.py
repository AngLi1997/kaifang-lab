"""用户控制器。"""

from datetime import datetime
from typing import List, Optional

from fastapi.exceptions import HTTPException

from app.core.crud import CRUDBase
from app.models.admin import User
from app.schemas.login import CredentialsSchema
from app.schemas.users import ProfileUpdate, UserCreate, UserUpdate
from app.utils.password import get_password_hash, verify_password

from .role import role_controller


class UserController(CRUDBase[User, UserCreate, UserUpdate]):
    """管理用户、登录认证与角色绑定。"""

    def __init__(self):
        super().__init__(model=User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """按邮箱查找用户，不存在时返回 `None`。"""
        return await self.model.filter(email=email).first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """按账号查找用户，不存在时返回 `None`。"""
        return await self.model.filter(username=username).first()

    async def create_user(self, obj_in: UserCreate) -> User:
        """哈希密码后创建用户。"""
        obj_in.password = get_password_hash(password=obj_in.password)
        obj = await self.create(obj_in)
        return obj

    async def update_last_login(self, id: int) -> None:
        """把用户的最后登录时间更新为当前时间。"""
        user = await self.model.get(id=id)
        user.last_login = datetime.now()
        await user.save()

    async def authenticate(self, credentials: CredentialsSchema) -> Optional["User"]:
        """校验账号、密码和启用状态，失败时抛出 400。"""
        user = await self.model.filter(username=credentials.username).first()
        if not user:
            raise HTTPException(status_code=400, detail="无效的账号")
        verified = verify_password(credentials.password, user.password)
        if not verified:
            raise HTTPException(status_code=400, detail="密码错误!")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="用户已被禁用")
        return user

    async def update_profile(self, user_id: int, obj_in: ProfileUpdate) -> User:
        """更新用户自己的昵称和邮箱；空白昵称存为 `None`。"""
        nickname = (obj_in.nickname or "").strip() or None
        return await self.update(id=user_id, obj_in={"nickname": nickname, "email": obj_in.email})

    async def update_roles(self, user: User, role_ids: List[int]) -> None:
        """用 `role_ids` 替换用户的全部角色。"""
        await user.roles.clear()
        for role_id in role_ids:
            role_obj = await role_controller.get(id=role_id)
            await user.roles.add(role_obj)

    async def reset_password(self, user_id: int):
        """把用户密码重置为默认值；超级管理员不允许重置。"""
        user_obj = await self.get(id=user_id)
        if user_obj.is_superuser:
            raise HTTPException(status_code=403, detail="不允许重置超级管理员密码")
        user_obj.password = get_password_hash(password="123456")
        await user_obj.save()


user_controller = UserController()

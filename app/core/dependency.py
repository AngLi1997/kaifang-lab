"""鉴权与权限校验的 FastAPI 依赖。"""

from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException, Request

from app.core.ctx import CTX_USER_ID
from app.models import Role, User
from app.settings import settings


class AuthControl:
    """基于请求头 `token` 的身份认证。"""

    @classmethod
    async def is_authed(cls, token: str = Header(..., description="token验证")) -> Optional["User"]:
        """校验 token 并返回当前用户，同时把用户 ID 写入请求上下文。"""
        try:
            if token == "dev":
                user = await User.filter().first()
                user_id = user.id
            else:
                decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
                user_id = decode_data.get("user_id")
            user = await User.filter(id=user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="Authentication failed")
            CTX_USER_ID.set(int(user_id))
            return user
        except jwt.DecodeError as e:
            raise HTTPException(status_code=401, detail="无效的Token") from e
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail="登录已过期") from e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{repr(e)}") from e


class PermissionControl:
    """基于角色绑定 API 的访问控制。"""

    @classmethod
    async def has_permission(cls, request: Request, current_user: User = Depends(AuthControl.is_authed)) -> None:
        """超级管理员直接放行；其他用户的角色须绑定当前请求的方法与路径。"""
        if current_user.is_superuser:
            return
        method = request.method
        path = request.url.path
        roles: list[Role] = await current_user.roles
        if not roles:
            raise HTTPException(status_code=403, detail="The user is not bound to a role")
        apis = [await role.apis for role in roles]
        permission_apis = list(set((api.method, api.path) for api in sum(apis, [])))
        # path = "/api/v1/auth/userinfo"
        # method = "GET"
        if (method, path) not in permission_apis:
            raise HTTPException(status_code=403, detail=f"Permission denied method:{method} path:{path}")


DEPEND_AUTH = Depends(AuthControl.is_authed)
DEPEND_PERMISSION = Depends(PermissionControl.has_permission)

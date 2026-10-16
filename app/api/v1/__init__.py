"""v1 版本接口路由。"""

from fastapi import APIRouter

from app.core.dependency import DEPEND_PERMISSION

from .apis import apis_router
from .auditlog import auditlog_router
from .base import base_router
from .depts import depts_router
from .files import files_router
from .menus import menus_router
from .roles import roles_router
from .users import users_router

v1_router = APIRouter()

v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(users_router, prefix="/user", dependencies=[DEPEND_PERMISSION])
v1_router.include_router(roles_router, prefix="/role", dependencies=[DEPEND_PERMISSION])
v1_router.include_router(menus_router, prefix="/menu", dependencies=[DEPEND_PERMISSION])
v1_router.include_router(apis_router, prefix="/api", dependencies=[DEPEND_PERMISSION])
v1_router.include_router(depts_router, prefix="/dept", dependencies=[DEPEND_PERMISSION])
v1_router.include_router(auditlog_router, prefix="/auditlog", dependencies=[DEPEND_PERMISSION])
v1_router.include_router(files_router, prefix="/file", dependencies=[DEPEND_PERMISSION])

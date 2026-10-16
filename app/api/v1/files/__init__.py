"""文件管理路由。"""

from fastapi import APIRouter

from .files import router

files_router = APIRouter()
files_router.include_router(router, tags=["文件模块"])

__all__ = ["files_router"]

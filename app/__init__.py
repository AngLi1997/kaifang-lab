"""KaifangLab FastAPI 应用入口，负责创建并配置全局 `app`。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise

from app.core.exceptions import SettingNotFound
from app.core.init_app import (
    init_data,
    make_middlewares,
    register_exceptions,
    register_routers,
)

try:
    from app.settings.config import settings
except ImportError as exc:
    raise SettingNotFound("Can not import settings") from exc


@asynccontextmanager
async def lifespan(application: FastAPI):
    """启动时初始化数据库与种子数据，关闭时释放数据库连接。"""
    await init_data(application)
    yield
    await Tortoise.close_connections()


def create_app() -> FastAPI:
    """创建 FastAPI 应用并注册中间件、异常处理器和路由。"""
    application = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
        lifespan=lifespan,
    )
    register_exceptions(application)
    register_routers(application, prefix="/api")
    return application


app = create_app()

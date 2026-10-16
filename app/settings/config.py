"""从环境变量与 `.env` 加载的应用配置。"""

import os
import typing

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置项，字段名与环境变量名一致。"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    VERSION: str = "0.1.0"
    APP_TITLE: str = "KaifangLab"
    PROJECT_NAME: str = "KaifangLab"
    APP_DESCRIPTION: str = "KaifangLab provides foundational service capabilities for KaifangHarness agents."

    CORS_ORIGINS: typing.List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: typing.List = ["*"]
    CORS_ALLOW_HEADERS: typing.List = ["*"]

    DEBUG: bool = True

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")
    SECRET_KEY: str = "3488a63e1765035d386f05409663f55c83bfae3b3c61a932744b20ad14244dcf"  # openssl rand -hex 32
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 day

    DB_BACKEND: str = "postgres"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "kaifang"
    POSTGRES_PASSWORD: str = "kaifang"
    POSTGRES_DB: str = "kaifang"

    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    @property
    def TORTOISE_ORM(self) -> dict:  # pylint: disable=invalid-name
        """按 `DB_BACKEND` 生成 Tortoise ORM 与 aerich 使用的配置。"""
        if self.DB_BACKEND == "sqlite":
            connection = {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": f"{self.BASE_DIR}/db.sqlite3"},
            }
        elif self.DB_BACKEND == "postgres":
            connection = {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": self.POSTGRES_HOST,
                    "port": self.POSTGRES_PORT,
                    "user": self.POSTGRES_USER,
                    "password": self.POSTGRES_PASSWORD,
                    "database": self.POSTGRES_DB,
                },
            }
        else:
            raise ValueError(f"Unsupported DB_BACKEND: {self.DB_BACKEND}")

        return {
            "connections": {"default": connection},
            "apps": {
                "models": {
                    "models": ["app.models", "aerich.models"],
                    "default_connection": "default",
                },
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai",
        }


settings = Settings()

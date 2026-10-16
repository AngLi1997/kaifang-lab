"""应用配置；`TORTOISE_ORM` 供 aerich 通过 `app.settings.TORTOISE_ORM` 读取。"""

from .config import settings

TORTOISE_ORM = settings.TORTOISE_ORM

__all__ = ["settings", "TORTOISE_ORM"]

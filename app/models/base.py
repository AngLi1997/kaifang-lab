"""ORM 模型基类与通用字段 mixin。"""

import asyncio
from datetime import datetime

from tortoise import fields, models

from app.settings import settings


class BaseModel(models.Model):
    """带自增主键并支持序列化为字典的抽象模型。"""

    id = fields.BigIntField(pk=True, index=True)

    async def to_dict(self, m2m: bool = False, exclude_fields: list[str] | None = None):
        """把字段序列化为字典，日期按 `settings.DATETIME_FORMAT` 格式化；`m2m` 为真时包含多对多字段。"""
        if exclude_fields is None:
            exclude_fields = []

        d = {}
        for field in self._meta.db_fields:
            if field not in exclude_fields:
                value = getattr(self, field)
                if isinstance(value, datetime):
                    value = value.strftime(settings.DATETIME_FORMAT)
                d[field] = value

        if m2m:
            tasks = [
                self.__fetch_m2m_field(field, exclude_fields)
                for field in self._meta.m2m_fields
                if field not in exclude_fields
            ]
            results = await asyncio.gather(*tasks)
            for field, values in results:
                d[field] = values

        return d

    async def __fetch_m2m_field(self, field, exclude_fields):
        values = await getattr(self, field).all().values()
        formatted_values = []

        for value in values:
            formatted_value = {}
            for k, v in value.items():
                if k not in exclude_fields:
                    if isinstance(v, datetime):
                        formatted_value[k] = v.strftime(settings.DATETIME_FORMAT)
                    else:
                        formatted_value[k] = v
            formatted_values.append(formatted_value)

        return field, formatted_values

    class Meta:
        abstract = True


class UUIDModel:
    """提供唯一 `uuid` 字段的 mixin。"""

    uuid = fields.UUIDField(unique=True, pk=False, index=True)


class TimestampMixin:
    """提供 `created_at`、`updated_at` 字段的 mixin。"""

    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)

"""ORM 与接口共用的枚举类型。"""

from enum import Enum, StrEnum


class EnumBase(Enum):
    """提供成员名称与取值列表的枚举基类。"""

    @classmethod
    def get_member_values(cls):
        """返回全部成员（含别名）的取值列表。"""
        return [item.value for item in cls.__members__.values()]

    @classmethod
    def get_member_names(cls):
        """返回全部规范成员（不含别名）的名称列表。"""
        return [item.name for item in cls]


class MethodType(StrEnum):
    """HTTP 请求方法。"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

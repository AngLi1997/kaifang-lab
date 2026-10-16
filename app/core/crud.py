"""基于 Tortoise ORM 的通用增删改查控制器。"""

from typing import Any, Dict, Generic, List, NewType, Tuple, Type, TypeVar, Union

from pydantic import BaseModel
from tortoise.expressions import Q
from tortoise.models import Model

Total = NewType("Total", int)
ModelT = TypeVar("ModelT", bound=Model)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class CRUDBase(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """针对单个 ORM 模型的通用增删改查操作。"""

    def __init__(self, model: Type[ModelT]):
        self.model = model

    async def get(self, id: int) -> ModelT:
        """按主键获取对象；不存在时抛出 `DoesNotExist`。"""
        return await self.model.get(id=id)

    async def list(
        self, page: int, page_size: int, search: Q = Q(), order: list | None = None
    ) -> Tuple[Total, List[ModelT]]:
        """按条件分页查询，返回总数与当前页对象列表。"""
        query = self.model.filter(search)
        page_query = query.offset((page - 1) * page_size).limit(page_size).order_by(*(order or []))
        return await query.count(), await page_query

    async def create(self, obj_in: CreateSchemaT) -> ModelT:
        """根据 schema 或字典创建并保存对象。"""
        if isinstance(obj_in, Dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump()
        obj = self.model(**obj_dict)
        await obj.save()
        return obj

    async def update(self, id: int, obj_in: Union[UpdateSchemaT, Dict[str, Any]]) -> ModelT:
        """按主键更新对象；schema 仅写入显式设置的字段。"""
        if isinstance(obj_in, Dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump(exclude_unset=True, exclude={"id"})
        obj = await self.get(id=id)
        obj = obj.update_from_dict(obj_dict)
        await obj.save()
        return obj

    async def remove(self, id: int) -> None:
        """按主键删除对象。"""
        obj = await self.get(id=id)
        await obj.delete()

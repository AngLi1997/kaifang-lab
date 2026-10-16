"""部门管理相关的请求结构。"""

from pydantic import BaseModel, Field


class BaseDept(BaseModel):
    """部门的公共字段。"""

    name: str = Field(..., description="部门名称", example="研发中心")
    desc: str = Field("", description="备注", example="研发中心")
    order: int = Field(0, description="排序")
    parent_id: int = Field(0, description="父部门ID")


class DeptCreate(BaseDept):
    """创建部门的请求体。"""


class DeptUpdate(BaseDept):
    """更新部门的请求体。"""

    id: int

    def update_dict(self):
        """返回显式设置且不含 `id` 的待更新字段。"""
        return self.model_dump(exclude_unset=True, exclude={"id"})

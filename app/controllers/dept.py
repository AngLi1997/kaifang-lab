"""部门控制器，维护部门树与闭包表。"""

from tortoise.expressions import Q
from tortoise.transactions import atomic

from app.core.crud import CRUDBase
from app.models.admin import Dept, DeptClosure
from app.schemas.depts import DeptCreate, DeptUpdate


class DeptController(CRUDBase[Dept, DeptCreate, DeptUpdate]):
    """管理部门及其 `DeptClosure` 祖先关系。"""

    def __init__(self):
        super().__init__(model=Dept)

    async def get_dept_tree(self, name):
        """返回未删除部门组成的树，`name` 非空时只保留名称包含它的部门。"""
        q = Q()
        # 获取所有未被软删除的部门
        q &= Q(is_deleted=False)
        if name:
            q &= Q(name__contains=name)
        all_depts = await self.model.filter(q).order_by("order")

        # 辅助函数，用于递归构建部门树
        def build_tree(parent_id):
            return [
                {
                    "id": dept.id,
                    "name": dept.name,
                    "desc": dept.desc,
                    "order": dept.order,
                    "parent_id": dept.parent_id,
                    "children": build_tree(dept.id),  # 递归构建子部门
                }
                for dept in all_depts
                if dept.parent_id == parent_id
            ]

        # 从顶级部门（parent_id=0）开始构建部门树
        dept_tree = build_tree(0)
        return dept_tree

    async def get_dept_info(self):
        """预留接口，当前未实现。"""

    async def update_dept_closure(self, obj: Dept):
        """根据父部门的祖先关系为 `obj` 写入闭包记录。"""
        parent_depts = await DeptClosure.filter(descendant=obj.parent_id)
        for i in parent_depts:
            print(i.ancestor, i.descendant)
        dept_closure_objs: list[DeptClosure] = []
        # 插入父级关系
        for item in parent_depts:
            dept_closure_objs.append(DeptClosure(ancestor=item.ancestor, descendant=obj.id, level=item.level + 1))
        # 插入自身x
        dept_closure_objs.append(DeptClosure(ancestor=obj.id, descendant=obj.id, level=0))
        # 创建关系
        await DeptClosure.bulk_create(dept_closure_objs)

    @atomic()
    async def create_dept(self, obj_in: DeptCreate):
        """校验父部门存在后创建部门并写入闭包记录。"""
        # 创建
        if obj_in.parent_id != 0:
            await self.get(id=obj_in.parent_id)
        new_obj = await self.create(obj_in=obj_in)
        await self.update_dept_closure(new_obj)

    @atomic()
    async def update_dept(self, obj_in: DeptUpdate):
        """更新部门；父部门变化时重建闭包记录。"""
        dept_obj = await self.get(id=obj_in.id)
        # 更新部门关系
        if dept_obj.parent_id != obj_in.parent_id:
            await DeptClosure.filter(ancestor=dept_obj.id).delete()
            await DeptClosure.filter(descendant=dept_obj.id).delete()
            await self.update_dept_closure(dept_obj)
        # 更新部门信息
        dept_obj.update_from_dict(obj_in.model_dump(exclude_unset=True))
        await dept_obj.save()

    @atomic()
    async def delete_dept(self, dept_id: int):
        """软删除部门并移除其作为子代的闭包记录。"""
        # 删除部门
        obj = await self.get(id=dept_id)
        obj.is_deleted = True
        await obj.save()
        # 删除关系
        await DeptClosure.filter(descendant=dept_id).delete()


dept_controller = DeptController()

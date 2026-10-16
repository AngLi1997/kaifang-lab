"""角色控制器。"""

from typing import List

from app.core.crud import CRUDBase
from app.models.admin import Api, Menu, Role
from app.schemas.roles import RoleCreate, RoleUpdate


class RoleController(CRUDBase[Role, RoleCreate, RoleUpdate]):
    """管理角色及其菜单、API 权限。"""

    def __init__(self):
        super().__init__(model=Role)

    async def is_exist(self, name: str) -> bool:
        """判断是否已存在同名角色。"""
        return await self.model.filter(name=name).exists()

    async def update_roles(self, role: Role, menu_ids: List[int], api_infos: List[dict]) -> None:
        """用给定菜单 ID 和 API（`path`、`method`）替换角色的全部权限。"""
        await role.menus.clear()
        for menu_id in menu_ids:
            menu_obj = await Menu.filter(id=menu_id).first()
            await role.menus.add(menu_obj)

        await role.apis.clear()
        for item in api_infos:
            api_obj = await Api.filter(path=item.get("path"), method=item.get("method")).first()
            await role.apis.add(api_obj)


role_controller = RoleController()

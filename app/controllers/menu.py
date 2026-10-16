"""菜单控制器。"""

from typing import Optional

from app.core.crud import CRUDBase
from app.models.admin import Menu
from app.schemas.menus import MenuCreate, MenuUpdate


class MenuController(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    """管理 `Menu` 表。"""

    def __init__(self):
        super().__init__(model=Menu)

    async def get_by_menu_path(self, path: str) -> Optional["Menu"]:
        """按路径查找菜单，不存在时返回 `None`。"""
        return await self.model.filter(path=path).first()


menu_controller = MenuController()

"""API 权限记录的控制器。"""

from collections.abc import Iterable

from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

from app.core.crud import CRUDBase
from app.log import logger
from app.models.admin import Api
from app.schemas.apis import ApiCreate, ApiUpdate


class ApiController(CRUDBase[Api, ApiCreate, ApiUpdate]):
    """管理 `Api` 表，并与应用中需要鉴权的路由保持同步。"""

    def __init__(self):
        super().__init__(model=Api)

    async def refresh_api(self, routes: Iterable[BaseRoute]):
        """按 `routes` 中带依赖的 `APIRoute` 同步 `Api` 表：删除失效记录，新增或更新现有记录。"""
        auth_routes = [route for route in routes if isinstance(route, APIRoute) and len(route.dependencies) > 0]

        # 删除废弃API数据
        all_api_list = [(list(route.methods)[0], route.path_format) for route in auth_routes]
        delete_api = []
        for api in await Api.all():
            if (api.method, api.path) not in all_api_list:
                delete_api.append((api.method, api.path))
        for item in delete_api:
            method, path = item
            logger.debug(f"API Deleted {method} {path}")
            await Api.filter(method=method, path=path).delete()

        for route in auth_routes:
            method = list(route.methods)[0]
            path = route.path_format
            api_data = {"method": method, "path": path, "summary": route.summary, "tags": list(route.tags)[0]}
            api_obj = await Api.filter(method=method, path=path).first()
            if api_obj:
                await api_obj.update_from_dict(api_data).save()
            else:
                logger.debug(f"API Created {method} {path}")
                await Api.create(**api_data)


api_controller = ApiController()

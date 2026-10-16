"""用户昵称：默认超级管理员昵称补齐与个人资料更新。"""

import asyncio

from tortoise import Tortoise

from app.controllers.user import user_controller
from app.core.init_app import SUPERUSER_NICKNAME, init_superuser
from app.models.admin import User
from app.schemas.users import ProfileUpdate


async def _with_db(body):
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["app.models"]})
    await Tortoise.generate_schemas()
    try:
        await body()
    finally:
        await Tortoise.close_connections()


def test_new_superuser_gets_default_nickname():
    async def body():
        await init_superuser()
        admin = await User.get(username="admin")
        assert admin.nickname == SUPERUSER_NICKNAME

    asyncio.run(_with_db(body))


def test_existing_admin_without_nickname_is_backfilled_once():
    async def body():
        await User.create(username="admin", email="admin@admin.com", is_superuser=True)
        await User.create(username="alice", email="alice@example.com")
        await init_superuser()
        assert (await User.get(username="admin")).nickname == SUPERUSER_NICKNAME
        assert (await User.get(username="alice")).nickname is None

        await User.filter(username="admin").update(nickname="老板")
        await init_superuser()
        assert (await User.get(username="admin")).nickname == "老板"

    asyncio.run(_with_db(body))


def test_update_profile_stores_blank_nickname_as_none():
    async def body():
        user = await User.create(username="bob", email="bob@example.com", nickname="Bob")
        updated = await user_controller.update_profile(user.id, ProfileUpdate(nickname="  ", email="b@example.com"))
        assert updated.nickname is None
        assert updated.email == "b@example.com"
        updated = await user_controller.update_profile(user.id, ProfileUpdate(nickname=" 小鲍 ", email="b@example.com"))
        assert updated.nickname == "小鲍"

    asyncio.run(_with_db(body))

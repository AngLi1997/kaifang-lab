"""登录与当前用户信息接口。"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, File, Path, UploadFile

from app.controllers.file import avatar_url, file_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DEPEND_AUTH
from app.models.admin import Api, Menu, Role, User
from app.models.enums import FileCategory
from app.schemas.base import Fail, Success
from app.schemas.login import CredentialsSchema, JWTOut, JWTPayload
from app.schemas.users import ProfileUpdate, UpdatePassword
from app.settings import settings
from app.utils.jwt_utils import create_access_token
from app.utils.password import get_password_hash, verify_password

router = APIRouter()
HIDDEN_MENU_COMPONENTS = {"/system/api", "/top-menu"}


@router.post("/access_token", summary="获取token")
async def login_access_token(credentials: CredentialsSchema):
    """校验账号密码并签发访问令牌。"""
    user: User = await user_controller.authenticate(credentials)
    await user_controller.update_last_login(user.id)
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + access_token_expires

    data = JWTOut(
        access_token=create_access_token(
            data=JWTPayload(
                user_id=user.id,
                username=user.username,
                is_superuser=user.is_superuser,
                exp=expire,
            )
        ),
        username=user.username,
        nickname=user.nickname or user.username,
    )
    return Success(data=data.model_dump())


@router.get("/userinfo", summary="查看用户信息", dependencies=[DEPEND_AUTH])
async def get_userinfo():
    """返回当前用户信息（不含密码）。"""
    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get(id=user_id)
    data = await user_obj.to_dict(exclude_fields=["password"])
    data["avatar"] = avatar_url(user_obj)
    return Success(data=data)


@router.get("/usermenu", summary="查看用户菜单", dependencies=[DEPEND_AUTH])
async def get_user_menu():
    """返回当前用户可见的两级菜单树。"""
    user_id = CTX_USER_ID.get()
    user_obj = await User.filter(id=user_id).first()
    menus: list[Menu] = []
    if user_obj.is_superuser:
        menus = await Menu.all()
    else:
        role_objs: list[Role] = await user_obj.roles
        for role_obj in role_objs:
            menu = await role_obj.menus
            menus.extend(menu)
        menus = list(set(menus))
    menus = [menu for menu in menus if menu.component not in HIDDEN_MENU_COMPONENTS]
    parent_menus: list[Menu] = []
    for menu in menus:
        if menu.parent_id == 0:
            parent_menus.append(menu)
    res = []
    for parent_menu in parent_menus:
        parent_menu_dict = await parent_menu.to_dict()
        parent_menu_dict["children"] = []
        for menu in menus:
            if menu.parent_id == parent_menu.id:
                parent_menu_dict["children"].append(await menu.to_dict())
        res.append(parent_menu_dict)
    return Success(data=res)


@router.get("/userapi", summary="查看用户API", dependencies=[DEPEND_AUTH])
async def get_user_api():
    """返回当前用户可访问的 API，格式为小写方法加路径。"""
    user_id = CTX_USER_ID.get()
    user_obj = await User.filter(id=user_id).first()
    if user_obj.is_superuser:
        api_objs: list[Api] = await Api.all()
        apis = [api.method.lower() + api.path for api in api_objs]
        return Success(data=apis)
    role_objs: list[Role] = await user_obj.roles
    apis = []
    for role_obj in role_objs:
        api_objs: list[Api] = await role_obj.apis
        apis.extend([api.method.lower() + api.path for api in api_objs])
    apis = list(set(apis))
    return Success(data=apis)


@router.post("/update_profile", summary="修改个人资料", dependencies=[DEPEND_AUTH])
async def update_user_profile(req_in: ProfileUpdate):
    """修改当前用户的昵称和邮箱；邮箱已被其他用户使用时返回失败。"""
    user_id = CTX_USER_ID.get()
    owner = await user_controller.get_by_email(req_in.email)
    if owner and owner.id != user_id:
        return Fail(msg="该邮箱已被其他用户使用")
    user = await user_controller.update_profile(user_id, req_in)
    data = await user.to_dict(exclude_fields=["password"])
    data["avatar"] = avatar_url(user)
    return Success(data=data, msg="修改成功")


@router.post("/update_password", summary="修改密码", dependencies=[DEPEND_AUTH])
async def update_user_password(req_in: UpdatePassword):
    """校验旧密码后修改当前用户密码。"""
    user_id = CTX_USER_ID.get()
    user = await user_controller.get(user_id)
    verified = verify_password(req_in.old_password, user.password)
    if not verified:
        return Fail(msg="旧密码验证错误！")
    user.password = get_password_hash(req_in.new_password)
    await user.save()
    return Success(msg="修改成功")


@router.post("/avatar", summary="上传头像", dependencies=[DEPEND_AUTH])
async def upload_avatar(file: UploadFile = File(..., description="头像图片")):
    """上传当前用户的头像并替换旧头像，返回新的头像地址。"""
    user = await user_controller.get(id=CTX_USER_ID.get())
    await file_controller.replace_avatar(user, file)
    return Success(data={"avatar": avatar_url(user)})


@router.get("/avatar/{file_id}", summary="查看头像")
async def get_avatar(file_id: int = Path(..., description="头像文件ID")):
    """返回头像图片；供 `<img>` 直接引用，因此不要求 token，且只提供头像分类的文件。"""
    file_obj = await file_controller.model.get(id=file_id, category=FileCategory.AVATAR)
    return await file_controller.stream(file_obj, inline=True, cache_control="public, max-age=86400")

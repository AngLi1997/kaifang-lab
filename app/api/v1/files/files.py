"""文件上传、查询、下载与删除接口。"""

from fastapi import APIRouter, File, Query, UploadFile
from tortoise.expressions import Q

from app.controllers.file import file_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.models.enums import FileCategory
from app.schemas.base import Success, SuccessExtra
from app.settings import settings

router = APIRouter()


async def _current_user():
    return await user_controller.get(id=CTX_USER_ID.get())


@router.post("/upload", summary="上传文件")
async def upload_file(file: UploadFile = File(..., description="待上传文件")):
    """上传附件到默认桶，返回文件元数据。"""
    user = await _current_user()
    file_obj = await file_controller.upload(
        file,
        category=FileCategory.ATTACHMENT,
        owner_id=user.id,
        max_size_mb=settings.FILE_MAX_SIZE_MB,
    )
    return Success(data=await file_obj.to_dict())


@router.get("/list", summary="查看文件列表")
async def list_files(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    original_name: str = Query("", description="原始文件名，用于搜索"),
    category: FileCategory = Query(None, description="文件分类"),
):
    """分页查询文件；超级管理员可查看全部文件，其他用户只能查看自己上传的文件。"""
    user = await _current_user()
    q = Q()
    if not user.is_superuser:
        q &= Q(owner_id=user.id)
    if original_name:
        q &= Q(original_name__icontains=original_name)
    if category:
        q &= Q(category=category)
    total, file_objs = await file_controller.list(page=page, page_size=page_size, search=q, order=["-id"])
    data = [await obj.to_dict() for obj in file_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="查看文件信息")
async def get_file(file_id: int = Query(..., description="文件ID")):
    """返回文件元数据。"""
    file_obj = await file_controller.get_accessible(file_id, await _current_user())
    return Success(data=await file_obj.to_dict())


@router.get("/download", summary="下载文件")
async def download_file(
    file_id: int = Query(..., description="文件ID"),
    inline: bool = Query(False, description="为真时浏览器内联打开，否则作为附件下载"),
):
    """经后端从 MinIO 流式读取文件内容。"""
    file_obj = await file_controller.get_accessible(file_id, await _current_user())
    return await file_controller.stream(file_obj, inline=inline)


@router.get("/presigned_url", summary="获取文件临时下载地址")
async def get_presigned_url(
    file_id: int = Query(..., description="文件ID"),
    expires: int = Query(3600, description="有效期(秒)，最长 7 天"),
):
    """生成直连 MinIO 的临时下载 URL。"""
    file_obj = await file_controller.get_accessible(file_id, await _current_user())
    url = await file_controller.presigned_url(file_obj, expires)
    return Success(data={"url": url, "expires": expires})


@router.delete("/delete", summary="删除文件")
async def delete_file(file_id: int = Query(..., description="文件ID")):
    """删除 MinIO 对象及其元数据。"""
    file_obj = await file_controller.get_accessible(file_id, await _current_user())
    await file_controller.delete_file(file_obj)
    return Success(msg="Deleted Successfully")

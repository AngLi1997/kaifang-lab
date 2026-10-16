"""文件控制器：上传到 MinIO、元数据维护、访问控制与下载响应。"""

import mimetypes
import os
import re
import uuid
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import quote

from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from minio.error import S3Error
from pydantic import BaseModel

from app.core.crud import CRUDBase
from app.core.storage import PRESIGNED_MAX_EXPIRES, storage
from app.log import logger
from app.models.admin import User
from app.models.enums import FileCategory
from app.models.file import File
from app.settings import settings

DEFAULT_AVATAR_URL = "/favicon.png"
AVATAR_URL_PREFIX = "/api/v1/base/avatar"
_EXTENSION_PATTERN = re.compile(r"^\.[a-z0-9]{1,10}$")
_MISSING_OBJECT_CODES = {"NoSuchKey", "NoSuchObject"}


def build_object_key(category: FileCategory, owner_id: int, filename: str, now: Optional[datetime] = None) -> str:
    """生成对象键 `{category}/{owner_id}/{YYYY}/{MM}/{DD}/{uuid}{ext}`。

    原始文件名只贡献扩展名（小写，仅字母数字且不超过 10 位，否则省略），因此对象键不含用户可控的路径片段。
    """
    now = now or datetime.now()
    ext = os.path.splitext(filename or "")[1].lower()
    if not _EXTENSION_PATTERN.match(ext):
        ext = ""
    return f"{category.value}/{owner_id}/{now:%Y/%m/%d}/{uuid.uuid4().hex}{ext}"


def content_disposition(filename: str, inline: bool) -> str:
    """按 RFC 6266/5987 生成 `Content-Disposition`，同时提供 ASCII 回退名和 UTF-8 文件名。"""
    disposition = "inline" if inline else "attachment"
    ascii_name = filename.encode("ascii", "ignore").decode().replace('"', "").replace("\\", "") or "download"
    return f"{disposition}; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename, safe='')}"


def avatar_url(user: User) -> str:
    """返回用户头像的访问路径；未设置头像时返回默认图标。"""
    if user.avatar_id:
        return f"{AVATAR_URL_PREFIX}/{user.avatar_id}"
    return DEFAULT_AVATAR_URL


def _resolve_content_type(upload: UploadFile) -> str:
    content_type = (upload.content_type or "").split(";")[0].strip().lower()
    if not content_type or content_type == "application/octet-stream":
        content_type = mimetypes.guess_type(upload.filename or "")[0] or "application/octet-stream"
    return content_type


def _measure(upload: UploadFile) -> int:
    upload.file.seek(0, os.SEEK_END)
    size = upload.file.tell()
    upload.file.seek(0)
    return size


class _NoSchema(BaseModel):
    pass


class FileController(CRUDBase[File, _NoSchema, _NoSchema]):
    """管理 `File` 元数据及其在 MinIO 中的对象。"""

    def __init__(self):
        super().__init__(model=File)

    async def upload(
        self,
        upload: UploadFile,
        category: FileCategory,
        owner_id: int,
        max_size_mb: int,
        allowed_types: Optional[list[str]] = None,
    ) -> File:
        """校验大小与类型后上传到默认桶并写入元数据。

        超过 `max_size_mb` 返回 413，类型不在 `allowed_types` 中返回 415，空文件返回 400。
        元数据写入失败时删除已上传的对象后重新抛出异常。
        """
        size = _measure(upload)
        if size == 0:
            raise HTTPException(status_code=400, detail="文件为空")
        if size > max_size_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"文件大小超过限制 {max_size_mb}MB")
        content_type = _resolve_content_type(upload)
        if allowed_types is not None and content_type not in allowed_types:
            raise HTTPException(status_code=415, detail=f"不支持的文件类型 {content_type}")

        original_name = os.path.basename(upload.filename or "") or "unnamed"
        object_key = build_object_key(category, owner_id, original_name)
        etag = await storage.put_object(object_key, upload.file, size, content_type)
        try:
            return await self.model.create(
                bucket=storage.bucket,
                object_key=object_key,
                original_name=original_name[:255],
                content_type=content_type,
                size=size,
                etag=etag,
                category=category,
                owner_id=owner_id,
            )
        except Exception:
            await storage.remove_object(object_key)
            raise

    async def delete_file(self, file: File) -> None:
        """先删除 MinIO 对象再删除元数据；对象删除失败时保留元数据，便于重试。"""
        await storage.remove_object(file.object_key)
        await file.delete()

    async def get_accessible(self, file_id: int, user: User) -> File:
        """返回 `user` 可访问的文件：超级管理员可访问全部文件，其他用户只能访问自己上传的文件。"""
        file = await self.get(id=file_id)
        if not user.is_superuser and file.owner_id != user.id:
            raise HTTPException(status_code=403, detail="无权访问该文件")
        return file

    async def stream(self, file: File, inline: bool, cache_control: str = "private, no-cache") -> StreamingResponse:
        """以流式响应返回文件内容；对象已不在 MinIO 中时返回 404。"""
        try:
            body = await storage.open_stream(file.object_key)
        except S3Error as exc:
            if exc.code in _MISSING_OBJECT_CODES:
                raise HTTPException(status_code=404, detail="文件内容不存在") from exc
            raise
        headers = {
            "Content-Length": str(file.size),
            "Content-Disposition": content_disposition(file.original_name, inline),
            "Cache-Control": cache_control,
            "X-Content-Type-Options": "nosniff",
        }
        return StreamingResponse(body, media_type=file.content_type, headers=headers)

    async def presigned_url(self, file: File, expires_seconds: int) -> str:
        """生成以附件方式下载的临时 URL，有效期不超过 7 天。"""
        if expires_seconds <= 0 or timedelta(seconds=expires_seconds) > PRESIGNED_MAX_EXPIRES:
            raise HTTPException(status_code=400, detail="有效期须在 1 秒到 7 天之间")
        response_headers = {"response-content-disposition": content_disposition(file.original_name, inline=False)}
        return await storage.presigned_get_url(file.object_key, timedelta(seconds=expires_seconds), response_headers)

    async def replace_avatar(self, user: User, upload: UploadFile) -> File:
        """上传新头像并绑定到 `user`；旧头像在绑定成功后删除，删除失败只记录警告。"""
        new_file = await self.upload(
            upload,
            category=FileCategory.AVATAR,
            owner_id=user.id,
            max_size_mb=settings.AVATAR_MAX_SIZE_MB,
            allowed_types=settings.AVATAR_ALLOWED_TYPES,
        )
        old_avatar_id = user.avatar_id
        user.avatar_id = new_file.id
        await user.save(update_fields=["avatar_id"])
        if old_avatar_id:
            old_file = await self.model.filter(id=old_avatar_id).first()
            if old_file:
                try:
                    await self.delete_file(old_file)
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    # 新头像已生效，旧对象残留不影响用户，只记录以便人工清理
                    logger.warning(f"Failed to delete old avatar file {old_avatar_id}: {exc!r}")
        return new_file


file_controller = FileController()

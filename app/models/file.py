"""对象存储文件的 ORM 模型。"""

from tortoise import fields

from .base import BaseModel, TimestampMixin
from .enums import FileCategory


class File(BaseModel, TimestampMixin):
    """保存在 MinIO 中的文件元数据；文件内容只存在于 `bucket`/`object_key` 指向的对象。"""

    bucket = fields.CharField(max_length=63, description="存储桶")
    object_key = fields.CharField(max_length=512, unique=True, description="对象键")
    original_name = fields.CharField(max_length=255, description="原始文件名", index=True)
    content_type = fields.CharField(max_length=128, description="MIME 类型")
    size = fields.BigIntField(description="文件大小(字节)")
    etag = fields.CharField(max_length=64, null=True, description="对象ETag")
    category = fields.CharEnumField(FileCategory, description="文件分类", index=True)
    owner_id = fields.BigIntField(description="上传用户ID", index=True)

    class Meta:
        table = "file"

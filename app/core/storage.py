"""MinIO 对象存储客户端：桶初始化、对象读写与预签名 URL。

MinIO SDK 是同步阻塞 API，异步方法通过 `run_in_threadpool` 调用，避免阻塞事件循环。
"""

from collections.abc import Iterator
from datetime import timedelta
from typing import BinaryIO

from minio import Minio
from starlette.concurrency import run_in_threadpool

from app.settings import settings

# S3 协议规定预签名 URL 的最长有效期为 7 天。
PRESIGNED_MAX_EXPIRES = timedelta(days=7)
STREAM_CHUNK_SIZE = 64 * 1024


class MinioStorage:
    """封装单个默认桶的 MinIO 访问；客户端在首次使用时按 `settings` 创建。"""

    def __init__(self, bucket: str):
        self.bucket = bucket
        self._client: Minio | None = None

    @property
    def client(self) -> Minio:
        """返回懒加载的 MinIO 客户端。"""
        if self._client is None:
            self._client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        return self._client

    async def ensure_bucket(self) -> None:
        """默认桶不存在时创建；MinIO 不可达或凭据错误时抛出异常，使应用启动失败。"""

        def _ensure() -> None:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)

        await run_in_threadpool(_ensure)

    async def put_object(self, object_key: str, data: BinaryIO, length: int, content_type: str) -> str:
        """从 `data` 当前位置上传 `length` 字节到 `object_key`，返回对象 ETag。"""
        result = await run_in_threadpool(
            self.client.put_object,
            self.bucket,
            object_key,
            data,
            length,
            content_type=content_type,
        )
        return result.etag

    async def remove_object(self, object_key: str) -> None:
        """删除对象；对象不存在时 MinIO 同样返回成功。"""
        await run_in_threadpool(self.client.remove_object, self.bucket, object_key)

    async def open_stream(self, object_key: str) -> Iterator[bytes]:
        """打开对象并返回按块读取的同步迭代器；迭代结束或被关闭时释放 HTTP 连接。"""
        response = await run_in_threadpool(self.client.get_object, self.bucket, object_key)

        def _iterate() -> Iterator[bytes]:
            try:
                yield from response.stream(STREAM_CHUNK_SIZE)
            finally:
                response.close()
                response.release_conn()

        return _iterate()

    async def presigned_get_url(self, object_key: str, expires: timedelta, response_headers: dict) -> str:
        """生成 `object_key` 的临时下载 URL；URL 主机为 `MINIO_ENDPOINT`，调用方必须能直接访问该地址。"""
        return await run_in_threadpool(
            self.client.presigned_get_object,
            self.bucket,
            object_key,
            expires=expires,
            response_headers=response_headers,
        )


storage = MinioStorage(bucket=settings.MINIO_DEFAULT_BUCKET)

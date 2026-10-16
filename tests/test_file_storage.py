"""文件存储的对象键规则、下载响应头与上传校验。"""

import asyncio
import io
import re
from datetime import datetime

import pytest
from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from starlette.datastructures import Headers

from app.controllers.file import build_object_key, content_disposition, file_controller
from app.models.enums import FileCategory

KEY_PATTERN = re.compile(r"^attachment/7/2026/03/05/[0-9a-f]{32}(?P<ext>\.[a-z0-9]+)?$")


def _upload(data: bytes, filename: str, content_type: str) -> UploadFile:
    return UploadFile(io.BytesIO(data), filename=filename, headers=Headers({"content-type": content_type}))


def test_object_key_layout():
    key = build_object_key(FileCategory.ATTACHMENT, 7, "Report.PDF", now=datetime(2026, 3, 5))
    match = KEY_PATTERN.match(key)
    assert match and match.group("ext") == ".pdf"


@pytest.mark.parametrize(
    "filename", ["../../etc/passwd", "noext", "a.tar.gz/../x", "a.<script>", "a.verylongextension"]
)
def test_object_key_ignores_unsafe_names(filename):
    key = build_object_key(FileCategory.ATTACHMENT, 7, filename, now=datetime(2026, 3, 5))
    assert KEY_PATTERN.match(key)
    assert ".." not in key


def test_object_keys_are_unique():
    keys = {build_object_key(FileCategory.AVATAR, 1, "a.png") for _ in range(100)}
    assert len(keys) == 100


def test_content_disposition_encodes_utf8_name():
    value = content_disposition('报告"v1.pdf', inline=False)
    assert value.startswith("attachment; ")
    assert 'filename="v1.pdf"' in value
    assert "filename*=UTF-8''%E6%8A%A5%E5%91%8A%22v1.pdf" in value


def test_content_disposition_inline():
    assert content_disposition("a.png", inline=True).startswith("inline; ")


@pytest.mark.parametrize(
    ("data", "content_type", "allowed", "status"),
    [
        (b"", "text/plain", None, 400),
        (b"x" * (1024 * 1024 + 1), "text/plain", None, 413),
        (b"<svg/>", "image/svg+xml", ["image/png"], 415),
    ],
)
def test_upload_rejects_before_storage(data, content_type, allowed, status):
    upload = _upload(data, "f", content_type)
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            file_controller.upload(upload, FileCategory.ATTACHMENT, owner_id=1, max_size_mb=1, allowed_types=allowed)
        )
    assert exc_info.value.status_code == status

# 文件存储（MinIO）

KaifangLab 使用 MinIO 作为默认文件存储。文件内容保存在 MinIO 的默认桶中，文件元数据（原始文件名、类型、大小、上传人、对象键等）保存在数据库 `file` 表中。用户头像、附件等所有上传文件都走这一套方案。

## 组成

| 部分 | 位置 | 职责 |
| --- | --- | --- |
| MinIO 服务 | `compose.yaml` 中的 `minio` 服务 | 对象存储，API 端口 `9000`，控制台端口 `9001` |
| 存储客户端 | `app/core/storage.py` | 连接 MinIO、启动时创建默认桶、上传/读取/删除对象、生成预签名 URL |
| 文件模型 | `app/models/file.py`（`file` 表） | 文件元数据；`user.avatar_id` 指向头像文件 |
| 文件控制器 | `app/controllers/file.py` | 大小与类型校验、对象键生成、权限检查、流式下载 |
| 接口 | `app/api/v1/files/`、`app/api/v1/base/base.py` | 通用文件接口与头像接口 |

## 启动 MinIO

```sh
cp .env.example .env              # 首次使用
docker compose up -d postgres redis minio
# 或者
make services-up
```

`compose.yaml` 使用 `minio/minio:RELEASE.2025-04-22T22-12-26Z` 镜像，数据持久化在 Docker volume `minio-data` 中。MinIO 的 root 账号读取 `.env` 中的 `MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY`（未设置时为 `miniokaifang`/`miniokaifang`），因此后端与 MinIO 天然使用同一组凭据。MinIO 要求密码至少 8 位。

- API 地址：`http://<主机>:9000`
- 控制台：`http://<主机>:9001`，使用上述账号登录，可浏览桶和对象

后端启动时会检查 `MINIO_DEFAULT_BUCKET` 是否存在，不存在则自动创建，无需手动建桶。MinIO 不可达或凭据错误时后端会在启动阶段报错退出，请先确认 MinIO 已启动且 `.env` 配置正确。

## 配置项

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MINIO_ENDPOINT` | `127.0.0.1:9000` | MinIO API 地址，格式为 `host:port`，不带协议 |
| `MINIO_ACCESS_KEY` | `miniokaifang` | 访问密钥，同时作为 compose 中 MinIO 的 root 用户名 |
| `MINIO_SECRET_KEY` | `miniokaifang` | 私有密钥，同时作为 compose 中 MinIO 的 root 密码 |
| `MINIO_SECURE` | `false` | 是否通过 HTTPS 访问 MinIO：`true`/`false` |
| `MINIO_DEFAULT_BUCKET` | `kaifang-lab` | 默认桶名，须符合 S3 桶命名规则（3–63 位小写字母、数字、`-`、`.`） |
| `FILE_MAX_SIZE_MB` | `100` | 通用附件上传大小上限（MB） |
| `AVATAR_MAX_SIZE_MB` | `10` | 头像上传大小上限（MB） |
| `AVATAR_ALLOWED_TYPES` | `["image/png","image/jpeg","image/webp","image/gif"]` | 头像允许的 MIME 类型，环境变量中使用 JSON 数组 |

生产环境请为 MinIO 使用独立的强口令，不要沿用示例值；也可以在 MinIO 中为后端单独创建一个仅能访问默认桶的访问密钥，再填入 `MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY`。

## 路径定义

### 存储桶

所有文件存放在同一个桶 `MINIO_DEFAULT_BUCKET` 中。桶保持私有（不配置匿名访问策略），浏览器和调用方不直接访问 MinIO，而是经后端接口或预签名 URL 读取。

### 对象键

对象键（object key，即文件在桶内的路径）由后端统一生成：

```text
{category}/{owner_id}/{YYYY}/{MM}/{DD}/{uuid}{ext}
```

| 片段 | 含义 | 示例 |
| --- | --- | --- |
| `category` | 文件分类，见下表 | `avatar` |
| `owner_id` | 上传用户 ID | `1` |
| `YYYY/MM/DD` | 上传日期（服务器时区） | `2026/10/16` |
| `uuid` | 32 位十六进制随机 ID，保证对象键唯一 | `4148460d0e414759874c9aba5470981a` |
| `ext` | 原始文件名的扩展名，转为小写；只保留 1–10 位字母数字，否则省略 | `.png` |

示例：

```text
avatar/1/2026/10/16/4148460d0e414759874c9aba5470981a.png
attachment/3/2026/10/16/930f936ef3f140ed83a59b2e212f6294.pdf
```

原始文件名只用于提取扩展名，完整的原始文件名保存在 `file.original_name` 中，下载时通过 `Content-Disposition` 还原。因此对象键中不会出现用户可控的路径片段（如 `../`），同名文件也不会互相覆盖。

### 文件分类

| `category` | 用途 | 上传接口 | 大小上限 | 类型限制 |
| --- | --- | --- | --- | --- |
| `avatar` | 用户头像 | `POST /api/v1/base/avatar` | `AVATAR_MAX_SIZE_MB` | `AVATAR_ALLOWED_TYPES` |
| `attachment` | 通用附件 | `POST /api/v1/file/upload` | `FILE_MAX_SIZE_MB` | 不限 |

新增分类时，在 `app/models/enums.py` 的 `FileCategory` 中添加枚举值，并在对应业务接口中调用 `file_controller.upload(...)` 传入该分类及其大小、类型限制。

### 元数据表 `file`

| 字段 | 说明 |
| --- | --- |
| `id` | 文件 ID，接口中以 `file_id` 引用 |
| `bucket` | 存储桶 |
| `object_key` | 对象键（唯一） |
| `original_name` | 原始文件名（去除目录部分） |
| `content_type` | MIME 类型；客户端未提供或为 `application/octet-stream` 时按扩展名推断 |
| `size` | 文件大小（字节） |
| `etag` | MinIO 返回的 ETag |
| `category` | 文件分类 |
| `owner_id` | 上传用户 ID |
| `created_at` / `updated_at` | 创建、更新时间 |

数据库结构由启动时的 aerich 自动迁移生成，`file` 表和 `user.avatar_id` 字段会在升级后首次启动时自动创建。

## 接口说明

所有接口前缀为 `/api/v1`，鉴权方式与其他接口相同：请求头 `token: <access_token>`。响应格式为 `{"code": 200, "msg": ..., "data": ...}`（下载接口除外，直接返回文件内容）。

### 上传文件

`POST /api/v1/file/upload`，`multipart/form-data`，表单字段 `file`。

```sh
curl -X POST http://localhost:9999/api/v1/file/upload \
  -H "token: $TOKEN" \
  -F "file=@./report.pdf"
```

返回文件元数据：

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 3,
    "bucket": "kaifang-lab",
    "object_key": "attachment/1/2026/10/16/4148460d0e414759874c9aba5470981a.pdf",
    "original_name": "report.pdf",
    "content_type": "application/pdf",
    "size": 3145728,
    "etag": "f1c9645dbc14efddc7d8a322685f26eb",
    "category": "attachment",
    "owner_id": 1,
    "created_at": "2026-10-16 10:00:00",
    "updated_at": "2026-10-16 10:00:00"
  }
}
```

业务表只需保存返回的 `id`（例如 `attachment_id`），不要保存 MinIO 地址。

### 查询、下载与删除

| 接口 | 说明 |
| --- | --- |
| `GET /api/v1/file/list?page=1&page_size=10&original_name=&category=` | 分页查询文件，按 ID 倒序 |
| `GET /api/v1/file/get?file_id=3` | 查看文件元数据 |
| `GET /api/v1/file/download?file_id=3&inline=false` | 经后端流式下载；`inline=true` 时浏览器内联打开 |
| `GET /api/v1/file/presigned_url?file_id=3&expires=3600` | 生成直连 MinIO 的临时下载 URL，有效期 1 秒到 7 天 |
| `DELETE /api/v1/file/delete?file_id=3` | 删除 MinIO 对象及元数据 |

```sh
curl -H "token: $TOKEN" -OJ "http://localhost:9999/api/v1/file/download?file_id=3"
```

下载响应带有 `Content-Disposition`（含 UTF-8 文件名）、`Content-Length` 和 `X-Content-Type-Options: nosniff`。

预签名 URL 的主机就是 `MINIO_ENDPOINT`，签名与该主机绑定，只有能直接访问该地址的调用方（例如同一内网中的 KaifangHarness 智能体）才能使用；浏览器端下载优先使用 `/file/download`。

### 头像

| 接口 | 鉴权 | 说明 |
| --- | --- | --- |
| `POST /api/v1/base/avatar` | 登录即可 | 上传当前用户头像，表单字段 `file`；成功后替换并删除旧头像 |
| `GET /api/v1/base/avatar/{file_id}` | 无需 token | 返回头像图片，供 `<img>` 直接引用；只提供 `avatar` 分类的文件 |

```sh
curl -X POST http://localhost:9999/api/v1/base/avatar \
  -H "token: $TOKEN" \
  -F "file=@./me.png"
# {"code":200,"msg":"OK","data":{"avatar":"/api/v1/base/avatar/1"}}
```

`GET /api/v1/base/userinfo` 返回的 `avatar` 字段即头像地址；未设置头像时为 `/favicon.png`。管理端「个人中心 → 修改信息」页面提供头像上传按钮。

### 错误码

| 状态码 | 场景 |
| --- | --- |
| `400` | 空文件；预签名有效期超出范围 |
| `403` | 非超级管理员访问他人上传的文件 |
| `404` | 文件记录不存在，或对象已不在 MinIO 中 |
| `413` | 超过大小上限 |
| `415` | 头像类型不在 `AVATAR_ALLOWED_TYPES` 中 |

## 权限

- `/api/v1/file/*` 接口受角色 API 权限控制（标签「文件模块」）。超级管理员可访问全部文件；其他用户即使拥有接口权限，也只能查看、下载和删除自己上传的文件。
- 头像上传和读取接口不走角色 API 权限，任何已登录用户都可以设置自己的头像。
- 首次初始化角色时，「普通用户」只获得 GET 接口，因此默认可以查询和下载自己的文件；上传和删除附件需要管理员在「角色管理」中授权 `POST /api/v1/file/upload`、`DELETE /api/v1/file/delete`。
- 已有数据库的 `api` 表不会自动加入新接口，升级后请由超级管理员调用 `POST /api/v1/api/refresh` 刷新接口列表，再为角色授权。
- 头像读取接口不要求登录，只返回 `avatar` 分类文件，不能借此读取附件。文件 ID 是自增整数，可被枚举，因此头像应视为公开信息。

## 在业务代码中使用

```python
from app.controllers.file import file_controller
from app.models.enums import FileCategory
from app.settings import settings

file_obj = await file_controller.upload(
    upload,                       # fastapi.UploadFile
    category=FileCategory.ATTACHMENT,
    owner_id=user.id,
    max_size_mb=settings.FILE_MAX_SIZE_MB,
    allowed_types=None,           # 或允许的 MIME 类型列表
)
response = await file_controller.stream(file_obj, inline=False)
await file_controller.delete_file(file_obj)
```

`upload` 在元数据写入失败时会删除已上传的对象；`delete_file` 先删除对象再删除元数据，对象删除失败时保留记录以便重试。

## 部署注意事项

- `deploy/web.conf` 为 `/api/` 设置了 `client_max_body_size 100m`（Nginx 默认仅 1MB）。调整 `FILE_MAX_SIZE_MB` 时需同步修改。
- 应用容器需要能访问 `MINIO_ENDPOINT`；容器内的 `127.0.0.1` 指向容器自身，部署时请填写 MinIO 的实际地址。
- 审计日志不记录 `multipart/form-data` 请求体和非 JSON 响应（如文件下载），上传的文件信息以 `file` 表为准。
- 备份时需要同时备份数据库与 MinIO 数据（`minio-data` volume 或对应的数据目录）。

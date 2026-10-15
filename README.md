# KaifangLab

**KaifangWork 智能体服务端能力平台**

KaifangLab 为 KaifangWork（自研智能体）提供统一的服务端管理与基础能力。当前范围包括账号认证、角色与接口权限、组织架构、菜单资源和审计日志，作为智能体体系的服务端基础平台。

## 交付范围

| 能力 | 说明 |
| --- | --- |
| 身份认证 | 用户登录、JWT 令牌与账号资料管理 |
| 访问控制 | 基于角色的菜单、接口授权与动态导航 |
| 组织管理 | 部门和用户信息维护 |
| 审计留痕 | 记录管理端关键请求，支持查询与追溯 |
| 服务管理 | 维护菜单资源及 API 权限目录 |

后端提供 REST API，管理端用于维护平台配置与权限。智能体的模型推理和任务编排由 KaifangWork 负责，不属于本服务当前交付范围。

## 技术组成

- 后端：Python 3.12、FastAPI、Tortoise ORM
- 管理端：Vue 3、Vite、Naive UI
- 数据：PostgreSQL（默认）或 SQLite
- 本地依赖：Docker Compose 提供 PostgreSQL 与 Redis 服务

## 本地运行

### 后端

安装 Docker 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)，然后在仓库根目录执行：

```powershell
Copy-Item .env.example .env
```

macOS/Linux 使用 `cp .env.example .env`。随后启动数据库并运行服务：

```sh
docker compose up -d postgres redis
uv sync
uv run python run.py
```

服务默认监听 `http://localhost:9999`，接口文档位于 `http://localhost:9999/docs`。PostgreSQL 连接参数见 `.env.example`；将 `DB_BACKEND` 设为 `sqlite` 可使用本地 SQLite。

### 管理端

需要 Node.js 18.8 或更高版本，并安装 pnpm：

```sh
cd web
pnpm install
pnpm dev
```

## 首次登录

首次启动会创建初始管理员账号 `admin`，初始口令为 `123456`。请仅在本地开发环境使用该口令；部署到共享或生产环境前，应先配置并更换为独立的强口令。

## 部署交付

仓库提供 Dockerfile，可从仓库根目录构建应用镜像：

```sh
docker build -t kaifanglab:0.1.0 .
```

部署时配置 PostgreSQL 地址、数据库凭据、JWT 密钥、调试模式和允许的跨域来源。生产环境应使用独立密钥与数据库账号，并将 `DEBUG` 设为 `false`、将 `CORS_ORIGINS` 限定为实际管理端域名。

## 仓库结构

```text
app/          FastAPI 接口、业务逻辑、数据模型与配置
migrations/   数据库迁移文件（运行时生成）
deploy/       Web 服务与容器入口配置
web/          Vue 管理端
```

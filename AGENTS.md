# Repository Guidelines（仓库指南）

## 项目结构

仓库由 FastAPI 后端和 Vue 3 前端组成。后端代码位于 `app/`：`api/v1/` 按功能组织接口，`controllers/` 存放业务逻辑，`models/` 定义 ORM 模型，`schemas/` 存放 Pydantic 数据结构，`settings/` 管理配置。数据库迁移文件位于 `migrations/`。前端代码位于 `web/src/`：页面在 `views/`，通用组件在 `components/`，路由和守卫在 `router/`，状态管理在 `store/`，源码静态资源在 `assets/`。需要原样对外提供的资源放在 `web/public/`。

## 开发、构建与检查命令

- `docker compose up -d postgres redis minio`：启动本地数据库与 MinIO 文件存储服务；文件存储方案见 `docs/file-storage.md`。
- `uv sync`：安装后端依赖；`uv run python run.py`：启动后端。
- 在 `web/` 目录运行 `pnpm i` 安装前端依赖，运行 `pnpm dev` 启动 Vite。
- 在 `web/` 目录运行 `pnpm build` 构建前端，运行 `pnpm lint` 执行 ESLint。
- `make check`：检查 Python 格式并运行 Ruff；`make format`：使用 Black 和 isort 格式化代码。
- `make test`：运行 pytest，需要本地 `.env`。后端测试放在 `tests/`，文件名使用 `test_*.py`。

## 代码风格与命名

Python 使用 4 空格缩进，Black 行宽为 120，isort 使用 Black 配置；对 `app/` 运行 Ruff。JavaScript 和 Vue 使用 2 空格缩进、单引号、不加分号，格式参数见 `web/.prettierrc.json`。Python 模块和函数使用 `snake_case`，Vue 组件使用 `PascalCase`。新增接口按功能放入 `app/api/v1/` 对应目录。

## 测试指南

修改后端行为时运行 `make test`；修改前端时运行 `pnpm lint` 和 `pnpm build`。行为变更应补充针对性回归测试。涉及 UI 的 PR 请尽量附上页面截图；当前前端未配置独立测试运行器。

## 提交与拉取请求

近期提交标题简短、以动作描述为主，常见格式如 `fix ...`、`Update ...`。请说明改动内容及关联问题，列出实际执行的验证命令；UI 改动请附截图。

## 安全与配置

本地开发时可复制 `.env.example` 为 `.env` 并填写环境配置。不要提交真实密码、令牌或其他环境专属密钥；文档和示例仅使用安全的占位值。

# KaifangLab

**Server capabilities for KaifangHarness agents**

KaifangLab provides shared server-side management and foundational capabilities for KaifangHarness, our in-house agent platform. Its current scope covers identity, role and API permissions, organizational units, menu resources, and audit logs.

## Delivery scope

| Capability | Description |
| --- | --- |
| Identity | User sign-in, JWT tokens, and account profile management |
| Access control | Role-based menu and API authorization with dynamic navigation |
| Organization | Department and user administration |
| Audit trail | Searchable records of key management requests |
| Service administration | Menu resources and API permission catalog |

The backend exposes REST APIs, while the console manages platform configuration and permissions. Model inference and agent orchestration are handled by KaifangHarness and are outside this service's current delivery scope.

## Technology

- Backend: Python 3.12, FastAPI, Tortoise ORM
- Console: Vue 3, Vite, Naive UI
- Data: PostgreSQL by default, with SQLite available for local development
- Local services: PostgreSQL and Redis through Docker Compose

## Run locally

### Backend

Install Docker and [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from the repository root:

```sh
cp .env.example .env
docker compose up -d postgres redis
uv sync
uv run python run.py
```

The API listens at `http://localhost:9999`; interactive API documentation is available at `http://localhost:9999/docs`. Database settings are documented in `.env.example`. Set `DB_BACKEND=sqlite` to use a local SQLite database.

### Console

Node.js 18.8 or newer and pnpm are required:

```sh
cd web
pnpm install
pnpm dev
```

## Initial sign-in

The first startup creates the `admin` account with the initial password `123456`. Use it only for local development. Set a unique, strong password before deploying to a shared or production environment.

## Delivery

Build the application image from the repository root:

```sh
docker build -t kaifanglab:0.1.0 .
```

Configure the PostgreSQL address and credentials, JWT secret, debug mode, and allowed origins for deployment. Use dedicated production secrets and database credentials, set `DEBUG=false`, and restrict `CORS_ORIGINS` to the console's actual domain.

## Repository layout

```text
app/          FastAPI APIs, business logic, data models, and settings
migrations/   Database migrations generated at runtime
deploy/       Web server and container entrypoint configuration
web/          Vue administration console
```

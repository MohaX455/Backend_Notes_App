# Notes App Backend

A FastAPI backend for a workspace-based notes application. The backend handles authentication, workspace management, and note CRUD operations with async SQLAlchemy.

## Overview

The backend exposes REST endpoints for:
- user registration and login
- JWT access token and refresh token management
- workspace creation, retrieval, update, and deletion
- note creation, retrieval, update, and deletion
- health checks for API and database

## Tech stack

| Layer | Technology |
| --- | --- |
| Framework | FastAPI |
| ORM | SQLAlchemy (async) |
| Database | MySQL |
| Auth | JWT with refresh tokens |
| Validation | Pydantic |
| Migrations | Alembic |
| Tooling | Python, pytest |

## Architecture

- `app/main.py` — FastAPI application and CORS setup
- `app/api/routes/` — route controllers for auth, notes, workspace, and health
- `app/services/` — business logic services
- `app/repositories/` — repository layer for database access
- `app/models/` — SQLAlchemy ORM models
- `app/schemas/` — request/response Pydantic models
- `app/core/` — configuration, database, security, and dependencies

## Database models

- `User` — username, email, password hash, workspaces, notes, refresh tokens
- `Workspace` — user-owned workspace container for notes
- `Note` — workspace note with title, content, pin flag
- `RefreshToken` — refresh token persistence and revocation state

## API overview

### Auth
- `POST /auth/register` — register a new user
- `POST /auth/login` — login and receive access token and refresh cookie
- `POST /auth/refresh` — refresh access token using stored refresh cookie
- `POST /auth/logout` — revoke refresh token
- `GET /auth/me` — get current authenticated user

### Workspace
- `GET /api/workspaces` — get current user workspaces
- `POST /api/workspace` — create workspace
- `GET /api/workspace/{id}` — get workspace details
- `PUT /api/workspace/{id}` — update workspace name
- `DELETE /api/workspace/{id}` — delete workspace

### Notes
- `GET /api/notes` — list notes for a workspace
- `POST /api/notes` — create note
- `GET /api/notes/{id}` — get note by ID
- `PUT /api/notes/{id}` — update note
- `DELETE /api/notes/{id}` — delete note

### Health
- `GET /health/` — API health check
- `GET /health/db` — database connectivity check

## Environment variables

The backend loads configuration from `.env` via Pydantic settings.

Required variables:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=youruser
DB_PASSWORD=yourpassword
DB_NAME=yourdb
SECRET_KEY=your-secret-key
API_URL=http://localhost:8000
```

## Run locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run with Docker

```bash
docker build -t notes-app-backend .
```

The project also supports combined orchestration via `docker compose up --build` from the repository root.

## Production readiness

- async SQLAlchemy session management
- JWT auth with refresh token rotation
- refresh token persistence and revocation
- Alembic migrations
- health endpoints
- CORS config for frontend origin

## Skills demonstrated

- FastAPI REST API development
- async SQLAlchemy repository pattern
- JWT authentication and token refresh
- Pydantic request/response validation
- Docker containerization
- database schema modeling with relationships

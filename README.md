# Divvy

Divvy is a full-stack web application for managing shared household expenses, groups, and authentication.

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI + Uvicorn + SQLAlchemy
- Database: PostgreSQL
- Auth: JWT + Argon2 password hashing
- Runtime: Docker Compose

## Repository Structure

```text
DIVVY/
├── FrontEnd/               # React frontend
├── backend/                # FastAPI backend
├── docker-compose.yml      # Multi-service Docker setup
├── .env.example            # Environment variable template
├── scripts/
│   ├── start.sh            # Smart startup script (Linux/macOS)
│   └── start.ps1           # Smart startup script (Windows PowerShell)
└── README.md
```

## Prerequisites

- Docker
- Docker Compose (Docker CLI plugin)

No local Python, Node, or PostgreSQL installation is required for normal development.

## Quick Start

1. Create your environment file:

```bash
cp .env.example .env
```

2. Update `.env` with your values:

- Set a secure `SECRET_KEY`
- Set `FRONTEND_HOST=http://localhost:5173`
- For remote database (Neon or other): set `DATABASE_URL` to that remote connection string
- For local Docker PostgreSQL: remove `DATABASE_URL` or leave it empty

3. Start the app:

Linux/macOS:

```bash
./scripts/start.sh
```

Windows PowerShell:

```powershell
./scripts/start.ps1
```

The smart start script does this automatically:

- If `DATABASE_URL` points to a remote DB, it starts `frontend` and `backend`
- If no remote DB is detected, it starts `frontend`, `backend`, and local PostgreSQL (`local-db` profile)

## Manual Docker Commands

Use these if you prefer direct compose commands.

Start with remote DB:

```bash
docker compose up
```

Start with local PostgreSQL container:

```bash
docker compose --profile local-db up
```

Start detached:

```bash
docker compose up -d
# or
docker compose --profile local-db up -d
```

Stop services:

```bash
docker compose down
# or
docker compose --profile local-db down
```

Rebuild images:

```bash
docker compose up --build
# or
docker compose --profile local-db up --build
```

View logs:

```bash
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

## Local URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

Backend tests from the running backend container:

```bash
docker compose exec backend pytest
```

If you started with the local DB profile, the same command works:

```bash
docker compose --profile local-db exec backend pytest
```

## Troubleshooting

- Missing `.env`:
  - `scripts/start.sh` and `scripts/start.ps1` will copy `.env.example` and stop so you can edit values.
- Backend cannot connect to local DB:
  - Start using `./scripts/start.sh` or `docker compose --profile local-db up`
  - Ensure `DATABASE_URL` is empty or removed in `.env`
- Frontend cannot reach backend:
  - Confirm backend is running on port `8000`
  - Confirm `FRONTEND_HOST` in `.env` is `http://localhost:5173`

## Notes

For additional Docker details, see `DOCKER_README.md`.

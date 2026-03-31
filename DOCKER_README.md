# Docker Setup Guide

This guide explains how to run the Divvy application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)
- A `.env` file in the project root with your environment variables (see setup below)

## Environment Setup

### 1. Create your .env file

Copy the `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env` with your actual values:
- **If using Neon**: Add your Neon `DATABASE_URL`
- **If using local DB**: Leave `DATABASE_URL` commented out or empty
- **SECRET_KEY**: A secure random string for JWT tokens
- **Other settings**: API URLs, CORS origins, etc.

**Important**: The `.env` file is ignored by Git and Docker, so your secrets stay safe.

## Quick Start (Automatic Detection)

### 🎯 Easiest Method: Use the Start Script

The smart start script automatically detects if you're using Neon or need a local database:

**Linux/Mac:**
```bash
./start.sh
```

**Windows (PowerShell):**
```powershell
.\start.ps1
```

The script will:
- ✅ Check if you have a `.env` file
- ✅ Detect if you're using a remote database (Neon)
- ✅ Start only the services you need

## Manual Start Options

### Option 1: With Neon Database (Remote)

If your `.env` has a Neon `DATABASE_URL`:

```bash
docker compose up
```

This starts:
- Backend API on `http://localhost:8000` (connects to your Neon database)
- Frontend application on `http://localhost:5173`

### Option 2: With Local PostgreSQL

If you want to use a local database instead:

```bash
docker compose --profile local-db up
```

This starts:
- PostgreSQL database on `localhost:5432`
- Backend API on `http://localhost:8000`
- Frontend application on `http://localhost:5173`

## Access the Application

- **Frontend**: Open your browser to http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

## Useful Commands

### Stop all services

Press `Ctrl+C` in the terminal, then run:

```bash
docker compose down

# Or if using local-db profile
docker compose --profile local-db down
```

### Start services in background (detached mode)
```bash
# With Neon
docker compose up -d

# With local database
docker compose --profile local-db up -d

# Or use the start script with -d flag
./start.sh -d
```

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### Stop services
```bash
docker compose down
```

### Rebuild containers (after code changes to Dockerfile)
```bash
# With Neon
docker compose up --build

# With local database
docker compose --profile local-db up --build

# Or use the start script
./start.sh --build
```

### Remove all containers and volumes (clean slate)
```bash
# Be careful: this deletes local database data!
docker compose --profile local-db down -v
```

### Switch between Neon and Local Database

**To switch to Neon:**
1. Add your Neon `DATABASE_URL` to `.env`
2. Run `docker compose up`

**To switch to local PostgreSQL:**
1. Comment out or remove `DATABASE_URL` from `.env`
2. Run `docker compose --profile local-db up`

### Access a service shell
```bash
# Backend
docker compose exec backend bash

# Frontend
docker compose exec frontend sh

# Database (if using local-db profile)
docker compose exec db psql -U postgres -d roommate_expense_splitter
```

### Run database migrations
```bash
docker compose exec backend python -m app.db.init_db
```

## Testing with Local Database

For running tests, you can use a local PostgreSQL container instead of your production Neon database:

### Start test environment
```bash
docker compose -f docker compose.test.yml up
```

This creates:
- A local PostgreSQL test database on `localhost:5433`
- Runs your test suite against this database

### Run tests manually
```bash
# Start just the test database
docker compose -f docker compose.test.yml up test-db -d

# Run tests
docker compose -f docker compose.test.yml run --rm backend-test pytest -v

# Or run tests in the main backend container
docker compose exec backend pytest -v
```

### Clean up test database
```bash
docker compose -f docker compose.test.yml down -v
```

## Development Workflow

The Docker setup includes volume mounts, so code changes are automatically reflected:

- **Backend**: Hot-reload enabled with `--reload` flag
- **Frontend**: Vite's hot module replacement (HMR) works automatically
- **Database**: Uses your remote Neon database by default, or local container if DATABASE_URL not set

## Environment Variables

Environment variables are loaded from your `.env` file:

- The backend container reads all variables from `.env`
- Never commit `.env` to Git (it's in `.gitignore`)

### For Neon Database (Remote):
```env
PROJECT_NAME=Divvy
API_V1_STR=/api/v1
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/database
TEST_DATABASE_URL=postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/test_database
FRONTEND_HOST=http://localhost:5173
```

### For Local Database:
```env
PROJECT_NAME=Divvy
API_V1_STR=/api/v1
SECRET_KEY=your-secure-secret-key
# Leave DATABASE_URL commented out or empty - it will default to the local container
# DATABASE_URL=
FRONTEND_HOST=http://localhost:5173
```

**The docker compose.yml automatically uses the local database container if `DATABASE_URL` is not set!**

## Troubleshooting

### Port already in use
If you get port conflicts, stop other services or change ports in `docker compose.yml`.

### Database connection issues
Make sure the backend waits for the database to be ready. The `healthcheck` configuration handles this.

### Frontend can't connect to backend
Check that `VITE_API_URL` points to the correct backend URL.

### Backend can't connect to Neon database
1. Check your `.env` file exists and has the correct `DATABASE_URL`
2. Verify your Neon database is accessible (not paused)
3. Check that your IP is allowed in Neon's settings (if IP restrictions are enabled)

### Backend can't connect to local database
1. Make sure you started with `--profile local-db` flag
2. Check the database container is running: `docker compose ps`
3. View backend logs: `docker compose logs backend`

### Permission issues
On Linux, you might need to run Docker commands with `sudo` or add your user to the `docker` group.

## Production Deployment

For production:

1. Use multi-stage builds in Dockerfiles
2. Build optimized frontend: `npm run build` and serve with nginx
3. Set proper environment variables (strong SECRET_KEY, etc.)
4. Use Docker secrets for sensitive data
5. Configure proper CORS settings
6. Use a reverse proxy (nginx/traefik)

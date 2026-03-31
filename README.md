# Divvy

Software Engineering II project.

Divvy is a full-stack web application for managing shared household expenses, roommate groups, and authentication.

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI + Uvicorn + SQLAlchemy
- Database: PostgreSQL
- Auth: JWT + Argon2 password hashing

## Repository Structure

```text
Roommate-Expense-Splitter/
├── FrontEnd/              # React frontend
├── backend/               # FastAPI backend
├── .env.example           # Example environment variables
├── .env                   # Your local environment variables
└── README.md
```

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL 12+ server if you host DB locally
- PostgreSQL client (`psql`) only if you need to run SQL scripts manually (optional for remote pre-initialized DBs)

## 0. Install Prerequisites

Install Python, Node.js, npm, and PostgreSQL using your OS package manager.

If you use a remote database that is already initialized, you can skip installing PostgreSQL locally and skip `psql`.

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm postgresql postgresql-contrib
```

macOS (Homebrew):

```bash
brew update
brew install python node postgresql@16
brew services start postgresql@16
```

Windows (winget, PowerShell):

```powershell
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS.17
winget install PostgreSQL.PostgreSQL
```

After installation, verify versions:

```bash
python3 --version
node --version
npm --version
psql --version
```

If `psql` is not installed, that is fine when using a remote DB that is already initialized.

## 1. Install Backend Dependencies

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Install Frontend Dependencies

From the repository root:

```bash
cd FrontEnd
npm install
```

## 3. Configure Environment Variables

From the repository root, copy the example file and update values for your machine:

```bash
cp .env.example .env
```

Note: backend settings load from `../.env`, so keep `.env` at the repository root.

## 4. Initialize PostgreSQL Database

Only do this step if your PostgreSQL database is uninitialized (fresh setup).

If you are using a remote DB that is already initialized, skip this section.

Create the database and run schema scripts:

Example:

```bash
createdb roommate_expense_splitter
psql -U postgres -d roommate_expense_splitter -f backend/sql_scripts/create_tables.sql
```

Optional seed data:

```bash
psql -U postgres -d roommate_expense_splitter -f backend/sql_scripts/seed_test_data.sql
```

## 5. Run the Project (Backend + Frontend Together)

Use two terminals.

Terminal 1 (backend):

```bash
cd backend
source .venv/bin/activate
./scripts/run-dev.sh
```

If the script is not executable:

```bash
bash scripts/run-dev.sh
```

Or on Windows (PowerShell):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
.\scripts\run-dev.ps1
```

Terminal 2 (frontend):

```bash
cd FrontEnd
npm run dev
```

## Local URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests (Backend)

```bash
cd backend
source .venv/bin/activate
pytest
```

## Common Issues

- Backend fails to load environment variables:
  - Confirm `.env` is in the repository root, not in `backend/`.
- Frontend cannot reach backend:
  - Ensure backend is running on port 8000.
  - Ensure `FRONTEND_HOST` in `.env` matches the frontend URL.
- Database connection errors:
  - Verify PostgreSQL is running.
  - Verify `DATABASE_URL` credentials, host, port, and database name.

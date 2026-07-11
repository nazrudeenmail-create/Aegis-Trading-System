# Development Workflow

> Find the right commands for every environment change — no hunting, no guesswork.

---

| | GitHub Codespaces | Your Local Machine |
|--|------------------|--------------------|
| Docker | ✅ Pre-installed | 🔧 [Install Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| Python | ✅ Pre-installed | ✅ Install from [python.org](https://www.python.org/downloads/) |
| Node.js | ✅ Pre-installed | ✅ Install from [nodejs.org](https://nodejs.org/) (LTS) |
| Git | ✅ Pre-installed | ✅ Install from [git-scm.com](https://git-scm.com/) |

> ⚠️ **Docker is the only tool you must install yourself on a local machine.**  
> If you see `docker: command not found`, jump to [Troubleshooting → Docker not installed](#docker-command-not-found).

---

## Table of Contents

- [1. Quick Start — First Time on a New Machine](#1-quick-start--first-time-on-a-new-machine)
- [2. Docker — All Services at Once](#2-docker--all-services-at-once)
- [3. Local Development — No Docker for Backend/Frontend](#3-local-development--no-docker-for-backendfrontend)
- [4. Daily Workflow Checklist](#4-daily-workflow-checklist)
- [5. Troubleshooting](#5-troubleshooting)
- [6. Command Cheat Sheet](#6-command-cheat-sheet)

---

## 1. Quick Start — First Time on a New Machine

### Prerequisites

| Tool | Minimum Version | Check Command | Required On |
|------|----------------|---------------|-------------|
| Python | 3.12+ | `python --version` | Always |
| Node.js | 20+ (LTS) | `node --version` | Always |
| npm | 9+ | `npm --version` | Always |
| Docker | 24+ | `docker --version` | Local machine (pre-installed on Codespaces) |
| Git | 2.40+ | `git --version` | Always |

> ⚠️ **On a new local machine, install Docker first.** Codespaces has it built-in.  
> Docker Desktop: [Windows/Mac](https://www.docker.com/products/docker-desktop/) | Linux: `sudo apt install docker.io docker-compose-v2`  
> After installing Docker Desktop on Windows/Mac, **restart your computer.**

### Option A: Automated Setup (Recommended)

**Linux / macOS / GitHub Codespaces:**

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows (PowerShell):**

```powershell
.\scripts\setup.ps1
```

This script handles everything:
- Creates Python virtual environment (`venv`)
- Installs all Python and Node.js dependencies
- Creates `.env` files from `.env.example` templates
- Auto-generates a `SECRET_KEY`

### Option B: Manual Setup (If Script Fails)

**Step 1 — Clone and enter project:**

```bash
git clone https://github.com/nazrudeenmail-create/Aegis-Trading-System.git
cd Aegis-Trading-System
```

**Step 2 — Backend:**

```bash
cd backend

# Virtual environment
python -m venv venv

# Activate (Linux/macOS):
source venv/bin/activate
# Activate (Windows PowerShell):
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env
cp .env.example .env
# (Windows: copy .env.example .env)

# Edit DATABASE_URL in .env if your PostgreSQL credentials differ from defaults
# Default: postgresql+psycopg://ats_user:ats_password@localhost:5432/ats_development

cd ..
```

**Step 3 — Frontend:**

```bash
cd frontend
npm install
cp .env.example .env
cd ..
```

**Step 4 — Start database (Docker):**

```bash
docker compose up -d postgres
```

**Step 5 — Run database migrations:**

```bash
cd backend
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\Activate.ps1

alembic upgrade head
cd ..
```

**Step 6 — Verify setup (Linux/macOS):**

```bash
cd backend
source venv/bin/activate
python -c "from app.core.config import get_settings; from app.main import app; print('Backend OK')"
deactivate
cd ..

cd frontend
npm run build
cd ..
```

### Option C: CodeSpaces

Also run
```bash
    pip install -r backend/requirements.txt
```

---

## 2. Docker — All Services at Once

Docker runs PostgreSQL, backend, and frontend together in containers.

### First time (build images):

```bash
docker compose up --build
```

### Start all services:

```bash
docker compose up -d
```

The `-d` flag runs containers in the background.

### URLs when Docker is running:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API Docs (Swagger) | http://localhost:8000/docs |
| Backend API (Raw) | http://localhost:8000 |
| PostgreSQL | `localhost:5432` (user: `ats_user`, pass: `ats_password`, db: `ats_development`) |

### Start only the database (for local dev):

```bash
docker compose up -d postgres
```

### Check running containers:

```bash
docker ps
```

### View logs:

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### Stop all services:

```bash
docker compose down
```

### Reset everything (WARNING: deletes all database data):

```bash
docker compose down -v
docker compose up -d
```

### Rebuild after Dockerfile changes:

```bash
docker compose up --build -d
```

---

## 3. Local Development — No Docker for Backend/Frontend

Use this approach when you need hot-reload for active development. Docker is still used **only for PostgreSQL**.

### Prerequisite: Start Database

```bash
# Start PostgreSQL in background (run once per session)
docker compose up -d postgres
```

---

### 🐧 Linux / macOS

**Terminal 1 — Backend:**

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

**Terminal 3 (optional) — Logs:**

```bash
docker compose logs -f postgres
```

---

### 🪟 Windows (PowerShell)

**Terminal 1 — Backend:**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```powershell
cd frontend
npm run dev
```

**Terminal 3 (optional) — Logs:**

```powershell
docker compose logs -f postgres
```

---

### URLs when running locally:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API Docs | http://localhost:8000/docs |
| Backend API | http://localhost:8000 |

### Stop Services

- **Backend / Frontend:** `Ctrl + C` in each terminal
- **Database:** `docker compose down`
- **Deactivate venv (when done):** `deactivate`

---

## 4. Daily Workflow Checklist

When you sit down to work:

### Step 1 — Pull latest changes from GitHub:

```bash
git pull
```

### Step 2 — If Python dependencies changed (check `backend/requirements.txt`):

```bash
cd backend
# Activate venv first (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
cd ..
```

### Step 3 — If Node.js dependencies changed (check `frontend/package.json`):

```bash
cd frontend
npm install
cd ..
```

### Step 4 — If database schema changed (new migrations):

```bash
cd backend
# Activate venv first
alembic upgrade head
cd ..
```

### Step 5 — Make sure database is running:

```bash
docker compose up -d postgres
```

### Step 6 — Start services:

```bash
# Terminal 1: Backend
cd backend
# Linux/macOS:
source venv/bin/activate && uvicorn app.main:app --reload --port 8000
# Windows:
.\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Step 7 — Before leaving:

```bash
git status
git add .
git commit -m "Describe what you changed"
git push
```

### Quick Git Commands Reference:

| Task | Command |
|------|---------|
| Check what changed | `git status` |
| See actual changes | `git diff` |
| Add all changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push to GitHub | `git push` |
| Pull latest | `git pull` |
| See commit history | `git log --oneline -10` |

---

## 5. Troubleshooting

### "docker: command not found"

Docker is not installed. Check your environment:

**GitHub Codespaces:** Docker is always pre-installed. If it's missing, restart the codespace.

**Local Machine — Install Docker Desktop:**

| OS | Instructions |
|----|-------------|
| **Windows** | Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/). **Restart your PC after installation.** |
| **macOS** | Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/). |
| **Linux** | `sudo apt install docker.io docker-compose-v2` (Ubuntu/Debian) |

After installing, verify:
```bash
docker --version
```

### "Developing without Docker at all"

If you can't or don't want to install Docker, install PostgreSQL directly on your machine:

1. **Install PostgreSQL** from https://www.postgresql.org/download/
2. **During installation**, set the superuser password, then create:
   - User: `ats_user`
   - Password: `ats_password`
   - Database: `ats_development`
3. **Update `backend/.env`:**
   ```
   DATABASE_URL=postgresql+psycopg://ats_user:ats_password@localhost:5432/ats_development
   ```
4. **Run migrations** (venv must be activated):
   ```bash
   cd backend
   alembic upgrade head
   ```
5. Continue with the normal [Local Development](#3-local-development--no-docker-for-backendfrontend) section — just skip the `docker compose up -d postgres` step since PostgreSQL is already running natively.

> ⚠️ **Cloud PostgreSQL alternative:** If you prefer a free cloud database, services like [Neon](https://neon.tech), [Supabase](https://supabase.com), or [Railway](https://railway.app) offer free PostgreSQL tiers. Just update `DATABASE_URL` with their connection string.

### "Port 8000 is already in use"

Something else is using the backend port. Kill it:

**Linux/macOS:**
```bash
lsof -i :8000
kill -9 <PID>
```

**Windows (PowerShell):**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "Port 5173 is already in use"

Same issue for frontend port. Replace `8000` with `5173` in the commands above.

### "Database connection refused"

Make sure PostgreSQL container is running:

```bash
docker ps | grep postgres
```

If not running:
```bash
docker compose up -d postgres
```

If it's running but still failing, check the DATABASE_URL in `backend/.env`:
- **Local dev (no Docker for backend):** `postgresql+psycopg://ats_user:ats_password@**localhost**:5432/ats_development`
- **Inside Docker:** `postgresql+psycopg://ats_user:ats_password@**postgres**:5432/ats_development`

### "Docker container won't start"

Check logs:
```bash
docker compose logs postgres
```

Common fix — wipe and restart:
```bash
docker compose down -v
docker compose up -d postgres
```

### "Module not found" errors in backend

Reactivate venv and reinstall:
```bash
cd backend
# Activate venv
pip install -r requirements.txt
```

### "Virtual environment not found" / "No module named venv"

Create it:
```bash
cd backend
python -m venv venv
# Activate, then:
pip install -r requirements.txt
```

### "alembic: command not found"

Make sure venv is activated:
```bash
cd backend
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\Activate.ps1
alembic upgrade head
```

### "Missing SECRET_KEY" warning

The setup script auto-generates this. To do it manually:
```bash
cd backend
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output into backend/.env as SECRET_KEY=<output>
```

---

## 6. Command Cheat Sheet

### General

| Task | Linux / macOS / Codespaces | Windows (PowerShell) |
|------|---------------------------|---------------------|
| One-time setup | `./scripts/setup.sh` | `.\scripts\setup.ps1` |
| Docker not installed? | See [Troubleshooting](#docker-command-not-found) | See [Troubleshooting](#docker-command-not-found) |
| Open project | `cd /path/to/Aegis-Trading-System` | `cd C:\Users\...\Aegis-Trading-System` |
| Pull latest | `git pull` | `git pull` |
| Push changes | `git add . && git commit -m "msg" && git push` | `git add .; git commit -m "msg"; git push` |

### Database (PostgreSQL)

| Task | Command (run from project root) |
|------|--------------------------------|
| Start DB | `docker compose up -d postgres` |
| Stop DB | `docker compose down` |
| Check if running | `docker ps` |
| Reset DB (⚠️ data loss) | `docker compose down -v && docker compose up -d postgres` |
| Run migrations | `cd backend && alembic upgrade head && cd ..` |
| Create migration | `cd backend && alembic revision --autogenerate -m "description" && cd ..` |
| View DB logs | `docker compose logs -f postgres` |

### Backend

| Task | Linux / macOS | Windows (PowerShell) |
|------|--------------|---------------------|
| Activate venv | `cd backend && source venv/bin/activate` | `cd backend; .\venv\Scripts\Activate.ps1` |
| Start backend | `uvicorn app.main:app --reload --port 8000` | `uvicorn app.main:app --reload --port 8000` |
| Install deps | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Run tests | `pytest` | `pytest` |
| Run single test | `pytest tests/test_file.py -v` | `pytest tests/test_file.py -v` |
| Deactivate venv | `deactivate` | `deactivate` |

### Frontend

| Task | Command (run from `frontend/`) |
|------|--------------------------------|
| Install deps | `npm install` |
| Start dev server | `npm run dev` |
| Production build | `npm run build` |
| Preview build | `npm run preview` |
| Lint | `npm run lint` |

### Docker (All Services)

| Task | Command (run from project root) |
|------|--------------------------------|
| Start all (first time) | `docker compose up --build` |
| Start all (background) | `docker compose up -d` |
| Stop all | `docker compose down` |
| Rebuild & restart | `docker compose up --build -d` |
| View all logs | `docker compose logs -f` |
| View service logs | `docker compose logs -f backend` |
| Reset everything | `docker compose down -v && docker compose up --build -d` |
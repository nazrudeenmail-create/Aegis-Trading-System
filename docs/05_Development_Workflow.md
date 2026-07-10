
---

# 05_Development_Workflow.md

## Working in GitHub Codespaces

### Open Project

```bash
cd /workspaces/Aegis-Trading-System
```

### Start Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

### Verify Everything

```bash
git status
```

---

## Before Leaving Codespaces

### Check Changes

```bash
git status
```

### Commit

```bash
git add .
git commit -m "Your message"
```

### Push

```bash
git push
```

---

## Working on Local Laptop

### Open Project

```bash
cd path/to/Aegis-Trading-System
```

### Update Project

```bash
git pull
```

### Start Backend

**Windows**

```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

**Linux/macOS**

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

---

## Before Leaving Local

```bash
git status
git add .
git commit -m "Your message"
git push
```

---

## First Time Only (New Machine)

### Install Python Packages

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Start Docker

```bash
docker compose up -d
```

---

## If Someone Else Updated GitHub

```bash
git pull
```

---

## If Dependencies Changed

```bash
pip install -r backend/requirements.txt
```

---

## If Database Changed

```bash
alembic upgrade head
```

---

## Check Running Containers

```bash
docker ps
```

---

## Stop Docker

```bash
docker compose down
```

---

## Exit Virtual Environment

```bash
deactivate
```

---



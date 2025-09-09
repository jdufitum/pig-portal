## Pig Farm Web App

Full‑stack app with a FastAPI backend and a React (Vite + TypeScript) frontend.

There are two backends in this repository:
- `backend/` (primary): production‑ready FastAPI app used by Docker Compose, with Postgres, Alembic migrations, and Nginx at the edge.
- `app/` (minimal): lightweight FastAPI demo used for simple local development with SQLite.

### Prerequisites
- Docker, Docker Compose v2, and Make (for the full stack)
- Node.js 18+ and npm (for frontend dev server)
- Python 3.11+ (for the minimal backend)

---

## Quick Start

Clone the repository:

```bash
git clone <your-repo-url>.git
cd <your-repo-dir>
```

Pick one workflow:

### A) Full stack with Docker Compose (recommended)
1) Create an `.env` at the repo root:
```env
# Required
POSTGRES_PASSWORD=changeme
SECRET_KEY=please-change-me
CORS_ORIGINS=http://localhost

# Optional (S3-compatible storage for file features)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=pigfiles

# Optional timezone and backup retention
TZ=UTC
BACKUP_SCHEDULE=@daily
BACKUP_KEEP_DAYS=7
BACKUP_KEEP_WEEKS=4
BACKUP_KEEP_MONTHS=3
```

2) Build and start the stack:
```bash
make up
```

3) Open the app and API:
- App: http://localhost
- API docs: http://localhost/api/docs

Useful commands:
```bash
make logs     # follow all service logs
make down     # stop and remove containers
```

Notes:
- The Compose stack builds the frontend image, which already contains the built SPA in `/usr/share/nginx/dist`. To apply UI code changes, rebuild just the frontend service:
  ```bash
  docker compose --env-file .env -f infrastructure/docker-compose.yml build frontend && \
  docker compose --env-file .env -f infrastructure/docker-compose.yml up -d frontend
  ```
- The backend container runs database migrations automatically on start: `alembic upgrade head`.

### B) Local development without Docker (simple, SQLite)
Run the minimal backend (`app/`) and the Vite dev server.

Backend:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd frontend
npm ci
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

Open:
- App: http://localhost:5173
- API docs (minimal backend): http://localhost:8000/docs

---

## Project Structure
- `backend/`: Primary FastAPI service (used by Docker Compose). See `backend/README.md` for internals.
- `frontend/`: React + Vite SPA, built into an Nginx image for production.
- `infrastructure/`: Nginx config and `docker-compose.yml` orchestrating db, backend, frontend, backups.
- `Makefile`: Convenience targets for Compose lifecycle.
- `app/`: Minimal FastAPI demo (SQLite) for simple local dev.

---

## Common Tasks

### Migrations (backend service)
Migrations run automatically on container start. To run manually:
```bash
docker compose --env-file .env -f infrastructure/docker-compose.yml exec backend alembic upgrade head
```

### Backups (Postgres)
Create a compressed backup to the current directory:
```bash
make backup
```
Restore from a `.sql.gz` file:
```bash
make restore FILE=backup_YYYYmmdd_HHMMSS.sql.gz
```

### Seeding demo data (minimal backend only)
```bash
source .venv/bin/activate  # if not already active
python scripts/seed.py
```

---

## Environment Notes
- Backend reads `SECRET_KEY` (or `JWT_SECRET`) and `CORS_ORIGINS` (or `ALLOWED_ORIGINS`).
- Compose injects `DATABASE_URL` for Postgres; the minimal backend defaults to SQLite at `sqlite:///./pigs.db`.
- For the Vite dev server, set `VITE_API_BASE_URL` to your backend origin (e.g., `http://localhost:8000`).

---

## Troubleshooting
- CORS errors: ensure `CORS_ORIGINS` includes your frontend origin (e.g., `http://localhost` or `http://localhost:5173`).
- Port conflicts: free up ports 80 (frontend), 8000 (backend), 5173 (Vite), or adjust Compose.
- Frontend changes not visible in Docker: rebuild and redeploy the `frontend` service (see notes in Quick Start A).


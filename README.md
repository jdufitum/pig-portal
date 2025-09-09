## Pig Farm Web App

A full-stack web application consisting of a FastAPI backend and a React (Vite + TypeScript) frontend.

### Quick Start

Clone the repository:

```bash
git clone <your-repo-url>.git
cd <your-repo-dir>
```

Run locally (recommended for development):

```bash
# Backend (FastAPI)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Vite)
cd frontend
npm ci
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

Open the app at `http://localhost:5173`.

### API Docs

- Local dev: `http://localhost:8000/docs`
- Docker (behind Nginx): `http://localhost/api/docs`

### Project Structure

- `app/`: FastAPI application (used by Docker Compose and local dev)
- `frontend/`: React + Vite SPA
- `infrastructure/`: Nginx config and Docker Compose
- `Dockerfile`: Backend image for the `app/` service
- `Makefile`: Convenience targets for Docker Compose lifecycle
- `backend/`: An additional FastAPI project (not used by default). See `backend/README.md`.

## Running with Docker Compose

Prerequisites: Docker and Docker Compose v2, Make.

1) Create an `.env` file at the repository root (see sample below).

2) Build the frontend and generate static assets:

```bash
cd frontend
npm ci
npm run build
cd ..
```

3) Start the stack:

```bash
make up
```

4) Populate the Nginx volume with the frontend build (one-time or whenever you rebuild the frontend):

```bash
docker compose --env-file .env -f infrastructure/docker-compose.yml \
  run --rm -v "$(pwd)/frontend/dist:/dist" frontend \
  sh -lc 'rm -rf /usr/share/nginx/html/* && cp -r /dist/* /usr/share/nginx/html'
```

Then open `http://localhost`.

To view logs or stop services:

```bash
make logs
make down
```

### Environment Variables (.env)

Create a file named `.env` at the repository root. These are consumed by `infrastructure/docker-compose.yml` and the `Makefile`:

```env
# Required
POSTGRES_PASSWORD=changeme
JWT_SECRET=please-change-me
ALLOWED_ORIGINS=http://localhost:5173,http://localhost

# Optional (for S3-compatible object storage integrations)
S3_ENDPOINT=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=

# Optional: container timezone
TZ=UTC
```

Notes:
- The backend will use Postgres via `DATABASE_URL` injected by Docker Compose.
- For local development without Docker, the backend defaults to SQLite at `sqlite:///./pigs.db`.
- If you run the frontend dev server, set `VITE_API_BASE_URL=http://localhost:8000` so API calls go to the FastAPI server.

## Local Development (detailed)

### Backend (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Optional: override DB (defaults to SQLite)
# export DATABASE_URL=postgresql+psycopg://postgres:<password>@localhost:5432/pigs
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: `GET http://localhost:8000/health`

### Frontend (Vite + React)

```bash
cd frontend
npm ci
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

Open `http://localhost:5173`.

## Troubleshooting

- CORS errors: ensure `ALLOWED_ORIGINS` includes your frontend origin (e.g., `http://localhost:5173`). For local dev, use the `VITE_API_BASE_URL` env as shown above.
- Frontend not loading with Docker: make sure you have built the frontend and copied `frontend/dist` into the `frontend_build` volume (see step 4 under Docker Compose).
- Port conflicts: change ports or stop processes occupying ports 80, 8000, or 5173.


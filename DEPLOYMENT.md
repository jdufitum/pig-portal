# Deployment Guide (Single VPS)

This guide deploys a production-ready stack with Docker Compose, Nginx (or Caddy) reverse proxy, HTTPS, PostgreSQL, and environment variables.

## 1) Prerequisites
- Ubuntu 22.04+ VPS
- Docker and Docker Compose installed
- DNS A record pointing to your VPS (for HTTPS)

## 2) Clone and configure
```bash
git clone <this-repo>
cd <this-repo>
cp .env.example .env
# Edit .env with secure values (SECRET_KEY, POSTGRES_PASSWORD, etc.)
```

Required .env keys:
- POSTGRES_PASSWORD
- SECRET_KEY (or JWT_SECRET)
- CORS_ORIGINS (comma-separated)
- S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET (optional)
- TZ

## 3) Build frontend
Place built frontend assets into volume `frontend_build` or adapt compose to build your frontend image. For a simple copy:
- scp or mount your frontend `dist/` into `infrastructure/frontend_build` directory (create it), then bind mount in compose, or bake a separate image.

## 4) Bring up the stack
```bash
make up
make logs
```
This starts:
- db: PostgreSQL 16
- backend: FastAPI app
- frontend: Nginx serving static and proxying /api

Open http://YOUR_SERVER (HTTPS below).

## 5) HTTPS Options

### Option A: Caddy (automatic HTTPS)
- Install Caddy on the VPS (or run as container)
- Edit `infrastructure/Caddyfile` and set your domain
- Run Caddy alongside compose, pointing to `backend:8000` and serving static at `/usr/share/nginx/html`. Example run:
```bash
sudo caddy run --config infrastructure/Caddyfile
```
Caddy will obtain and renew certificates automatically.

### Option B: Nginx + certbot
- Install certbot: `sudo apt-get install -y certbot python3-certbot-nginx`
- Ensure Nginx container maps port 80, and add port 443 mapping with TLS server block (or run host Nginx)
- On host, run:
```bash
sudo certbot --nginx -d your.domain.com --redirect
```
- Update Nginx config to proxy `/api` to `backend:8000` and serve static. Certificates are managed by certbot.

## 6) Makefile commands
- make up: build and start services
- make down: stop services
- make logs: follow logs
- make backup: dump the Postgres DB (ad-hoc; nightly backups also run in container)
- make restore FILE=backup_timestamp.sql.gz: restore a backup into DB

## 7) Environment and secrets
All secrets are loaded from `.env`. Do not commit `.env`. Rotate regularly.

## 8) Backups
Nightly backups are performed by the `backup` service using `postgres-backup-local` with retention settings:

- `BACKUP_SCHEDULE` (cron or shortcuts like @daily)
- `BACKUP_KEEP_DAYS`, `BACKUP_KEEP_WEEKS`, `BACKUP_KEEP_MONTHS`

Backups are stored in the `db_backups` volume inside the compose project. Periodically copy them off the host:

```bash
docker compose --env-file .env -f infrastructure/docker-compose.yml run --rm \
  -v "$PWD:/host" backup sh -lc 'cp -r /backups /host/db_backups'
```

You can still run `make backup` for an immediate dump.

## 10) Monitoring

- Prometheus metrics are exposed at `/metrics` on the backend (port 8000).
- If using a reverse proxy, also surface at `/api/metrics`. Configure your Prometheus scrape job accordingly.

## 9) Updates
```bash
git pull
make build
make up
```
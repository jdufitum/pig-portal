## Backend (FastAPI)

### Setup
1. Create and fill a `.env` based on `.env.example`.
2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

### Run (dev)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Alembic
```bash
alembic upgrade head
```
# FinServ Issue Autopilot

Dashboard and automation backend for triaging and resolving GitHub issues in the [finserv-monorepo-demo](https://github.com/ikc2210/finserv-monorepo-demo) repository.

## Structure

```
frontend/   React + Vite + Tailwind dashboard
backend/    FastAPI API server
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the dashboard polls the backend at http://localhost:8000/api.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/issues` | List all tracked issues |
| `POST` | `/api/run` | Trigger the automation pipeline |
| `POST` | `/api/issues/{id}/override` | Move a needs_human issue back to automation |
| `GET` | `/health` | Health check |

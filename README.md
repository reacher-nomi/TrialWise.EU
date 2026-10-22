# TrialWise

Explainable clinical-trial eligibility analysis. Paste a trial's inclusion/exclusion criteria and get them back as structured data, with the original sentence kept as evidence. Anything the system can't read safely is flagged for **manual review** instead of guessed.

> DPD-26W student prototype (TH Deggendorf). Public data only, no real patient data.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript, built with Vite |
| Backend | FastAPI (Python 3.13), SQLAlchemy 2 |
| Database | PostgreSQL 17 |
| External data | ClinicalTrials.gov API v2 |
| Dependencies | `uv` (Python), `npm` (frontend). Both use lock files |
| Containers | Docker + Docker Compose |
| CI | GitHub Actions |
| Environments | Dev = local · Stage = GitHub Codespaces · Live = Azure VM |

## Quick start (Dev)

You need **Docker Desktop** installed and running.

```bash
cp .env.example .env          # Windows PowerShell: copy .env.example .env
docker compose up --build
```

| What | URL |
|---|---|
| App | http://localhost:5173 |
| API docs (try every endpoint) | http://localhost:8000/docs |

Code changes reload automatically. Stop with `Ctrl+C`. Wipe the database with `docker compose down -v`.

## Run without Docker (optional)

```bash
# Backend: needs a running PostgreSQL, or use SQLite for quick tests:
cd backend
uv sync
DATABASE_URL=sqlite:///./dev.db uv run fastapi dev app/main.py

# Frontend (second terminal)
cd frontend
npm install
npm run dev
```

## Tests & checks (same as CI)

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest
cd frontend && npm run build
```

## Project structure

```
trialwise/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, all routes under /api
│   │   ├── config.py          # settings from environment variables
│   │   ├── db.py              # database engine, tables, session
│   │   ├── routers/           # HTTP endpoints (health, criteria, trials)
│   │   └── services/
│   │       ├── extractor.py   # ⭐ Criteria Analyzer (rule-based baseline)
│   │       └── ctgov.py       # ClinicalTrials.gov client
│   ├── tests/                 # pytest
│   ├── pyproject.toml + uv.lock
│   └── Dockerfile
├── frontend/
│   ├── src/                   # React app (App.tsx, api.ts)
│   ├── Dockerfile             # stages: dev / build / prod (nginx)
│   └── nginx.conf             # Live: serves app + proxies /api
├── docker-compose.yml         # Dev
├── docker-compose.prod.yml    # Live
├── .devcontainer/             # Stage (Codespaces)
├── .github/workflows/ci.yml   # CI pipeline
├── docs/                      # architecture, workflow, presentation notes
└── deploy/azure-vm.md         # how to deploy Live
```

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | API + database status ("one-button" check) |
| POST | `/api/criteria/analyze` | Criteria text → structured criteria (saved to DB) |
| GET | `/api/criteria/analyses` | List saved analyses |
| GET | `/api/criteria/analyses/{id}` | One saved analysis |
| GET | `/api/trials/search?condition=…&status=TERMINATED` | Search ClinicalTrials.gov |

## Team workflow

See [docs/workflow.md](docs/workflow.md): branches, pull requests, board, definition of done.

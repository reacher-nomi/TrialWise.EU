# Architecture

## Overview

```
                 Browser
                    │  (only talks to ONE origin → no CORS issues)
                    ▼
     ┌──────────────────────────────┐
     │ Frontend                     │  Dev:  Vite dev server  :5173
     │ React + TypeScript           │  Live: nginx            :80
     └──────────────┬───────────────┘
                    │  /api/*  (proxied)
                    ▼
     ┌──────────────────────────────┐        ┌─────────────────────────┐
     │ Backend – FastAPI            │ ─────▶ │ ClinicalTrials.gov API  │
     │  • routers  (HTTP layer)     │        │ (public trial data)     │
     │  • services (logic)          │        └─────────────────────────┘
     │      extractor.py            │        ┌─────────────────────────┐
     │      ctgov.py                │ ─ ─ ─▶ │ LLM API (planned)       │
     └──────────────┬───────────────┘        └─────────────────────────┘
                    │  SQLAlchemy
                    ▼
     ┌──────────────────────────────┐
     │ PostgreSQL 17                │  saved analyses
     └──────────────────────────────┘
```

Every box is one Docker container, started together by Docker Compose.

## Key decisions (and why)

| Decision | Choice | Why | Alternative considered |
|---|---|---|---|
| Backend framework | FastAPI | Python (team's strongest language), automatic API docs, type-checked requests | Django (heavier), Flask (less built in) |
| Frontend framework | React + TS (Vite) | Industry standard, typed, fast dev server | Vue, Streamlit (faster but less flexible UI) |
| Database | PostgreSQL | Reliable, JSON columns, full-text search, free | MongoDB (no need for schemaless data) |
| Container solution | Docker | Same setup on every laptop and the server | Plain installs ("works on my machine" problems) |
| Orchestrator | Docker Compose | Simple, one file, enough for 3 services | Kubernetes (far too complex for this scale) |
| Dependency management | uv + lock file; npm + package-lock | Exact same versions everywhere, very fast | pip + requirements.txt (no proper locking) |
| Cloud provider | Azure (EU region, Germany West Central) | Student credit, EU data location (GDPR-friendly) | AWS (similar), Render/Railway (simpler, less control) |
| CI | GitHub Actions | Built into GitHub, free for this usage | GitLab CI |

## Environments

| | Dev | Stage | Live |
|---|---|---|---|
| Where | Your laptop | GitHub Codespaces | Azure VM |
| Start | `docker compose up` | Open repo in Codespaces (auto-starts) | `docker compose -f docker-compose.prod.yml up -d` |
| Compose file | `docker-compose.yml` | `docker-compose.yml` | `docker-compose.prod.yml` |
| Hot reload | ✅ | ✅ | ❌ (optimised build) |
| Who uses it | Developers | Team + coach for testing | Demo / users |
| DB exposed | localhost only | Codespace only | ❌ never |

## Data & privacy

- Only **public** trial registry data + text users paste in.
- No real patient data is stored. Synthetic data only, if ever needed.
- Secrets live in `.env` (never committed). CI uses dummy values.

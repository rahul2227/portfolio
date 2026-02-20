# Portfolio — Claude Code Project Instructions

## Tech Stack

- **Frontend**: React 18 + Vite + TypeScript + Tailwind CSS
- **Backend**: FastAPI + async SQLAlchemy + aiosqlite (SQLite)
- **Infra**: Nginx reverse proxy + systemd + cloudflared tunnel
- **Python tooling**: `uv` (not pip) — always use `uv run`, `uv add`, `uv sync`
- **Node tooling**: `npm`
- **Server**: Raspberry Pi 4 (4GB), Debian 13 trixie, aarch64

## Key Commands

```bash
# Backend dev
cd backend && uv run uvicorn portfolio_api.main:app --reload --port 8000

# Frontend dev (proxies /api to :8000)
cd frontend && npm run dev

# Build frontend for production
cd frontend && npm run build

# Lint
cd backend && uv run ruff check .
cd frontend && npm run lint

# Seed database
cd backend && uv run python -m portfolio_api.seed

# Deploy (on Pi)
bash deploy/scripts/deploy.sh
```

## Architecture

```
frontend/src/       → React SPA (pages + components)
backend/portfolio_api/ → FastAPI app
  main.py           → App entry point, root_path="/api"
  config.py         → pydantic-settings, env vars with PORTFOLIO_ prefix
  database.py       → async SQLAlchemy engine + session
  routers/          → health.py, projects.py, contact.py
  models/           → SQLAlchemy ORM models
  schemas/          → Pydantic v2 request/response schemas
  seed.py           → Load seed.json into DB
backend/data/       → seed.json (committed), portfolio.db (gitignored)
deploy/nginx/       → portfolio.conf
deploy/systemd/     → portfolio-backend.service, cloudflared-portfolio.service, portfolio-demo-ocr.service
deploy/scripts/     → deploy.sh
demos/text-ocr/     → Handwritten text recognition Streamlit demo
  app.py            → Streamlit app entry point
  model.py          → ONNX inference wrapper (OCRInference)
  models/           → ocr_lstm_int8.onnx (Git LFS), mappings.json
  tests/            → pytest test suite
  scripts/          → export_onnx.py (one-time ONNX conversion)
```

## Code Conventions

### Python (backend)
- Type annotations on all functions
- Async handlers and DB operations
- Ruff for linting (`uv run ruff check .`)
- Pydantic v2 models with `model_config = {"from_attributes": True}`
- Config via pydantic-settings, never hardcode secrets
- Add deps with `uv add <package>`, commit `uv.lock`

### TypeScript (frontend)
- Functional components with typed props interfaces
- Tailwind utility classes, no custom CSS
- No `any` types
- `fetch` for API calls to `/api/*`
- Mobile-first responsive design (sm → md → lg)

### API
- RESTful, all routes under `/api`
- Nginx strips `/api` prefix before forwarding to FastAPI
- FastAPI `root_path="/api"` for OpenAPI docs

## Demos

Each demo lives in `demos/<name>/` with its own `pyproject.toml` managed by `uv`.

### Key Commands
- Install deps: `cd demos/<name> && uv sync`
- Run locally: `cd demos/<name> && uv run streamlit run app.py`
- Run tests: `cd demos/<name> && uv sync --group dev && uv run pytest tests/ -v`

### Architecture
- Streamlit apps proxied through Nginx with `--server.baseUrlPath=/demo/<name>`
- Each demo gets a systemd service (`deploy/systemd/portfolio-demo-<name>.service`)
- Model artifacts tracked via Git LFS (`.onnx` files — see `.gitattributes`)
- Nginx requires WebSocket upgrade headers for Streamlit

### Current Demos
| Demo | Port | Route | Status |
|------|------|-------|--------|
| Text OCR | 8502 | /demo/ocr | Active |
| EEG Generator | 8501 | /demo/eeg | Planned |
| Medical Chatbot | 8503 | /demo/chatbot | Planned |
| Bomberman RL | 8504 | /demo/bomberman | Planned |

## Key Files

- `backend/portfolio_api/main.py` — FastAPI app
- `frontend/src/App.tsx` — React router and layout
- `deploy/nginx/portfolio.conf` — Nginx site config
- `backend/portfolio_api/config.py` — All configuration
- `deploy/scripts/deploy.sh` — Deployment script

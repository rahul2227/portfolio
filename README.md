# Portfolio

A self-hosted portfolio and interactive ML demo platform running on a Raspberry Pi 4. Visitors browse projects, read about the tech stack, and interact with live machine-learning demos -- all served from a credit-card-sized computer behind a Cloudflare Tunnel.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite 7 + TypeScript + Tailwind CSS 4 |
| Backend | FastAPI + async SQLAlchemy + aiosqlite (SQLite) |
| Infrastructure | Nginx reverse proxy + systemd services + cloudflared tunnel |
| Python tooling | `uv` (not pip) |
| Node tooling | `npm` |
| Server | Raspberry Pi 4 (4 GB RAM), Debian 13 Trixie, aarch64 |

## Architecture

```
Internet
  Visitor --> Cloudflare Tunnel (free SSL, CDN, DDoS protection)
                    |
                    v  (secure outbound tunnel, no inbound ports)
            Raspberry Pi 4
            +--------------------------+
            |  Nginx (port 80)         |
            |    /         -> frontend/dist (React SPA)
            |    /api/*    -> FastAPI :8000
            |    /demo/*   -> Streamlit apps :8501-8504
            +--------------------------+
            |  FastAPI backend         |
            |    /health, /projects, /contact
            |    SQLite + Redis cache
            +--------------------------+
            |  ML demos (Streamlit)    |
            |    EEG Generator, Medical Chatbot,
            |    Text OCR, Bomberman RL
            +--------------------------+
            |  systemd manages all     |
            |  services automatically  |
            +--------------------------+
```

## Directory Structure

```
portfolio/
  backend/
    portfolio_api/          FastAPI application
      main.py               App entry-point (root_path="/api")
      config.py             pydantic-settings (PORTFOLIO_ prefix)
      database.py           Async SQLAlchemy engine + session
      routers/              health.py, projects.py, contact.py
      models/               SQLAlchemy ORM models
      schemas/              Pydantic v2 request/response schemas
      seed.py               Load seed.json into database
    data/                   seed.json (committed), portfolio.db (gitignored)
  frontend/
    src/                    React SPA source
      App.tsx               Router and layout
      components/           Reusable UI components
      pages/                Route-level page components
      assets/               Static assets (images, SVGs)
    dist/                   Production build output (gitignored)
  deploy/
    nginx/                  portfolio.conf — Nginx site config
    systemd/                portfolio-backend.service, cloudflared-portfolio.service
    scripts/                deploy.sh — one-command deployment
  demos/                    Interactive ML demo apps (future)
  CLAUDE.md                 Claude Code project instructions
  .claude/                  Claude Code rules, agents, skills, hooks
```

## Laptop Development Setup

### Prerequisites

- **Node.js 20+** (for the frontend)
- **Python 3.13+** (for the backend)
- **uv** (Python package manager) -- install with `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Backend

```bash
cd backend

# Install Python dependencies (creates .venv automatically)
uv sync

# Start the dev server with hot-reload
uv run uvicorn portfolio_api.main:app --reload --port 8000

# Seed the database with sample projects
uv run python -m portfolio_api.seed

# Run linter
uv run ruff check .
```

The backend will be available at `http://localhost:8000`. API docs are at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend

# Install Node dependencies
npm install

# Start the Vite dev server (proxies /api requests to :8000)
npm run dev

# Run linter
npm run lint
```

The frontend dev server will be available at `http://localhost:5173`. The Vite config automatically proxies all `/api/*` requests to the backend on port 8000, so both servers should be running during development.

### Seed Database

Populate the SQLite database with project data from `backend/data/seed.json`:

```bash
cd backend && uv run python -m portfolio_api.seed
```

## Pi Deployment Setup

### System Packages

Ensure the following are installed on the Raspberry Pi:

```bash
sudo apt update && sudo apt install -y nginx redis-server
# Install Node.js 20+ via nvm or NodeSource
# Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# Install cloudflared: see https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
```

### Deploy

Run the deployment script from the repository root:

```bash
bash deploy/scripts/deploy.sh
```

This script will:
1. Pull the latest code from `origin main` (if a remote is configured)
2. Install frontend dependencies and build the production bundle
3. Sync backend Python dependencies with `uv sync --frozen`
4. Copy systemd service files to `/etc/systemd/system/` if they have changed
5. Restart the backend and reload Nginx
6. Run health checks against both the backend and frontend

### Manual Setup (first time only)

Symlink the Nginx site config:

```bash
sudo ln -sf /home/rahser/portfolio/deploy/nginx/portfolio.conf /etc/nginx/sites-enabled/portfolio
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

Copy and enable the systemd services:

```bash
sudo cp deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now portfolio-backend
sudo systemctl enable --now cloudflared-portfolio
```

### Get the Public URL

The cloudflared quick-tunnel service generates a random `trycloudflare.com` URL on each start. To find the current URL:

```bash
journalctl -u cloudflared-portfolio --no-pager -n 50 | grep -o 'https://.*trycloudflare.com' | tail -1
```

For a permanent custom domain, configure a named Cloudflare Tunnel with your own domain (e.g. `rahulsharma.dev`).

## Environment Variables

All backend configuration uses the `PORTFOLIO_` prefix and can be set via environment variables or a `.env` file in the backend directory.

| Variable | Default | Description |
|----------|---------|-------------|
| `PORTFOLIO_DEBUG` | `false` | Enable FastAPI debug mode |
| `PORTFOLIO_DATABASE_URL` | `sqlite+aiosqlite:///...backend/data/portfolio.db` | SQLAlchemy database URL |
| `PORTFOLIO_REDIS_URL` | `redis://127.0.0.1:6379/0` | Redis connection URL |
| `PORTFOLIO_CONTACT_RATE_LIMIT` | `5` | Max contact form submissions per hour |

## Claude Code Skills

This project includes several Claude Code slash commands for common operations:

| Command | Description |
|---------|-------------|
| `/deploy` | Build frontend, sync backend deps, restart services, and run health checks |
| `/test` | Run the full test suite (pytest + vitest) and lint checks, then summarize results |
| `/seed-db` | Seed the SQLite database from `seed.json`. Pass `reset` to drop and recreate tables first |
| `/status` | Check health of all services, system resources (RAM, disk, CPU temp), and show the public tunnel URL |

## License

Private project. All rights reserved.

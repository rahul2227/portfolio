---
name: deploy
description: "Deploy the portfolio app. Usage: /deploy <target> [mode]. Targets: pi (production), local (dev/test). Modes: dev (default for local), prod."
allowed-tools: Bash
---

Deploy the portfolio application. Target is required — no auto-detection.

## Usage

```
/deploy <target> [mode]
```

| Command               | Behavior                                                    |
|-----------------------|-------------------------------------------------------------|
| `/deploy pi`          | Production deploy on Raspberry Pi (systemd, nginx, tunnel)  |
| `/deploy local`       | Local dev servers with hot reload (Vite + uvicorn --reload) |
| `/deploy local prod`  | Local production-like build (no HMR, built frontend)        |

If no target is provided, ask the user which target they want.

---

## Target: `pi` — Production Deploy

Must be run while SSH'd into the Raspberry Pi. Runs the existing deploy script.

### Steps

1. **Verify we are on the Pi**:
   ```bash
   if [[ "$(hostname)" != "rpi"* && "$(uname -m)" != "aarch64" ]]; then
     echo "ERROR: This does not appear to be the Raspberry Pi. Run /deploy local instead."
     exit 1
   fi
   ```
   If the check fails, stop and tell the user.

2. **Run the deploy script**:
   ```bash
   bash deploy/scripts/deploy.sh
   ```
   The script handles: git pull, frontend build, backend + demo dep sync, systemd unit copy, service restarts, and health checks.

3. **Report the public URL**:
   ```bash
   journalctl -u cloudflared-portfolio --no-pager -n 50 | grep -o 'https://.*trycloudflare.com' | tail -1
   ```

4. Report success or failure. If any step fails, stop and report the error.

---

## Target: `local` — Local Dev Deploy (default mode: dev)

Starts all services in the foreground with interleaved logs. Intended for testing on MacBook.

### Steps

1. **Install/sync dependencies** — run these in parallel:
   ```bash
   cd frontend && npm install
   ```
   ```bash
   cd backend && uv sync
   ```
   ```bash
   cd demos/text-ocr && uv sync
   ```

2. **Start all services in foreground** using a single bash command that runs all processes and interleaves their output. Use trap to clean up all child processes on exit:
   ```bash
   trap 'kill 0' EXIT

   # Frontend — Vite dev server with HMR
   (cd frontend && npm run dev 2>&1 | sed 's/^/[frontend] /') &

   # Backend — FastAPI with auto-reload
   (cd backend && uv run uvicorn portfolio_api.main:app --reload --port 8000 2>&1 | sed 's/^/[backend]  /') &

   # OCR Demo — Streamlit
   (cd demos/text-ocr && uv run streamlit run app.py --server.port 8502 --server.baseUrlPath /demo/ocr --server.headless true 2>&1 | sed 's/^/[ocr-demo] /') &

   wait
   ```

3. **Print service URLs** before starting:
   ```
   Frontend:  http://localhost:5173
   Backend:   http://localhost:8000
   API Docs:  http://localhost:8000/docs
   OCR Demo:  http://localhost:8502/demo/ocr
   ```

4. Note to the user: Press Ctrl+C to stop all services.

---

## Target: `local prod` — Local Production-Like Deploy

Builds frontend for production and runs services without hot reload. Foreground with logs.

### Steps

1. **Install/sync dependencies** — run these in parallel:
   ```bash
   cd frontend && npm ci
   ```
   ```bash
   cd backend && uv sync --frozen
   ```
   ```bash
   cd demos/text-ocr && uv sync --frozen
   ```

2. **Build frontend**:
   ```bash
   cd frontend && npm run build
   ```

3. **Start all services in foreground**:
   ```bash
   trap 'kill 0' EXIT

   # Backend — FastAPI production mode (no reload)
   (cd backend && uv run uvicorn portfolio_api.main:app --port 8000 2>&1 | sed 's/^/[backend]  /') &

   # OCR Demo — Streamlit
   (cd demos/text-ocr && uv run streamlit run app.py --server.port 8502 --server.baseUrlPath /demo/ocr --server.headless true 2>&1 | sed 's/^/[ocr-demo] /') &

   # Frontend — serve built dist/ with a simple static server
   (cd frontend && npx serve dist -l 5173 -s 2>&1 | sed 's/^/[frontend] /') &

   wait
   ```

4. **Print service URLs** before starting:
   ```
   Frontend:  http://localhost:5173 (production build)
   Backend:   http://localhost:8000
   API Docs:  http://localhost:8000/docs
   OCR Demo:  http://localhost:8502/demo/ocr
   ```

5. Note to the user: Press Ctrl+C to stop all services.

---

## Guidelines

- Target is **required**. If omitted, ask the user: "Which target? `pi` or `local`"
- For `local` mode, default to `dev` if no mode argument is given
- Always print the service URLs before streaming logs so the user knows where to look
- If a dependency install fails, stop and report the error — do not start services with broken deps
- For `pi` target, delegate to `deploy/scripts/deploy.sh` which handles all production logic
- When new demos are added to the project, add them to both local deploy modes (dev and prod)

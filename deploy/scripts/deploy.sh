#!/usr/bin/env bash
# deploy.sh — Build and deploy the portfolio on the Raspberry Pi
# Usage: bash deploy/scripts/deploy.sh
#
# Steps:
#   1. Pull latest code (if git remote configured)
#   2. Build frontend (npm ci + npm run build)
#   3. Sync backend Python deps (uv sync --frozen)
#   4. Sync OCR demo Python deps (uv sync --frozen)
#   5. Copy systemd unit files if changed, daemon-reload
#   6. Restart backend + OCR demo + reload Nginx
#   7. Health-check backend, OCR demo, and frontend

set -euo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FRONTEND_DIR="${REPO_DIR}/frontend"
BACKEND_DIR="${REPO_DIR}/backend"
SYSTEMD_SRC="${REPO_DIR}/deploy/systemd"
SYSTEMD_DEST="/etc/systemd/system"

# ── Colours (disabled when stdout is not a terminal) ─────────────────────────
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    CYAN='\033[0;36m'
    NC='\033[0m'  # No Colour
else
    GREEN='' RED='' YELLOW='' CYAN='' NC=''
fi

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; exit 1; }

# ── Step 1: Pull latest code ────────────────────────────────────────────────
info "Step 1/7 — Pulling latest code"
cd "${REPO_DIR}"
if git remote get-url origin &>/dev/null; then
    git pull origin main
    ok "git pull complete"
else
    warn "No git remote 'origin' configured — skipping pull"
fi

# ── Step 2: Build frontend ──────────────────────────────────────────────────
info "Step 2/7 — Building frontend"
cd "${FRONTEND_DIR}"
npm ci --prefer-offline
npm run build
ok "Frontend built -> ${FRONTEND_DIR}/dist"

# ── Step 3: Sync backend dependencies ────────────────────────────────────────
info "Step 3/7 — Syncing backend Python dependencies"
cd "${BACKEND_DIR}"
uv sync --frozen
ok "Backend dependencies synced"

# ── Step 4: Sync OCR demo dependencies ───────────────────────────────────────
info "Step 4/7 — Syncing OCR demo Python dependencies"
cd "${REPO_DIR}/demos/text-ocr"
uv sync --frozen
ok "OCR demo dependencies synced"

# ── Step 5: Copy systemd unit files if changed ──────────────────────────────
info "Step 5/7 — Checking systemd unit files"
NEED_RELOAD=false
for unit_file in "${SYSTEMD_SRC}"/*.service; do
    unit_name="$(basename "${unit_file}")"
    dest="${SYSTEMD_DEST}/${unit_name}"
    if [[ ! -f "${dest}" ]] || ! diff -q "${unit_file}" "${dest}" &>/dev/null; then
        info "  Copying ${unit_name} -> ${SYSTEMD_DEST}/"
        sudo cp "${unit_file}" "${dest}"
        NEED_RELOAD=true
    fi
done
if [[ "${NEED_RELOAD}" == "true" ]]; then
    sudo systemctl daemon-reload
    ok "systemd units updated and daemon reloaded"
else
    ok "systemd units unchanged — no reload needed"
fi

# ── Step 6: Restart services ────────────────────────────────────────────────
info "Step 6/7 — Restarting services"
sudo systemctl restart portfolio-backend
ok "portfolio-backend restarted"

# Restart OCR demo; use 'enable --now' on first deploy in case the unit is new
sudo systemctl restart portfolio-demo-ocr
ok "portfolio-demo-ocr restarted"

sudo systemctl reload nginx
ok "nginx reloaded"

# ── Step 7: Health checks ───────────────────────────────────────────────────
info "Step 7/7 — Running health checks"
HEALTH_OK=true

# Give services a moment to start — OCR model load can take a few seconds on Pi
sleep 3

# Backend health check
if curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
    ok "Backend health check passed (http://127.0.0.1:8000/health)"
else
    warn "Backend health check failed — retrying in 3 seconds..."
    sleep 3
    if curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
        ok "Backend health check passed on retry"
    else
        echo -e "${RED}[FAIL]${NC}  Backend is not responding on port 8000"
        HEALTH_OK=false
    fi
fi

# OCR demo health check — Streamlit exposes /_stcore/health when ready
if curl -sf http://127.0.0.1:8502/_stcore/health >/dev/null 2>&1; then
    ok "OCR demo health check passed (http://127.0.0.1:8502/_stcore/health)"
else
    warn "OCR demo health check failed — retrying in 5 seconds (model load is slow on Pi)..."
    sleep 5
    if curl -sf http://127.0.0.1:8502/_stcore/health >/dev/null 2>&1; then
        ok "OCR demo health check passed on retry"
    else
        echo -e "${RED}[FAIL]${NC}  OCR demo is not responding on port 8502"
        HEALTH_OK=false
    fi
fi

# Frontend health check (via Nginx)
if curl -sf http://localhost/ >/dev/null 2>&1; then
    ok "Frontend health check passed (http://localhost/)"
else
    echo -e "${RED}[FAIL]${NC}  Frontend/Nginx is not responding on port 80"
    HEALTH_OK=false
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
if [[ "${HEALTH_OK}" == "true" ]]; then
    ok "Deploy complete — all services healthy"
else
    fail "Deploy finished but one or more health checks failed. Check logs with: journalctl -u portfolio-backend -n 30 OR journalctl -u portfolio-demo-ocr -n 30"
fi

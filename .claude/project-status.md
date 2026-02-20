# Project Status

## Current Phase: Phase 3 — EEG Signal Generator (next)

## Completed

### Phase 0 — Pi Foundation
- [x] Raspberry Pi OS Lite 64-bit flashed
- [x] SSH, static local IP, packages configured
- [x] Python 3.11+, Node.js, Nginx installed
- [x] Cloudflare account + tunnel (trycloudflare.com, no custom domain yet)
- [x] HTTPS verified end-to-end
- [x] Deploy script (`deploy/scripts/deploy.sh`) working

### Phase 1 — Portfolio Shell
- [x] React + Vite + TypeScript + Tailwind frontend
  - Landing page with hero section
  - Projects grid with tag filtering
  - About page
  - Contact form (POST /api/contact)
  - "Powered by Raspberry Pi 4" footer badge
- [x] FastAPI backend with routers: health, projects, contact
- [x] Async SQLAlchemy + aiosqlite + seed.json (8 projects)
- [x] Nginx reverse proxy configured
- [x] systemd services: portfolio-backend, cloudflared-portfolio
- [x] Claude Code agents, skills, hooks, and rules set up

### Phase 2 — Text OCR Demo
- [x] ONNX export script (`demos/text-ocr/scripts/export_onnx.py`)
  - CNN + BiLSTM + CTC model exported to ONNX opset 17 with dynamic axes
  - INT8 quantization: 46 MB → 11.6 MB
  - Validation: PyTorch vs ONNX output parity confirmed (max diff < 0.00004)
- [x] Inference wrapper (`demos/text-ocr/model.py`)
  - Preprocessing: grayscale → resize height 128 → pad/cap width 2048 → normalize
  - Greedy CTC decode with per-character confidence extraction
  - Fixed bugs in original evaluation.py (no duplicate collapse, no blank removal)
- [x] Streamlit app (`demos/text-ocr/app.py`)
  - 3 tabs: Upload, Draw (canvas), Try Samples
  - Sidebar model card with CTC explanation and limitations
  - Per-character confidence visualization (green/yellow/red)
  - Preprocessing pipeline visualization
- [x] 18 passing tests (test_model.py + test_app.py)
- [x] Infrastructure: nginx WebSocket proxy, systemd service, deploy script
- [x] Git LFS for .onnx model files
- [x] seed.json updated with accurate project description
- [x] CLAUDE.md updated with Demos section

**Key Decisions:**
- ONNX INT8 quantization — 4x smaller, acceptable accuracy for demo
- Line recognition only — honest about capabilities (no text detection)
- Legacy torch ONNX exporter (`dynamo=False`) — dynamo has LSTM dynamic shape issues
- `dependency-groups` in pyproject.toml — uv convention (not `project.optional-dependencies`)
- Padding to max_width=2048 — matches original training pipeline

## Not Yet Built
- No project detail pages (`/projects/:slug`)
- No rate limiting
- No project images (`image_url` all null)
- No GitHub URLs in seed data
- Redis configured but not used

## Planned
- Phase 3: EEG Signal Generator (port 8501, /demo/eeg)
- Phase 4: Medical Chatbot (port 8503, /demo/chatbot)
- Phase 5: Bomberman RL (port 8504, /demo/bomberman)
- Phase 6: Tier 2 Projects + Polish
- Phase 7: Production Hardening

## Source Repos (for reference when building demos)
Clone these into a sibling `project-refs/` directory for context:
- `Text_OCR` → demos/text-ocr
- `Generative-EEG-Augmentation` → demos/eeg-generator
- `Medical-chatbot` → demos/medical-chatbot
- `bomberman_game` + `bomberman_rl_RBN` → demos/bomberman-rl

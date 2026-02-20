# Portfolio Implementation Plan — Phases 2-7

## Context

The portfolio shell (Phase 1) is built: React SPA with 4 routes, FastAPI with 3 endpoints, deploy configs ready. The frontend works but looks generic (white/light theme, no project images, placeholder content). The goal is to transform this into an aesthetically pleasing portfolio with live ML inference demos, all running on a Raspberry Pi 4 (4GB).

**Key architectural decision**: All demos will be React pages calling FastAPI inference endpoints — no Streamlit. This avoids running 4 extra processes (~200MB each), keeps a unified look, and simplifies the Pi's resource budget.

---

## Phase 2: Portfolio Shell — Make It Beautiful

### 2.1 Fixes & Setup
- **`frontend/index.html`** — Change `<title>` from "frontend" to "Rahul Sharma | AI/ML Engineer", add meta description
- **`frontend/package.json`** — `npm install @tailwindcss/typography` (prose classes used in About.tsx but plugin missing)
- **`frontend/src/index.css`** — Configure dark theme via Tailwind v4 `@theme` directive + `@plugin "@tailwindcss/typography"`:
  - Near-black backgrounds (#0a0a0f / #12121a / #1a1a2e)
  - Zinc text (#e4e4e7 primary, #a1a1aa secondary)
  - Indigo accent (#6366f1), emerald for "live" indicators (#34d399)
  - Set `body` base styles in `@layer base`

### 2.2 Dark Theme Conversion (all existing components)
Every file in `frontend/src/components/` and `frontend/src/pages/` — swap light classes to dark palette:
- `Navbar.tsx` — bg-bg-primary/80 backdrop-blur, border-border, accent links
- `HeroSection.tsx` — text-text-primary/secondary, accent CTA buttons
- `ProjectCard.tsx` — border-border, hover:border-accent/50, accent tag pills, **wrap card in `<Link to={/projects/${slug}>}`**
- `Footer.tsx` — dark bg, pulsing green dot on "Raspberry Pi 4" badge
- `ContactForm.tsx` — dark inputs (bg-bg-secondary border-border), accent focus rings
- `Home.tsx` — dark skills grid, **add "Featured Projects" section** showing Tier-1 cards
- `Projects.tsx` — dark tag filter, Tier-1 cards get gradient top border + "Live Demo" badge
- `About.tsx` — rewrite with education/experience timeline, use `prose-invert`
- `Contact.tsx` — dark container

### 2.3 New Frontend Files
| File | Purpose |
|------|---------|
| `frontend/src/pages/ProjectDetail.tsx` | Route `/projects/:slug` — fetches `GET /api/projects/{slug}`, renders full description, architecture images, results, "Try Demo" button for Tier-1 |
| `frontend/src/pages/NotFound.tsx` | 404 catch-all route |
| `frontend/src/hooks/useDocumentTitle.ts` | Sets `document.title` per page |
| `frontend/src/components/FeaturedProjectCard.tsx` | Larger card variant for Home page featured section |

### 2.4 Backend Changes
- **`backend/portfolio_api/models/project.py`** — Add columns: `long_description` (Text, nullable), `architecture_image_url`, `results_image_url`
- **`backend/portfolio_api/schemas/project.py`** — Add `ProjectDetailResponse` extending `ProjectResponse` with new fields
- **`backend/portfolio_api/routers/projects.py`** — Add `GET /projects/{slug}` endpoint (returns 404 if not found)
- **`backend/portfolio_api/main.py`** — Mount static files: `app.mount("/static", StaticFiles(directory="static"))`
- **`backend/data/seed.json`** — Fill real github_urls, long_descriptions, image URLs
- **`backend/static/images/projects/`** — Copy architecture diagrams from project_refs

### 2.5 Route Updates
**`frontend/src/App.tsx`** — Add:
```
/projects/:slug  → ProjectDetail
/demo/ocr        → OCRDemo (Phase 3)
/demo/eeg        → EEGDemo (Phase 4)
/demo/chatbot    → ChatbotDemo (Phase 5)
/demo/bomberman  → BombermanDemo (Phase 6)
*                → NotFound
```

### 2.6 Nginx
- **`deploy/nginx/portfolio.conf`** — Add `client_max_body_size 5m`, increase `proxy_read_timeout 60s`, add `/api/static/` location block

---

## Phase 3: Text OCR Demo (most visual, simplest to deploy)

### 3.1 Model Prep (offline, on dev machine)
- Create `backend/demos/ocr/export_onnx.py` — loads `OCRModel` from `project_refs/Text_OCR/ocr_lstm_model.pth`, exports to ONNX with dynamic width axis
- Architecture: CNN (1→64→128→256→512) + BiLSTM + CTC — defined in `project_refs/Text_OCR/models/`
- Character mapping from `project_refs/Text_OCR/data_preprocessing/mappings_LSTM.json`
- Output: `backend/data/models/ocr_lstm.onnx` (~15-20MB), `backend/data/models/ocr_mappings.json`

### 3.2 Backend
| File | Purpose |
|------|---------|
| `backend/portfolio_api/routers/demo_ocr.py` | `POST /demo/ocr/infer` — accepts image upload, returns extracted text |
| `backend/portfolio_api/schemas/demo_ocr.py` | `OCRResult`: text, confidence, inference_time_ms |
| `backend/portfolio_api/services/ocr_service.py` | Lazy-load ONNX session, preprocess image (grayscale→resize h=64→normalize→pad), CTC decode |
| `backend/portfolio_api/middleware/rate_limit.py` | In-memory sliding window rate limiter (no Redis needed), 10 req/min/IP for demos |

Dependencies to add: `uv add onnxruntime pillow python-multipart`

### 3.3 Frontend
| File | Purpose |
|------|---------|
| `frontend/src/pages/demos/OCRDemo.tsx` | Upload area + sample images → shows original image + extracted text + confidence + timing |
| `frontend/src/components/demos/ImageDropZone.tsx` | Reusable drag-and-drop file upload component |
| `frontend/src/components/demos/DemoLayout.tsx` | Shared wrapper for all demo pages (header, back nav, project link) |
| `frontend/public/samples/ocr/` | 3 handwriting sample images (~50KB each) |

---

## Phase 4: EEG Signal Generator Demo (signature project)

### 4.1 Model Prep (offline)
- Create `backend/demos/eeg/export_onnx.py` — loads `EEGGenerator` from `project_refs/Generative-EEG-Augmentation/`
- Generator: latent_dim=100, 63 channels, 1001 time samples, 2 classes (CWGAN-GP)
- Checkpoint: `exploratory notebooks/models/best_generator.pth` (13.9MB)
- Output: `backend/data/models/eeg_generator.onnx` (~5-6MB)
- Pre-compute 2-3 reference "real EEG" waveforms as JSON in `backend/data/eeg_reference/`

### 4.2 Backend
| File | Purpose |
|------|---------|
| `backend/portfolio_api/routers/demo_eeg.py` | `POST /demo/eeg/generate` (params: label, num_channels, seed) + `GET /demo/eeg/reference/{label}` |
| `backend/portfolio_api/schemas/demo_eeg.py` | Request/response with channel data as `list[list[float]]` |
| `backend/portfolio_api/services/eeg_service.py` | Lazy-load ONNX, generate noise vector, run inference, select channel subset |

### 4.3 Frontend
| File | Purpose |
|------|---------|
| `frontend/src/pages/demos/EEGDemo.tsx` | Controls (class selector, channel slider, seed) → multi-channel waveform visualization + "Compare with Real EEG" toggle |
| `frontend/src/components/demos/EEGWaveformChart.tsx` | Canvas/SVG stacked time-series chart (8 channels x 1001 points, dark bg, colored lines) |

---

## Phase 5: Medical Research Search Demo

### Architecture Decision
Original project uses external ChromaDB + OpenAI API — not feasible on standalone Pi. **Approach: retrieval-only semantic search** over pre-indexed PubMed abstracts.

### 5.1 Data Prep (offline)
- Create `backend/demos/chatbot/prepare_embeddings.py`:
  - Load PubMed abstracts from `project_refs/Medical-chatbot/lib/backend/data/`
  - Embed ~1000 abstracts with `all-MiniLM-L6-v2`
  - Build FAISS index
  - Output: `backend/data/models/chatbot_embeddings.npy`, `chatbot_passages.json`, `chatbot_faiss.index`, `minilm_l6_v2.onnx` (~22MB), tokenizer files

### 5.2 Backend
| File | Purpose |
|------|---------|
| `backend/portfolio_api/routers/demo_chatbot.py` | `POST /demo/chatbot/query` + `GET /demo/chatbot/examples` |
| `backend/portfolio_api/schemas/demo_chatbot.py` | Query/response with retrieved passages, similarity scores, PubMed metadata |
| `backend/portfolio_api/services/chatbot_service.py` | Lazy-load MiniLM ONNX + FAISS index, embed query → search → return top-5 |

Dependencies: `uv add faiss-cpu tokenizers`

### 5.3 Frontend
| File | Purpose |
|------|---------|
| `frontend/src/pages/demos/ChatbotDemo.tsx` | Search bar + example question pills → result cards with highlighted passages, paper title, PubMed link, similarity score |

Framed as "Medical Research Search" (honest about retrieval-only, no LLM generation).

---

## Phase 6: Bomberman RL Demo

### Architecture Decision
Running the pygame game engine per request is wasteful. **Approach: pre-record episodes offline, replay in browser via Canvas.**

### 6.1 Episode Recording (offline)
- Create `backend/demos/bomberman/record_episodes.py` — runs game with trained Servus DQN agent, serializes each step as JSON
- Output: 5-10 episodes in `backend/data/demos/bomberman/episodes/` (~80KB each)
- Copy sprite PNGs from `project_refs/bomberman_rl_RBN/assets/` to `frontend/public/sprites/bomberman/`

### 6.2 Backend
| File | Purpose |
|------|---------|
| `backend/portfolio_api/routers/demo_bomberman.py` | `GET /demo/bomberman/episodes` (list) + `GET /demo/bomberman/episodes/{id}` (full episode JSON) |

Zero inference — just static JSON serving.

### 6.3 Frontend
| File | Purpose |
|------|---------|
| `frontend/src/pages/demos/BombermanDemo.tsx` | Episode selector → canvas game replay with play/pause/speed controls + stats overlay |
| `frontend/src/components/demos/BombermanRenderer.tsx` | Canvas renderer: 17x17 grid, 32x32 tiles, requestAnimationFrame playback with sprites |

---

## Phase 7: Polish & Hardening

- **Tier 2 project pages** — Update `seed.json` with real content for all 8 projects
- **Rate limiting** — Apply to all demo endpoints (10-30 req/min/IP depending on cost), add Nginx `limit_req_zone` as second layer
- **Health endpoint** — Extend with memory usage (psutil), CPU temp, disk, loaded models
- **Analytics** — Simple `DemoUsage` model tracking demo name, timestamp, IP hash
- **Error handling** — Global FastAPI exception handler, 503 for failed model loads
- **CORS** — Tighten to production domain only
- **SEO** — Per-page meta tags, Open Graph for project pages, sitemap.xml

---

## Pi 4 Memory Budget (4GB)

| Component | RAM |
|-----------|-----|
| OS + system | ~400MB |
| Nginx + cloudflared | ~40MB |
| uvicorn (2 workers) base | ~120MB |
| OCR ONNX model | ~100MB |
| EEG Generator ONNX | ~30MB |
| MiniLM + FAISS | ~50MB |
| Inference peak | ~200MB |
| **Total estimated** | **~940MB** |
| **Headroom** | **~3GB** |

Models are lazy-loaded (only on first request). Idle usage is ~560MB.

---

## Design Palette Reference

```
Backgrounds:  #0a0a0f (primary) / #12121a (cards) / #1a1a2e (hover)
Borders:      #2a2a3e
Text:         #e4e4e7 (primary) / #a1a1aa (secondary)
Accent:       #6366f1 (indigo) / #818cf8 (hover)
Live badge:   #34d399 (emerald)
Highlights:   #fbbf24 (amber tags)
```

---

## Verification Plan

1. **Phase 2**: `npm run dev` — all pages dark theme, project detail loads, 404 works, contact submits, linters pass
2. **Phase 3**: Upload handwriting → get OCR text + timing. Rate limit returns 429 after 10 rapid requests.
3. **Phase 4**: Generate EEG → waveform chart renders. Compare with real → side-by-side.
4. **Phase 5**: Search "epilepsy treatment" → relevant PubMed passages returned.
5. **Phase 6**: Select episode → watch agent play with controls.
6. **Phase 7**: Rate limits work, health endpoint shows system stats, CORS rejects unauthorized origins.
7. **Full integration**: `npm run build` → nginx serves SPA → all routes work.

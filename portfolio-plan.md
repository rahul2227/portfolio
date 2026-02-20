# 🏗️ Raspberry Pi Portfolio — Master Plan

## 1. Project Selection & Tiering

After reviewing all your repos, here's my recommendation. The goal is to tell a **coherent story**: *"I'm an AI/ML engineer with deep neuroscience domain expertise, strong CV/NLP skills, and I can deploy models end-to-end."*

### 🌟 Tier 1 — Hero Projects (Interactive demos on Pi)
These get full interactive experiences where visitors can play with the model.

| # | Project | Why | Interactive Demo Idea |
|---|---------|-----|----------------------|
| 1 | **Generative-EEG-Augmentation** | Thesis-adjacent, cutting-edge generative models (GANs, VAEs, Diffusion) for EEG. Unique domain. | Streamlit app: pick a generative model → generate synthetic EEG → visualize waveforms side-by-side with real data. Sliders for noise, channels, etc. |
| 2 | **Medical-chatbot** | Shows NLP + domain expertise (PubMed/neuroscience). Very demonstrable. | Chat interface: visitor types a neuroscience question → gets an answer. Use a quantized small LLM or distilled model on Pi. |
| 3 | **Text_OCR** | CV is immediately visual and impressive. | Upload/drag an image of distorted text → Pi runs OCR → returns extracted text with confidence scores + bounding boxes overlay. |
| 4 | **bomberman_game + bomberman_rl_RBN** | RL is fun and visual. Combine both into one showcase. | Browser-rendered Bomberman game. Visitor watches the trained RL agent play, or selects between different training checkpoints to see learning progression. |

### 📦 Tier 2 — Polished Showcases (Great README + static results, light interactivity)
These get well-documented pages with results, architecture diagrams, and maybe a "try a pre-computed example" feature.

| # | Project | Why | Showcase Approach |
|---|---------|-----|-------------------|
| 5 | **data_sanitization_pipeline** | Shows MLOps maturity — recruiters love pipeline thinking. | Architecture diagram, sample before/after data, metrics dashboard. |
| 6 | **Optimized-BCI** | Strong neuroscience + ML, has a fork already. | Detailed results page with confusion matrices, ROC curves, channel importance maps. |
| 7 | **ComputerVision-24** | Rounds out CV skills beyond OCR. | Gallery of results with model comparison. |
| 8 | **Blockchain_for_user_auth** *(optional)* | 6 stars, shows systems/security thinking. Different domain = breadth. | Architecture diagram + demo flow explanation. Only include if you want to show breadth beyond ML. |

### 🗑️ Skip / Archive / Keep Private
| Category | Repos | Reason |
|----------|-------|--------|
| **Forked reference repos** | PythonDataScienceHandbook, awesome-neuroscience, awesome-public-datasets, Deep-Learning-Papers-Reading-Roadmap, BCI-Competition-EEG-signal-Classification, awesome-blockchain, lepard, Vesper, hackerrank-solutions, simple-blockchain | Not original work — clutters your profile |
| **Tutorial-level ML** | titanic_analysis, Credit_card_fraud_detection, Regression-miles-per-galon-1970, Image_Augmentation, models_for_image_classification, Recommendation_system | Too basic for a Master's graduate portfolio |
| **Mobile/Flutter/Dart** | Sociality, vSplit, SandBox, Care_Research, Medic-Meditation-App, Flutter-Learning-Applications, Auto_route_Practice, Swift-Learning, CellioApp | Not relevant to your AI/ML positioning |
| **Old blockchain** | BLOCKCHAIN-COMPLETE-, SIMPLE_BLOCKCHAIN_CPP, Backend-for-secure-chat-channel | Dated, distracts from ML narrative |
| **Course assignments** | GNN-Assignments-23, Advance-Practical-GTF (all variants), advanced-practical-legecy-code | Keep private, not portfolio material |
| **Misc** | Abhi-s, REsources, Planets, rahul2227 (personal repo), phont-challenge, End-to-End-ML, Rahul-sharma_40_2012610 | Clean up or archive |

> **Special note on Thesis-EEG**: This is your strongest work but it's private. Consider extracting a public-facing version with key results (without proprietary data) as part of the portfolio narrative. Your thesis story ties Tier 1 projects together.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VISITOR'S BROWSER                        │
│  Portfolio SPA (React/Vite)  ←→  Streamlit iframes/links   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS (443)
                       ▼
              ┌────────────────┐
              │   Cloudflare   │  ← Free tier: DNS, CDN,
              │    Tunnel      │     DDoS protection, SSL
              └────────┬───────┘
                       │ Secure tunnel (no port forwarding!)
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   RASPBERRY PI 4                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                    Nginx (reverse proxy)              │    │
│  │  /           → Frontend static files                 │    │
│  │  /api/*      → FastAPI backend (:8000)               │    │
│  │  /demo/eeg   → Streamlit EEG app (:8501)             │    │
│  │  /demo/ocr   → Streamlit OCR app (:8502)             │    │
│  │  /demo/chat  → Streamlit Chat app (:8503)            │    │
│  │  /demo/rl    → Streamlit RL viz (:8504)              │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────┐  ┌────────────────────────────────────┐     │
│  │   FastAPI    │  │     Streamlit Apps (per project)   │     │
│  │   Backend    │  │                                    │     │
│  │             │  │  EEG Generator  │  Medical Chat    │     │
│  │  - Project  │  │  Text OCR       │  Bomberman RL    │     │
│  │    metadata │  │                                    │     │
│  │  - Contact  │  └────────────────────────────────────┘     │
│  │    form     │                                             │
│  │  - Analytics│  ┌────────────────────────────────────┐     │
│  │  - Health   │  │        ML Model Store               │     │
│  │    check    │  │                                    │     │
│  └─────────────┘  │  ONNX Runtime (ARM-optimized)      │     │
│                    │  TFLite models                     │     │
│                    │  Quantized INT8 where possible     │     │
│                    └────────────────────────────────────┘     │
│                                                              │
│  ┌─────────────┐  ┌──────────┐  ┌────────────────────┐      │
│  │  SQLite DB  │  │  Redis   │  │  Prometheus +       │      │
│  │  (metadata, │  │  (cache, │  │  Grafana (optional) │      │
│  │   contact)  │  │  sessions│  │  system monitoring  │      │
│  └─────────────┘  └──────────┘  └────────────────────┘      │
│                                                              │
│  OS: Raspberry Pi OS Lite (64-bit) — no desktop overhead     │
└──────────────────────────────────────────────────────────────┘
```

### Why this architecture?

**Cloudflare Tunnel** is the key insight here. Instead of:
- ❌ Exposing your home IP
- ❌ Fighting with ISP port blocking
- ❌ Paying for a static IP
- ❌ Setting up complex port forwarding

You get:
- ✅ Free SSL/HTTPS
- ✅ Free DDoS protection
- ✅ No inbound ports needed (tunnel is outbound from Pi)
- ✅ Works behind any NAT/ISP
- ✅ Free custom domain support (you just need to buy a cheap domain ~€1/year on Cloudflare Registrar or connect a free one)

**For the domain**: Buy a `.dev` domain on Cloudflare Registrar (~€10-12/year for `rahulsharma.dev` or similar). This is worth it for a professional portfolio. Alternatively, use a free subdomain via Cloudflare Pages or DuckDNS, but a real domain is a much better look for job applications.

---

## 3. Tech Stack Recommendation

| Layer | Technology | Why |
|-------|-----------|-----|
| **OS** | Raspberry Pi OS Lite 64-bit | No desktop = more RAM for models |
| **Reverse Proxy** | Nginx | Battle-tested, low overhead on ARM |
| **Tunnel** | Cloudflare Tunnel (`cloudflared`) | Free, secure, no port forwarding |
| **Backend API** | FastAPI (Python 3.11+) | You know Python, async, auto-docs |
| **Frontend** | React + Vite (or Astro for SSG) | Fast builds, modern, good for SPA portfolio |
| **Interactive Demos** | Streamlit | Perfect for ML demos, you already know it |
| **ML Inference** | ONNX Runtime / TFLite | ARM-optimized, fast inference |
| **Database** | SQLite | Zero config, perfect for single-server |
| **Cache** | Redis (optional) | Cache model outputs, rate limit demos |
| **Process Manager** | systemd services | Native, reliable, auto-restart |
| **Monitoring** | Simple health endpoint + UptimeRobot (free) | Know when Pi goes down |
| **Version Control** | Git + GitHub Actions | Auto-deploy on push via SSH |

### Why NOT Docker on Pi?
Docker adds ~200-400MB RAM overhead and ARM image compatibility can be tricky. With only one server and a known environment, `systemd` services + `venv` are simpler and leave more RAM for your models. You can always add Docker later if needed.

---

## 4. ML Model Deployment Strategy (Pi-Specific)

### RAM Budget (assuming 4GB Pi — adjust if 8GB)
```
Total RAM:               4096 MB
OS + system services:    ~400 MB
Nginx:                   ~50 MB
FastAPI backend:         ~100 MB
SQLite + Redis:          ~50 MB
─────────────────────────────────
Available for ML:        ~3400 MB (but not all at once)

Strategy: Load models ON-DEMAND, not all simultaneously.
Keep max 1-2 Streamlit apps warm, lazy-load others.
```

### Per-Project Model Strategy

| Project | Model Approach | Estimated Size | Notes |
|---------|---------------|---------------|-------|
| **EEG Generator** | Export your trained GAN/VAE/Diffusion to ONNX, quantize to INT8 | 50-200 MB | Generation is forward-pass only, Pi can handle it |
| **Medical Chatbot** | Use a small model like `TinyLlama-1.1B` (GGUF Q4) via `llama-cpp-python` OR use a retrieval-based approach (embeddings + FAQ) | 700 MB (TinyLlama) or 100 MB (retrieval) | Retrieval approach is more reliable on Pi; LLM will be slow but impressive |
| **Text OCR** | EasyOCR or PaddleOCR Lite → export to ONNX | 100-150 MB | These have ARM-optimized builds |
| **Bomberman RL** | Export trained policy network to ONNX | 10-50 MB | RL policies are tiny; the game rendering is the heavier part |

### Smart Loading Pattern
```python
# Don't load all models at startup — use lazy loading
class ModelManager:
    def __init__(self):
        self._models = {}
    
    def get_model(self, name: str):
        if name not in self._models:
            self._models[name] = self._load_model(name)
            # Evict oldest if RAM pressure
            if len(self._models) > 2:
                oldest = next(iter(self._models))
                del self._models[oldest]
        return self._models[name]
```

---

## 5. Phased Roadmap

### Phase 0: Pi Foundation (Week 1)
- [ ] Flash Raspberry Pi OS Lite 64-bit
- [ ] Configure SSH, set static local IP, update packages
- [ ] Install Python 3.11+, Node.js (via nvm), Nginx
- [ ] Set up Cloudflare account + Tunnel
- [ ] Buy/configure domain (e.g., `rahulsharma.dev`)
- [ ] Verify HTTPS works end-to-end with a "Hello World" page
- [ ] Set up basic Git deploy workflow (push to GitHub → webhook → Pi pulls)

### Phase 1: Portfolio Shell (Week 2-3)
- [ ] Design and build the portfolio frontend (React + Vite)
  - Landing page with hero section + your photo/intro
  - Projects grid with cards (filterable by tag: CV, NLP, RL, Neuro, etc.)
  - About page (education, skills, experience)
  - Contact form (FastAPI backend → sends email or stores in SQLite)
  - "Powered by Raspberry Pi 4" badge in footer (conversation starter!)
- [ ] Set up FastAPI backend with project metadata API
- [ ] Configure Nginx reverse proxy
- [ ] Deploy and test

### Phase 2: First Interactive Demo — Text_OCR (Week 3-4)
*Start with OCR because it's the most visually impressive and technically simplest to deploy.*
- [ ] Polish the Text_OCR repo (clean code, good README, proper structure)
- [ ] Convert model to ONNX / use PaddleOCR Lite
- [ ] Build Streamlit demo: upload image → see OCR results with bounding boxes
- [ ] Integrate into portfolio (iframe or link from project card)
- [ ] Add rate limiting (max N requests/hour per IP)

### Phase 3: EEG Generator Demo (Week 4-5)
*Your signature project — this is what makes you stand out.*
- [ ] Polish Generative-EEG-Augmentation repo
- [ ] Export your best GAN/VAE/Diffusion model to ONNX
- [ ] Build Streamlit app:
  - Model selector (GAN vs VAE vs Diffusion)
  - Parameter sliders (channels, noise level, duration)
  - Real-time waveform visualization (Plotly)
  - Side-by-side: real EEG vs generated EEG
- [ ] Write compelling project page explaining the neuroscience

### Phase 4: Medical Chatbot (Week 5-6)
- [ ] Polish Medical-chatbot repo
- [ ] Decide: small LLM (TinyLlama) vs retrieval-based approach
  - Retrieval: embed PubMed FAQ corpus → FAISS index → retrieve + format
  - LLM: llama-cpp-python with Q4 quantized model
- [ ] Build Streamlit chat interface
- [ ] Add example questions for visitors who don't know what to ask

### Phase 5: Bomberman RL Showcase (Week 6-7)
- [ ] Combine bomberman_game + bomberman_rl_RBN into one clean repo
- [ ] Export trained RL policy
- [ ] Build visualization:
  - Option A: Streamlit + matplotlib animation (simpler)
  - Option B: Browser-based game render with WebSocket to Pi (cooler but harder)
- [ ] Show training curves + agent progression

### Phase 6: Polish & Tier 2 Projects (Week 7-8)
- [ ] Add Tier 2 projects as static showcases (good READMEs, result images)
- [ ] Polish data_sanitization_pipeline
- [ ] Polish Optimized-BCI
- [ ] Polish ComputerVision-24
- [ ] Clean up GitHub: archive/private old repos, consistent naming

### Phase 7: Production Hardening (Week 8-9)
- [ ] Set up UptimeRobot monitoring (free, pings your domain)
- [ ] Add request rate limiting across all demos
- [ ] Set up log rotation
- [ ] Create a simple admin dashboard (system stats, request counts)
- [ ] Add analytics (self-hosted Plausible or simple SQLite-based counter)
- [ ] Test under load (what happens if multiple visitors hit demos simultaneously?)
- [ ] Set up automatic OS updates + service restarts

### Ongoing
- [ ] Add new projects as you build them at BASF (where appropriate)
- [ ] Blog section? (Optional — write about deploying ML on edge devices, your thesis, etc.)
- [ ] Iterate on design based on feedback

---

## 6. GitHub Cleanup Recommendations

### Immediate Actions
1. **Archive** all forked reference repos (or unstar/unfork them)
2. **Make private** all tutorial-level ML repos (titanic, credit card, regression, etc.)
3. **Archive** old Flutter/Dart/Swift repos (unless you want mobile on your profile)
4. **Rename repos** to follow consistent convention: `kebab-case`, descriptive names
5. **Pin** your 6 best repos on your GitHub profile

### Suggested Pinned Repos (after cleanup)
1. `generative-eeg-augmentation` — your flagship
2. `medical-chatbot` — NLP showcase
3. `text-ocr` — CV showcase
4. `bomberman-rl` — RL showcase (merged repo)
5. `data-sanitization-pipeline` — MLOps showcase
6. `portfolio` — the portfolio site itself (meta: shows infra skills)

---

## 7. Cost Breakdown

| Item | Cost | Notes |
|------|------|-------|
| Raspberry Pi 4 | Already owned | ✅ |
| Domain (`.dev`) | ~€12/year | Worth it. Cloudflare Registrar is cheapest |
| Cloudflare Tunnel | Free | Free tier is generous |
| SSL Certificate | Free | Via Cloudflare |
| UptimeRobot | Free | 50 monitors on free tier |
| Electricity | ~€5-10/year | Pi draws ~5W idle, ~7W under load |
| **Total** | **~€15-25/year** | |

---

## 8. Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Pi crashes / SD card corruption | Site goes down | Use a quality SD card (Samsung EVO), set up read-only root filesystem or regular backups to USB/cloud |
| Too many concurrent visitors hit ML demos | OOM / slow | Rate limit demos (max 2 concurrent inference), queue system, show "demo busy" message |
| ISP changes IP | Tunnel breaks temporarily | Cloudflare Tunnel auto-reconnects; add systemd watchdog |
| Model too large for Pi RAM | Can't load | Quantize to INT8, use smaller model variants, lazy loading |
| Power outage | Site offline | UPS for Pi (~€20) or just accept occasional downtime |
| Security breach via exposed service | Data loss | Cloudflare WAF (free), fail2ban, keep Streamlit apps read-only, no sensitive data on Pi |

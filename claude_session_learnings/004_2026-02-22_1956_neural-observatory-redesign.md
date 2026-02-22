# Session: 2026-02-22 — Neural Observatory Dark Theme Redesign

## Summary
Implemented the full "Neural Observatory" dark theme redesign across the portfolio frontend and added backend support for project detail pages. Converted all existing pages and components to a dark scientific aesthetic with custom Tailwind v4 tokens, created new pages (ProjectDetail, NotFound), added a `GET /projects/{slug}` API endpoint with long descriptions, and fixed issues with non-existent demo links and Streamlit navigation.

## Files Changed
- `.claude/design_language.md` — Created design system reference (palette, typography, component patterns)
- `frontend/index.html` — Added Google Fonts (Outfit, IBM Plex Sans, JetBrains Mono), meta description, updated title
- `frontend/src/index.css` — Full Tailwind v4 `@theme` with color tokens, font families, animations, dot-grid background
- `frontend/src/App.tsx` — Dark bg/text classes, added ProjectDetail and NotFound routes
- `frontend/src/components/Navbar.tsx` — Dark theme, "Rahul Sharma" branding, accent active states
- `frontend/src/components/Footer.tsx` — Dark theme with pulsing green "Raspberry Pi 4" badge
- `frontend/src/components/HeroSection.tsx` — Dark theme with staggered fade-up animations
- `frontend/src/components/ProjectCard.tsx` — Glow hover effect, Link wrapping, live/demo status badges (green for live, red for planned)
- `frontend/src/components/ContactForm.tsx` — Dark inputs, accent focus rings, success/error states
- `frontend/src/pages/Home.tsx` — Featured Projects section fetching tier-1 projects, dark skills grid
- `frontend/src/pages/Projects.tsx` — Dark tag filter buttons
- `frontend/src/pages/About.tsx` — Dark prose, accent dots
- `frontend/src/pages/Contact.tsx` — Dark text
- `frontend/src/hooks/useDocumentTitle.ts` — Created custom hook for per-page document titles
- `frontend/src/pages/ProjectDetail.tsx` — Created project detail page with tags, demo buttons, long description
- `frontend/src/pages/NotFound.tsx` — Created 404 page
- `frontend/vite.config.ts` — Added `/demo` proxy to Streamlit for local dev
- `backend/portfolio_api/models/project.py` — Added `long_description` column
- `backend/portfolio_api/schemas/project.py` — Added `ProjectDetailResponse` schema
- `backend/portfolio_api/routers/projects.py` — Added `GET /projects/{slug}` endpoint
- `backend/portfolio_api/seed.py` — Changed from skip-on-exists to upsert logic
- `backend/data/seed.json` — Added `long_description` to all 8 projects, fixed `demo_url` for unbuilt demos
- `demos/text-ocr/app.py` — Added back-to-project link with accent-colored pill button

## Decisions & Rationale
| Decision | Alternatives Considered | Why Chosen |
|----------|------------------------|------------|
| Set `demo_url: null` for unbuilt demos | Keep demo_url but show "coming soon" interstitial page | Simpler — no badge/button shown means no broken links; demo_url can be set when demos are actually built |
| Add back link as `st.markdown` HTML in Streamlit | Wrap Streamlit in a React iframe page | HTML link is minimal, iframe adds complexity and breaks Streamlit's native responsiveness |
| Tailwind v4 `@theme` tokens over config file | tailwind.config.js with theme.extend | Tailwind v4 uses CSS-native `@theme` — config file approach is v3 legacy |
| Vite `/demo` proxy for local dev | Direct links to port 8502 | Matches production Nginx behavior where `/demo/*` is proxied; avoids CORS and keeps URLs consistent |
| Parallel subagent execution (up to 5 agents) | Sequential single-agent execution | Massive speed improvement — Phases B, C (3 agents), and D all ran concurrently |

## Learnings
- Tailwind v4 `@plugin` replaces the old `plugins: []` array from tailwind.config.js — use `@plugin "@tailwindcss/typography"` in CSS
- Tailwind v4 `--color-*` tokens auto-generate utilities: `bg-bg-primary`, `text-accent`, `border-border` etc. Opacity modifiers work: `bg-accent/15`
- Tailwind v4 `--font-*` tokens auto-generate `font-display`, `font-body`, `font-mono` utilities
- Tailwind v4 `--animate-*` tokens auto-generate `animate-fade-up`, `animate-pulse-dot` utilities
- Vite dev server proxy needs `ws: true` for Streamlit WebSocket connections
- Deleting and re-creating a SQLite DB while uvicorn `--reload` is running doesn't trigger a reload — the server keeps the old DB connection; must restart the process
- Streamlit `unsafe_allow_html=True` is needed for custom HTML links — inline styles work since Streamlit strips `<style>` tags
- When subagents don't have Bash permission, they complete file edits but can't run verification (lint/build) — the orchestrator should handle verification centrally

## Subagent Analysis
| Agent | Task | Outcome | Notes |
|-------|------|---------|-------|
| frontend-dev | Phase A: index.html + index.css + npm install | Success (partial) | Completed file edits but couldn't run `npm install` without Bash permission; orchestrator did the install |
| backend-dev | Phase D: model + schema + router + seed | Success | All 5 steps completed cleanly; couldn't run ruff check but orchestrator verified |
| frontend-dev | Phase B: Navbar + Footer | Success | Clean class replacements and Footer rewrite |
| frontend-dev | Phase C1: App.tsx + HeroSection + ContactForm | Success | Three components in one agent to minimize overhead |
| frontend-dev | Phase C2: ProjectCard | Success | Most complex component — Link wrapping, glow effect, badge logic |
| frontend-dev | Phase C3: Home + Projects + About + Contact | Success | Four pages in one agent; largest agent by tool use count (18) |
| frontend-dev | Phase E: New pages + routes | Success | Created 3 files and modified App.tsx routes; ran lint+build successfully |
| frontend-dev | Phase F1: useDocumentTitle to all pages | Success (stuck on build) | Completed all file edits but got stuck waiting for Bash permission for lint/build; orchestrator stopped it and verified centrally |

Key subagent insight: Agents without Bash permission complete file edits fine but block on verification commands. Better to either grant Bash permission upfront or have the orchestrator handle all verification.

## Mistakes & Corrections
- **Mistake**: Seed data had `demo_url` set for EEG, Chatbot, and Bomberman demos that don't exist yet, causing 404 when clicking "Try Live Demo"
  - **Fix**: Set `demo_url: null` for those 3 projects and re-seeded
  - **Prevention**: Only set `demo_url` when the demo is actually built and deployed; treat seed.json as reflecting current state, not planned state
- **Mistake**: No Vite proxy for `/demo/*` path, so "Try Live Demo" on OCR returned 404 in local dev
  - **Fix**: Added `/demo` proxy entry in vite.config.ts pointing to port 8502 with `ws: true`
  - **Prevention**: When adding demo links, always ensure the local dev proxy matches production Nginx routing
- **Mistake**: Phase F1 agent got stuck waiting for Bash permission, wasting time
  - **Fix**: Stopped the agent and ran verification centrally
  - **Prevention**: For agents that need verification steps, either pre-approve Bash or plan for orchestrator to handle verification

## Unfinished Work
- [ ] Uncommitted change: `demos/text-ocr/app.py` — improved back-link styling (accent pill button)
- [ ] ProjectCard shows no badge for tier-1 projects without demo_url (EEG, Chatbot, Bomberman) — may want a "Coming Soon" badge
- [ ] No favicon update — still using default vite.svg
- [ ] No responsive testing verification done in browser
- [ ] Accessibility audit not performed (tab navigation, screen reader, contrast ratios)

## Memory Promotion Candidates
> These insights may be worth adding to MEMORY.md:
- Tailwind v4 uses `@theme` block in CSS (not tailwind.config.js), `@plugin` for plugins, and `--color-*`/`--font-*`/`--animate-*` tokens auto-generate utilities with opacity modifier support
- Vite proxy needs `ws: true` for Streamlit WebSocket connections
- Subagents without Bash permission complete file edits but block on verification — handle lint/build centrally in orchestrator
- SQLite DB deletion doesn't trigger uvicorn `--reload` — must restart the process
- User preference: no co-author information in git commits

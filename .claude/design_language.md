# Neural Observatory Design Language

Single source of truth for the portfolio's dark scientific interface.

## Palette

| Token | Hex | Tailwind Class | Usage |
|-------|-----|----------------|-------|
| `bg-primary` | `#0a0a0f` | `bg-bg-primary` | Page background |
| `bg-secondary` | `#12121a` | `bg-bg-secondary` | Cards, inputs |
| `bg-tertiary` | `#1a1a2e` | `bg-bg-tertiary` | Hover/elevated |
| `border` | `#2a2a3e` | `border-border` | Subtle borders |
| `border-hover` | `#3a3a5e` | `border-border-hover` | Interactive borders |
| `text-primary` | `#e4e4e7` | `text-text-primary` | Body text |
| `text-secondary` | `#a1a1aa` | `text-text-secondary` | Secondary text |
| `text-muted` | `#71717a` | `text-text-muted` | Muted/labels |
| `accent` | `#6366f1` | `text-accent`, `bg-accent` | Indigo primary |
| `accent-hover` | `#818cf8` | `hover:bg-accent-hover` | Indigo hover |
| `accent-glow` | `rgba(99,102,241,0.15)` | via `var(--color-accent-glow)` | Card hover glow |
| `live` | `#34d399` | `text-live`, `bg-live/10` | Live demo badge |
| `tag` | `#fbbf24` | `text-tag`, `bg-tag/10` | Tag pills |
| `error` | `#ef4444` | `text-error` | Error states |
| `success` | `#22c55e` | `text-success` | Success states |

## Typography

| Role | Font | Tailwind Class | Weights |
|------|------|----------------|---------|
| Display/headings | Outfit | `font-display` | 500, 600, 700 |
| Body | IBM Plex Sans | `font-body` | 400, 500, 600 |
| Code | JetBrains Mono | `font-mono` | 400 |

**Font loading**: Google Fonts via `<link>` in `frontend/index.html` with `preconnect`.

## Component Patterns

### Cards
```
rounded-lg border border-border bg-bg-secondary p-6
transition-all duration-300
hover:border-accent/50 hover:shadow-[0_0_20px_var(--color-accent-glow)] hover:scale-[1.02]
```

### Buttons (primary)
```
bg-accent text-white font-medium rounded-lg
hover:bg-accent-hover transition-colors
focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent
```

### Buttons (secondary)
```
text-text-primary font-medium rounded-lg border border-border
hover:bg-bg-tertiary transition-colors
```

### Tags
```
inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
bg-tag/10 text-tag border border-tag/20
```

### Live Badge
```
inline-flex items-center gap-1.5 px-2 py-0.5
bg-live/10 text-live rounded-full text-xs font-medium
```
With pulsing dot SVG: `<svg class="w-1.5 h-1.5 animate-pulse-dot" viewBox="0 0 6 6" fill="currentColor"><circle cx="3" cy="3" r="3" /></svg>`

### Inputs
```
bg-bg-secondary border-border text-text-primary placeholder-text-muted
focus:border-accent focus:ring-1 focus:ring-accent/20
```

### Section headings
```
text-2xl font-bold font-display text-text-primary
```

### Labels
```
text-sm font-semibold text-text-muted uppercase tracking-wide
```

### Skill chips
```
inline-flex items-center px-3 py-1 rounded-full text-sm
bg-bg-tertiary border border-border text-text-secondary
```

## Background Texture

Subtle dot grid applied to `html` in `frontend/src/index.css`:
```css
background-image: radial-gradient(circle, rgba(99, 102, 241, 0.06) 1px, transparent 1px);
background-size: 24px 24px;
```

## Animations

| Token | Class | Usage |
|-------|-------|-------|
| `fade-up` | `animate-fade-up` | Hero staggered entrance |
| `pulse-dot` | `animate-pulse-dot` | Live badge / Pi badge dots |

Stagger via inline `style={{ animationDelay: '0.1s' }}`.

## Theme Source of Truth

- **CSS tokens**: `frontend/src/index.css` (`@theme` block)
- **Tailwind v4**: Tokens auto-generate utilities (`--color-*` → `bg-*`, `text-*`, `border-*`; `--font-*` → `font-*`; `--animate-*` → `animate-*`)
- **Opacity modifiers**: Work on all color tokens: `bg-accent/15`, `text-live/80`, `border-tag/20`

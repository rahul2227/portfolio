---
globs: frontend/src/**/*.{ts,tsx}
---

# Frontend Rules

- Use Tailwind utility classes for all styling — avoid custom CSS files
- Functional components with explicitly typed props interfaces
- Use `fetch` for API calls to `/api/*` — no axios
- Mobile-first responsive design (sm → md → lg breakpoints)
- Accessible HTML: semantic elements, aria attributes, proper heading hierarchy
- Named exports preferred over default exports
- Keep components under 200 lines — extract sub-components if larger
- Handle loading and error states for all data-fetching components
- No `any` types — use proper TypeScript types

# Session: 2026-02-20 — Local Deploy Fixes

## Summary
Attempted local dev deploy using the `/deploy local` skill. Fixed a corrupted backend venv (stale binary from different platform/python) and a broken frontend `node_modules` (vite symlink pointing to nonexistent path). OCR demo worked correctly on first try.

## Files Changed
- `backend/.venv/` — Deleted and recreated. The existing venv had a broken Python binary (`cannot execute binary file`), likely from a different platform or Python version.
- `frontend/node_modules/` — Deleted and reinstalled. The vite binary symlink was broken (`ERR_MODULE_NOT_FOUND: Cannot find module .../node_modules/dist/node/cli.js`).

## Learnings
- Backend venv corruption manifests as `cannot execute binary file` — the `.venv/bin/python3` binary was incompatible. Fix: `rm -rf .venv && uv sync`.
- Frontend `node_modules` corruption shows as `ERR_MODULE_NOT_FOUND` on the vite CLI binary. Fix: `rm -rf node_modules && npm install`.
- `npm install` alone does not fix corrupted symlinks in `node_modules/.bin/` — a full `rm -rf node_modules` is needed first.

## Mistakes & Corrections
- **Mistake**: Backend `uv sync` failed silently (exit code 0) but printed an error about the stale venv binary
  - **Fix**: Deleted `.venv/` entirely and re-ran `uv sync` to create a fresh venv
  - **Prevention**: If `uv sync` prints any error text, treat it as a failure even if exit code is 0. Check for `error:` in output.

## Memory Promotion Candidates
> These insights may be worth adding to MEMORY.md:
- Stale `.venv` fix: if `uv sync` shows `cannot execute binary file`, delete `.venv/` and re-sync
- Stale `node_modules` fix: if vite shows `ERR_MODULE_NOT_FOUND`, delete `node_modules/` and `npm install`

---
name: test
description: Run the full test suite for both backend (pytest) and frontend (vitest) and summarize results.
disable-model-invocation: true
allowed-tools: Bash
---

Run all tests for the portfolio project and report results.

## Steps

1. **Backend tests**:
   ```bash
   cd /home/rahser/portfolio/backend && uv run pytest -v 2>&1
   ```

2. **Frontend tests**:
   ```bash
   cd /home/rahser/portfolio/frontend && npm test -- --run 2>&1
   ```

3. **Lint checks**:
   ```bash
   cd /home/rahser/portfolio/backend && uv run ruff check . 2>&1
   cd /home/rahser/portfolio/frontend && npm run lint 2>&1
   ```

4. **Summary**: Report for each category:
   - Total tests run
   - Passing / failing counts
   - Specific failing test names and their error output (if any)
   - Lint errors (if any)

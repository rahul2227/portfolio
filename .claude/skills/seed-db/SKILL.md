---
name: seed-db
description: Seed the SQLite database with project data from seed.json. Use 'reset' argument to drop and recreate tables first.
disable-model-invocation: true
allowed-tools: Bash
argument-hint: "[reset]"
---

Seed the portfolio database with project data.

## Mode
- Default (no argument): insert seed data, skip existing records
- `reset` argument: drop all tables, recreate them, then insert seed data

## Steps

1. If argument is "reset":
   ```bash
   cd /home/rahser/portfolio/backend
   rm -f data/portfolio.db
   echo "Database file removed. Will be recreated on next start."
   ```

2. Run the seed script:
   ```bash
   cd /home/rahser/portfolio/backend
   uv run python -m portfolio_api.seed
   ```

3. Verify the data was inserted:
   ```bash
   cd /home/rahser/portfolio/backend
   sqlite3 data/portfolio.db "SELECT count(*) FROM projects;"
   sqlite3 data/portfolio.db "SELECT slug, title, tier FROM projects ORDER BY tier, \"order\";"
   ```

4. Report how many records exist in each table.

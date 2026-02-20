---
globs: backend/**/*.py
---

# Backend Rules

- Async SQLAlchemy patterns with `AsyncSession`
- Pydantic v2 models for all request/response schemas (`model_config = {"from_attributes": True}`)
- Type annotations on all function parameters and return values
- Use dependency injection for DB sessions via `Depends(get_db)`
- Never hardcode secrets — use `Settings` from `config.py` with `PORTFOLIO_` env var prefix
- Add dependencies via `uv add <package>` (not pip install)
- Use SQLAlchemy `select()`, `insert()`, etc. — never raw SQL strings
- Proper HTTP status codes: 200 success, 201 creation, 404 not found, 422 validation

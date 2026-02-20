from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "PORTFOLIO_"}

    debug: bool = False
    database_url: str = (
        f"sqlite+aiosqlite:///{Path(__file__).resolve().parent.parent / 'data' / 'portfolio.db'}"
    )
    redis_url: str = "redis://127.0.0.1:6379/0"
    contact_rate_limit: int = 5  # max contact submissions per hour


settings = Settings()

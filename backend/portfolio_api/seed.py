"""Seed the database with project data from seed.json."""

import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from portfolio_api.database import async_session, engine
from portfolio_api.models import Base
from portfolio_api.models.project import Project


async def seed() -> None:
    seed_file = Path(__file__).resolve().parent.parent / "data" / "seed.json"
    with open(seed_file) as f:
        projects_data: list[dict[str, object]] = json.load(f)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        for item in projects_data:
            result = await session.execute(
                select(Project).where(Project.slug == item["slug"])
            )
            if result.scalar_one_or_none() is None:
                session.add(Project(**item))
                print(f"  Added: {item['title']}")
            else:
                print(f"  Skipped (exists): {item['title']}")
        await session.commit()

    print(f"\nSeeded {len(projects_data)} projects.")


if __name__ == "__main__":
    asyncio.run(seed())

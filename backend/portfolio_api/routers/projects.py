from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio_api.database import get_db
from portfolio_api.models.project import Project
from portfolio_api.schemas.project import ProjectResponse

router = APIRouter()


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)) -> list[ProjectResponse]:
    result = await db.execute(select(Project).order_by(Project.tier, Project.order))
    projects = result.scalars().all()
    return [ProjectResponse.from_orm_with_tags(p) for p in projects]

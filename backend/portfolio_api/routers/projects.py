from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio_api.database import get_db
from portfolio_api.models.project import Project
from portfolio_api.schemas.project import ProjectDetailResponse, ProjectResponse

router = APIRouter()


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)) -> list[ProjectResponse]:
    result = await db.execute(select(Project).order_by(Project.tier, Project.order))
    projects = result.scalars().all()
    return [ProjectResponse.from_orm_with_tags(p) for p in projects]


@router.get("/projects/{slug}", response_model=ProjectDetailResponse)
async def get_project(slug: str, db: AsyncSession = Depends(get_db)) -> ProjectDetailResponse:
    """Get a single project by slug for the detail page."""
    result = await db.execute(select(Project).where(Project.slug == slug))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectDetailResponse.from_orm_with_tags(project)

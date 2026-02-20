from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio_api.database import get_db
from portfolio_api.models.contact import ContactMessage
from portfolio_api.schemas.contact import ContactRequest, ContactResponse

router = APIRouter()


@router.post("/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def submit_contact(
    data: ContactRequest, db: AsyncSession = Depends(get_db)
) -> ContactMessage:
    message = ContactMessage(name=data.name, email=data.email, message=data.message)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

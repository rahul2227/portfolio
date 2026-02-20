from datetime import datetime

from pydantic import BaseModel, EmailStr


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str


class ContactResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    email: str
    message: str
    created_at: datetime

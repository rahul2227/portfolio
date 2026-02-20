from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from portfolio_api.models.contact import ContactMessage  # noqa: E402, F401
from portfolio_api.models.project import Project  # noqa: E402, F401

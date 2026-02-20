from pydantic import BaseModel


class ProjectResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    slug: str
    title: str
    description: str
    tags: list[str]
    tier: int
    order: int
    github_url: str | None
    demo_url: str | None
    image_url: str | None

    @classmethod
    def from_orm_with_tags(cls, obj: object) -> "ProjectResponse":
        """Convert ORM object, splitting comma-separated tags into a list."""
        data = {
            "id": obj.id,  # type: ignore[attr-defined]
            "slug": obj.slug,  # type: ignore[attr-defined]
            "title": obj.title,  # type: ignore[attr-defined]
            "description": obj.description,  # type: ignore[attr-defined]
            "tags": [t.strip() for t in obj.tags.split(",") if t.strip()],  # type: ignore[attr-defined]
            "tier": obj.tier,  # type: ignore[attr-defined]
            "order": obj.order,  # type: ignore[attr-defined]
            "github_url": obj.github_url,  # type: ignore[attr-defined]
            "demo_url": obj.demo_url,  # type: ignore[attr-defined]
            "image_url": obj.image_url,  # type: ignore[attr-defined]
        }
        return cls(**data)

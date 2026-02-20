import platform
import sys

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "platform": platform.machine(),
        "python": sys.version,
        "system": platform.system(),
    }

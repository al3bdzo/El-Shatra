from fastapi import APIRouter

from app.deps import player

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "engine": type(player).__name__}

"""GET /api/health: is the server up, and which providers and auth mode is it using? No login needed."""

from fastapi import APIRouter, Depends

from app import database
from app.config import Settings, get_settings

router = APIRouter()


@router.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "status": "ok",
        "llm_chain": settings.llm_chain_list,
        "stt_chain": settings.stt_chain_list,
        "auth_mode": settings.auth_mode,
        "database": "connected" if database.is_connected() else "unreachable",
    }

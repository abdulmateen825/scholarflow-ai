from fastapi import APIRouter
from app.core.config import settings
from app.integrations.google_mcp import google_mcp

router = APIRouter()


@router.get("/")
async def integrations():
    return {"integrations": await google_mcp.status(),
            "openai": {"configured": bool(settings.openai_api_key)},
            "tavily": {"configured": bool(settings.tavily_api_key)}}



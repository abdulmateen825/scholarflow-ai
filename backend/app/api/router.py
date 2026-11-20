from fastapi import APIRouter
from app.api.routes import assignments, analysis, integrations, memories, research
from app.core.config import settings

api = APIRouter()
api.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api.include_router(analysis.router, prefix="/assignments", tags=["analysis"])
api.include_router(memories.router, prefix="/memories", tags=["memory"])
api.include_router(research.router, prefix="/research", tags=["research"])
api.include_router(integrations.router, prefix="/integrations", tags=["integrations"])


@api.get("/classroom/status", tags=["integrations"])
async def classroom_status():
    from app.integrations.google_mcp import google_mcp
    return await google_mcp.check("Google Classroom", settings.google_classroom_mcp_url)


@api.get("/", tags=["system"])
async def api_info():
    return {"name": settings.app_name, "version": "1.0.0", "api_version": "v1"}

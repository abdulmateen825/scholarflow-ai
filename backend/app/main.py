import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.router import api
from app.core.config import settings
from app.core.errors import http_error_handler, unexpected_error_handler
from app.db.database import initialize_database

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("scholarflow")
app = FastAPI(title=settings.app_name, description="AI-powered academic assignment assistant", version="1.0.0")
app.add_event_handler("startup", initialize_database)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)
app.include_router(api, prefix="/api/v1")

@app.get("/")
async def root(): return {"name": settings.app_name, "status": "running", "docs": "/docs"}

@app.get("/health")
async def health(): return {"status": "healthy"}

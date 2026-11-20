from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": {"message": exc.detail}})

async def unexpected_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": {"message": "An unexpected server error occurred."}})

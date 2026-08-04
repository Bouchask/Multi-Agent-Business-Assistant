from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.config.settings import settings
from backend.app.core.logging import setup_logging
from backend.app.core.exceptions import UnauthorizedException, ForbiddenException, NotFoundException, BadRequestException, DuplicateEntityException
from backend.app.db.engine import engine
from backend.app.db.base import Base
from backend.app.models import *  # Import all tables for automatic schema build on startup
from backend.app.api.v1 import auth_router, project_router, task_router, meeting_router, file_router, chat_router
from backend.app.middleware.audit_log import AuditLoggingMiddleware

# Initialize structured loguru logging
setup_logging()

# Create SQL database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Multi-Agent Business Assistant API",
    description="Enterprise Multi-Agent Operating System built with FastAPI, LangGraph, and OpenRouter.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Audit Request Logging & CORS configuration
app.add_middleware(AuditLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enterprise structured exception handlers
@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail}, headers=exc.headers)

@app.exception_handler(ForbiddenException)
async def forbidden_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail})

@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail})

@app.exception_handler(BadRequestException)
async def bad_request_handler(request: Request, exc: BadRequestException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail})

@app.exception_handler(DuplicateEntityException)
async def duplicate_handler(request: Request, exc: DuplicateEntityException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail})

# Include API V1 Routers
app.include_router(auth_router.router)
app.include_router(project_router.router)
app.include_router(task_router.router)
app.include_router(meeting_router.router)
app.include_router(file_router.router)
app.include_router(chat_router.router)

@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "online",
        "service": "Multi-Agent Business Assistant",
        "environment": settings.APP_ENV,
        "version": "1.0.0"
    }

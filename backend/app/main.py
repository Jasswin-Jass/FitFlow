from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import FitFlowException
from app.api.v1.router import api_router
from app.database.session import engine
from app.database.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fitflow")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing FitFlow database schemas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully.")
    yield
    logger.info("Shutting down FitFlow engine...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FitFlow — Business Intelligence Platform for Gyms (Phase 1 API)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Centralized Exception Handlers
@app.exception_handler(FitFlowException)
async def fitflow_exception_handler(request: Request, exc: FitFlowException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "detail": exc.detail_message},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(p) for p in err.get("loc", []) if p != "body"])
        msg = err.get("msg", "Invalid value")
        errors.append(f"{loc}: {msg}" if loc else msg)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "ValidationError", "detail": "; ".join(errors)},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "InternalServerError", "detail": "An unexpected server error occurred."},
    )


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "FitFlow API",
        "environment": settings.ENVIRONMENT,
    }


# Include API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

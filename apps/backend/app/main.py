from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.backend.app.api.v1.router import api_v1_router
from apps.backend.app.core.config import settings

from contextlib import asynccontextmanager
from apps.backend.app.graph.driver import neo4j_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    # Startup
    neo4j_manager.init_driver()
    yield
    # Shutdown
    neo4j_manager.close()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Explainable AI-Assisted Criminal Network Analysis System Backend API",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    lifespan=lifespan,
)

# CORS Configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Structured Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global structured exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please refer to system logs.",
                "path": str(request.url.path),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


# Root Service Information Endpoint
@app.get("/", tags=["Service Info"])
async def root_info() -> dict[str, str]:
    """Root metadata endpoint."""
    return {
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "0.1.0",
        "docs_url": f"{settings.API_PREFIX}/docs",
        "health_url": f"{settings.API_PREFIX}/health",
        "synthetic_data_policy": "Strictly Synthetic Data Only",
    }


# Include API v1 Router
app.include_router(api_v1_router, prefix=settings.API_PREFIX)

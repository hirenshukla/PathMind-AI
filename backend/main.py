"""
PathMind AI - Production FastAPI Backend
========================================
Main application entry point with all middleware, routers, and startup events.
"""

import logging
import os
import time

# ─── Environment Detection ─────────────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"
DEBUG_ENABLED = os.getenv("DEBUG", "false").lower() == "true"

if IS_PRODUCTION and DEBUG_ENABLED:
    raise RuntimeError("DEBUG must be false in production.")

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from models.database import Base, DATABASE_URL, engine
from routers import admin, auth, career, decision, loan, market, realdata, resume, subscription, users
from services.scheduler import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


def detect_database_name(url: str) -> str:
    scheme = url.split("://", 1)[0].lower()
    dialect = scheme.split("+", 1)[0]
    return "postgresql" if dialect.startswith("postgresql") else dialect


DATABASE_NAME = detect_database_name(DATABASE_URL)


def parse_csv_env(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


DEFAULT_CORS_ORIGINS = (
    "https://pathmind.ai,https://www.pathmind.ai,https://app.pathmind.ai"
    if IS_PRODUCTION
    else "http://localhost:3000,http://localhost:3001,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:8080"
)

DEFAULT_TRUSTED_HOSTS = (
    "pathmind.ai,www.pathmind.ai,api.pathmind.ai,app.pathmind.ai"
    if IS_PRODUCTION
    else "localhost,127.0.0.1,*.localhost,*"
)

CORS_ALLOW_ORIGIN_REGEX = (os.getenv("CORS_ALLOW_ORIGIN_REGEX") or "").strip() or None


app = FastAPI(
    title="PathMind AI API",
    description="India's #1 AI-powered Career & Life Decision Platform",
    version="2.0.0",
    docs_url=None if IS_PRODUCTION else "/api/docs",
    redoc_url=None if IS_PRODUCTION else "/api/redoc",
    openapi_url=None if IS_PRODUCTION else "/api/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_csv_env(
        "CORS_ORIGINS",
        DEFAULT_CORS_ORIGINS,
    ),
    allow_origin_regex=CORS_ALLOW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=parse_csv_env("TRUSTED_HOSTS", DEFAULT_TRUSTED_HOSTS),
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    # In production, never leak error details to clients
    content = {"detail": "Internal server error"}
    if not IS_PRODUCTION:
        content["type"] = type(exc).__name__
        content["message"] = str(exc)
    return JSONResponse(status_code=500, content=content)


@app.on_event("startup")
async def startup_event():
    logger.info("PathMind AI Backend starting up...")
    # Prevent stale asyncpg connections when app lifecycle is recreated (tests/reloads).
    await engine.dispose()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()
    logger.info("Database tables ready")
    logger.info("Background scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("PathMind AI shutting down...")
    await engine.dispose()


@app.get("/health", tags=["System"])
async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": DATABASE_NAME},
        )

    return {"status": "healthy", "database": DATABASE_NAME}


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "PathMind AI API v2.0",
        "docs": None if IS_PRODUCTION else "/api/docs",
        "status": "running",
    }


API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{API_PREFIX}/user", tags=["Users"])
app.include_router(career.router, prefix=f"{API_PREFIX}/career", tags=["Career"])
app.include_router(decision.router, prefix=f"{API_PREFIX}/decision", tags=["Life Decision"])
app.include_router(resume.router, prefix=f"{API_PREFIX}/resume", tags=["Resume"])
app.include_router(market.router, prefix=f"{API_PREFIX}/market", tags=["Market"])
app.include_router(loan.router, prefix=f"{API_PREFIX}/loan", tags=["Loan"])
app.include_router(subscription.router, prefix=f"{API_PREFIX}/subscription", tags=["Subscription"])
app.include_router(admin.router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])
app.include_router(realdata.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=not IS_PRODUCTION,
        log_level="warning" if IS_PRODUCTION else "info",
        workers=4 if IS_PRODUCTION else 1,
    )

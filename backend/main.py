"""
PathMind AI - Production FastAPI Backend
========================================
Main application entry point with all middleware, routers, and startup events.
"""

import logging
import os
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from models.database import Base, engine
from routers import admin, auth, career, decision, loan, market, realdata, resume, subscription, users
from services.scheduler import start_scheduler

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"
DEBUG_ENABLED = os.getenv("DEBUG", "false").lower() == "true"

if IS_PRODUCTION and DEBUG_ENABLED:
    raise RuntimeError("DEBUG must be false in production.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "*",
        "localhost",
        "127.0.0.1",
        "*.onrender.com",
        "pathmind-backend.onrender.com",
    ],
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
    content = {"detail": "Internal server error"}
    if not IS_PRODUCTION:
        content["type"] = type(exc).__name__
        content["message"] = str(exc)
    return JSONResponse(status_code=500, content=content)


@app.on_event("startup")
async def startup_event():
    logger.info("PathMind AI Backend starting up...")
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


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "postgresql",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
    }


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
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )

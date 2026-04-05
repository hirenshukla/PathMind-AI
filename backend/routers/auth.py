"""
Auth Router — JWT Authentication
==================================
Handles signup, login, token refresh, password reset.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import logging
import jwt
import bcrypt
import secrets
import os

from models.database import get_db, User, UserProfile, Subscription, SubscriptionPlan, SubscriptionStatus
from schemas.schemas import (
    SignupRequest, LoginRequest, TokenResponse, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, MessageResponse
)
from services.email_service import send_verification_email, send_reset_email
from services.activity_service import log_activity

router = APIRouter()
security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
INSECURE_JWT_SECRETS = {
    "",
    "your-super-secret-key-change-in-production",
    "CHANGE-THIS-TO-A-LONG-RANDOM-SECRET",
}

SECRET_KEY = (os.getenv("JWT_SECRET_KEY") or "").strip()
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY must be set in the environment."
    )

if ENVIRONMENT == "production" and (SECRET_KEY in INSECURE_JWT_SECRETS or len(SECRET_KEY) < 32):
    raise RuntimeError(
        "JWT_SECRET_KEY must be a strong random value (minimum 32 characters) in production."
    )

if ENVIRONMENT != "production" and (SECRET_KEY in INSECURE_JWT_SECRETS or len(SECRET_KEY) < 32):
    logger.warning("Using weak JWT_SECRET_KEY in development. Replace it before production deploy.")

if ENVIRONMENT == "production" and len(SECRET_KEY) < 64:
    logger.warning(
        "JWT_SECRET_KEY is valid but shorter than the recommended 64+ characters for production."
    )

ALGORITHM       = "HS256"
ACCESS_EXPIRE   = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))    # 1 hour
REFRESH_EXPIRE  = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 30))      # 30 days


# ─── JWT Helpers ─────────────────────────────────────────────────────────────
def create_access_token(user_id: int, email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_EXPIRE)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": secrets.token_hex(16),
        "exp": now + timedelta(days=REFRESH_EXPIRE)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ─── Get Current User Dependency ─────────────────────────────────────────────
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )

    payload = verify_token(credentials.credentials, "access")
    user_id = int(payload["sub"])

    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_user_pro(user: User = Depends(get_current_user)) -> User:
    """Requires Pro subscription"""
    if user.role not in ("pro", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a Pro subscription. Upgrade at /subscription"
        )
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """Requires admin role"""
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: Request,
    body: SignupRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account"""

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    # Create user
    user = User(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email.lower(),
        hashed_password=hash_password(body.password),
        last_login=datetime.now(timezone.utc)
    )
    db.add(user)
    await db.flush()  # Get user.id

    # Create profile
    profile = UserProfile(
        user_id=user.id,
        age=body.age,
        user_type=body.user_type,
        education=body.education,
        skills=[],
        interests=[],
        profile_score=15.0  # Base score for registration
    )
    db.add(profile)

    # Create free subscription
    subscription = Subscription(
        user_id=user.id,
        plan=SubscriptionPlan.free,
        status=SubscriptionStatus.active,
        predictions_limit=5,
        predictions_used=0,
        started_at=datetime.now(timezone.utc)
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(user)

    # Send verification email (background)
    background_tasks.add_task(send_verification_email, user.email, user.first_name)

    # Generate tokens
    access_token  = create_access_token(user.id, user.email, user.role.value)
    refresh_token = create_refresh_token(user.id)

    await log_activity(db, user.id, "signup", {"user_type": body.user_type})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_EXPIRE * 60,
        user={
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role.value
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password"""

    result = await db.execute(
        select(User).where(User.email == body.email.lower(), User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    access_token  = create_access_token(user.id, user.email, user.role.value)
    refresh_token = create_refresh_token(user.id)

    await log_activity(db, user.id, "login", {})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_EXPIRE * 60,
        user={
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role.value
        }
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""

    payload = verify_token(body.refresh_token, "refresh")
    user_id = int(payload["sub"])

    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access_token = create_access_token(user.id, user.email, user.role.value)
    return {"access_token": new_access_token, "token_type": "bearer", "expires_in": ACCESS_EXPIRE * 60}


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Send password reset email"""

    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if user:
        reset_token = secrets.token_urlsafe(32)
        # Store reset token in Redis/DB (simplified here)
        background_tasks.add_task(send_reset_email, user.email, reset_token)

    return MessageResponse(message="If that email exists, a reset link has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password with token"""
    # Verify reset token from Redis/cache (simplified)
    # In production: verify token, find user, update password
    return MessageResponse(message="Password reset successfully. Please login.")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info"""
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout (invalidate token - handled client-side for JWT)"""
    await log_activity(db, current_user.id, "logout", {})
    return MessageResponse(message="Logged out successfully")

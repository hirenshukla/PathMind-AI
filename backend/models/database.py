"""
Database Models - SQLAlchemy ORM
==================================
All PostgreSQL table definitions using async SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    JSON, Text, ForeignKey, Enum, Index
)
from sqlalchemy.sql import func
from datetime import datetime
import enum
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"

# ─── Database URL ─────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/pathmind_db"
)

if IS_PRODUCTION and DATABASE_URL.startswith("sqlite"):
    raise RuntimeError("SQLite is not allowed in production. Use PostgreSQL for DATABASE_URL.")

DEBUG_ENABLED = os.getenv("DEBUG", "false").lower() == "true"
if IS_PRODUCTION and DEBUG_ENABLED:
    raise RuntimeError("DEBUG must be false in production.")

# ─── Engine & Session ─────────────────────────────────────────────────────────
engine_kwargs = {
    "echo": DEBUG_ENABLED,
}

# sqlite does not support pool_size/max_overflow in SQLAlchemy async engine
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(
        {
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "pool_pre_ping": True,
        }
    )

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

_db_initialized = False
_db_init_lock = asyncio.Lock()


async def init_db_once():
    """Create all tables once per process."""
    global _db_initialized
    if _db_initialized:
        return

    async with _db_init_lock:
        if _db_initialized:
            return
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _db_initialized = True

# ─── Dependency ───────────────────────────────────────────────────────────────
async def get_db():
    await init_db_once()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# ══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ══════════════════════════════════════════════════════════════════════════════

class UserRole(str, enum.Enum):
    free = "free"
    pro = "pro"
    admin = "admin"

class SubscriptionPlan(str, enum.Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"

class SubscriptionStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"
    trial = "trial"

class DemandLevel(str, enum.Enum):
    high = "High"
    medium = "Medium"
    low = "Low"

class SectorType(str, enum.Enum):
    government = "Government"
    private = "Private"
    both = "Both"

# ══════════════════════════════════════════════════════════════════════════════
# TABLES
# ══════════════════════════════════════════════════════════════════════════════

class User(Base):
    """Core user account table"""
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    first_name      = Column(String(100), nullable=False)
    last_name       = Column(String(100), nullable=True)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role            = Column(Enum(UserRole), default=UserRole.free)
    is_active       = Column(Boolean, default=True)
    is_verified     = Column(Boolean, default=False)
    avatar_url      = Column(String(500), nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())
    last_login      = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    profile         = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    predictions     = relationship("CareerPrediction", back_populates="user", cascade="all, delete-orphan")
    decisions       = relationship("LifeDecision", back_populates="user", cascade="all, delete-orphan")
    subscription    = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resume_analyses = relationship("ResumeAnalysis", back_populates="user", cascade="all, delete-orphan")
    activity_logs   = relationship("UserActivityLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class UserProfile(Base):
    """Extended user profile — skills, education, career info"""
    __tablename__ = "profiles"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    age          = Column(Integer, nullable=True)
    user_type    = Column(String(50), nullable=True)   # student, professional, govt, etc.
    education    = Column(String(100), nullable=True)
    field        = Column(String(100), nullable=True)
    skills       = Column(JSON, default=list)           # ["Python", "React", ...]
    interests    = Column(JSON, default=list)           # ["AI/ML", "Design", ...]
    current_role = Column(String(200), nullable=True)
    industry     = Column(String(100), nullable=True)
    experience_years = Column(Float, nullable=True)
    monthly_salary   = Column(Float, nullable=True)
    annual_ctc       = Column(String(50), nullable=True)
    goals            = Column(Text, nullable=True)
    location         = Column(String(100), nullable=True)
    cibil_score      = Column(Integer, nullable=True)
    profile_score    = Column(Float, default=0.0)       # 0-100 completeness
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="profile")

    __table_args__ = (
        Index("idx_profile_user", "user_id"),
    )


class CareerPrediction(Base):
    """Career path predictions by the ML model"""
    __tablename__ = "career_predictions"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    input_skills    = Column(JSON)          # skills array used as input
    input_interests = Column(JSON)          # interests array
    input_education = Column(String(100))
    input_style     = Column(String(50))
    results         = Column(JSON)          # [{rank, title, match_score, ...}]
    model_version   = Column(String(20), default="v2.0")
    ml_scores       = Column(JSON, nullable=True)   # raw ML model output
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="predictions")

    __table_args__ = (
        Index("idx_career_pred_user", "user_id"),
        Index("idx_career_pred_date", "created_at"),
    )


class LifeDecision(Base):
    """Life decision AI analysis records"""
    __tablename__ = "decisions"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    input_data      = Column(JSON)          # all form inputs
    recommendation  = Column(String(200))
    confidence      = Column(Float)
    output          = Column(JSON)          # full AI output
    model_used      = Column(String(50))    # "claude" / "rule_based" / "rf_model"
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="decisions")

    __table_args__ = (
        Index("idx_decision_user", "user_id"),
    )


class ResumeAnalysis(Base):
    """Parsed resume data and skill extraction results"""
    __tablename__ = "resume_analyses"

    id                 = Column(Integer, primary_key=True, index=True)
    user_id            = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    original_filename  = Column(String(255))
    extracted_skills   = Column(JSON)       # NLP-extracted skills
    extracted_exp      = Column(Float)      # years of experience
    extracted_edu      = Column(String(200))
    skill_match_scores = Column(JSON)       # {role: match%}
    top_roles          = Column(JSON)       # recommended roles
    gap_analysis       = Column(JSON)       # skills to learn
    raw_text_preview   = Column(Text, nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="resume_analyses")


class Subscription(Base):
    """User subscription and billing"""
    __tablename__ = "subscriptions"

    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    plan              = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.free)
    status            = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.active)
    razorpay_order_id    = Column(String(100), nullable=True)
    razorpay_payment_id  = Column(String(100), nullable=True)
    razorpay_sub_id      = Column(String(100), nullable=True)
    amount_paid          = Column(Float, nullable=True)
    currency             = Column(String(10), default="INR")
    billing_cycle        = Column(String(20), default="monthly")  # monthly / annual
    started_at           = Column(DateTime(timezone=True), nullable=True)
    expires_at           = Column(DateTime(timezone=True), nullable=True)
    cancelled_at         = Column(DateTime(timezone=True), nullable=True)
    predictions_used     = Column(Integer, default=0)
    predictions_limit    = Column(Integer, default=5)  # free=5, pro=unlimited(-1)
    created_at           = Column(DateTime(timezone=True), server_default=func.now())
    updated_at           = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="subscription")


class JobMarketData(Base):
    """Real job market dataset — populated from Kaggle/scraped data"""
    __tablename__ = "job_market_data"

    id           = Column(Integer, primary_key=True, index=True)
    role         = Column(String(200), index=True)
    sector       = Column(Enum(SectorType), default=SectorType.private)
    industry     = Column(String(100))
    required_skills = Column(JSON)      # ["Python", "SQL", ...]
    min_salary   = Column(Float)        # in LPA
    max_salary   = Column(Float)        # in LPA
    avg_salary   = Column(Float)
    demand_level = Column(Enum(DemandLevel), default=DemandLevel.medium)
    demand_score = Column(Float, default=50.0)   # 0-100
    growth_rate  = Column(Float, default=0.0)    # YoY %
    location     = Column(String(100), default="India")
    top_companies   = Column(JSON)
    min_experience  = Column(Float, default=0.0)
    education_req   = Column(String(100))
    last_updated    = Column(DateTime(timezone=True), server_default=func.now())
    data_source     = Column(String(100), default="internal")

    __table_args__ = (
        Index("idx_job_role", "role"),
        Index("idx_job_sector", "sector"),
        Index("idx_job_demand", "demand_score"),
    )


class SkillTaxonomy(Base):
    """Skills taxonomy for NLP matching"""
    __tablename__ = "skill_taxonomy"

    id          = Column(Integer, primary_key=True, index=True)
    skill_name  = Column(String(100), unique=True, index=True)
    category    = Column(String(50))    # programming, cloud, soft_skill, etc.
    aliases     = Column(JSON)          # ["ML", "Machine Learning", "ml"]
    related_to  = Column(JSON)          # related skill IDs
    demand_score = Column(Float, default=50.0)
    growth_rate  = Column(Float, default=0.0)


class LoanData(Base):
    """Loan products from Indian banks"""
    __tablename__ = "loan_data"

    id            = Column(Integer, primary_key=True, index=True)
    bank_name     = Column(String(100))
    loan_type     = Column(String(50))   # education, home, personal, etc.
    min_rate      = Column(Float)        # interest rate %
    max_rate      = Column(Float)
    max_amount    = Column(Float)        # in rupees
    min_tenure    = Column(Integer)      # months
    max_tenure    = Column(Integer)
    processing_fee = Column(Float, nullable=True)
    features      = Column(JSON)
    eligibility   = Column(JSON)
    last_updated  = Column(DateTime(timezone=True), server_default=func.now())


class UserActivityLog(Base):
    """User activity tracking for personalization engine"""
    __tablename__ = "user_activity_logs"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    action      = Column(String(100))   # "career_predict", "decision_analyze", etc.
    details     = Column(JSON, nullable=True)
    ip_address  = Column(String(50), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="activity_logs")

    __table_args__ = (
        Index("idx_activity_user", "user_id"),
        Index("idx_activity_date", "created_at"),
    )


class APIKey(Base):
    """API keys for developer access"""
    __tablename__ = "api_keys"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    key_hash   = Column(String(255), unique=True)
    name       = Column(String(100))
    is_active  = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)   # requests/hour
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used  = Column(DateTime(timezone=True), nullable=True)


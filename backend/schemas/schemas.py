"""
Pydantic Schemas — Request & Response Validation
==================================================
All API input/output schemas with validation rules.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ══════════════════════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class SignupRequest(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    age: Optional[int] = Field(None, ge=14, le=70)
    user_type: Optional[str] = Field(None)  # student/professional/govt/entrepreneur
    education: Optional[str] = Field(None)

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


# ══════════════════════════════════════════════════════════════════════════════
# USER / PROFILE SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=14, le=70)
    user_type: Optional[str] = None
    education: Optional[str] = None
    field: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    current_role: Optional[str] = None
    industry: Optional[str] = None
    experience_years: Optional[float] = Field(None, ge=0, le=50)
    monthly_salary: Optional[float] = Field(None, ge=0)
    annual_ctc: Optional[str] = None
    goals: Optional[str] = None
    location: Optional[str] = None
    cibil_score: Optional[int] = Field(None, ge=300, le=900)


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    email: str
    role: str
    is_verified: bool
    profile_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    user_id: int
    age: Optional[int]
    user_type: Optional[str]
    education: Optional[str]
    field: Optional[str]
    skills: List[str]
    interests: List[str]
    current_role: Optional[str]
    industry: Optional[str]
    experience_years: Optional[float]
    monthly_salary: Optional[float]
    goals: Optional[str]
    profile_score: float

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# CAREER PREDICTION SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class CareerPredictRequest(BaseModel):
    skills: List[str] = Field(..., min_items=1, max_items=50)
    interests: Optional[List[str]] = Field(default_factory=list)
    education: str
    field: Optional[str] = None
    work_style: Optional[str] = None
    target_salary: Optional[str] = None
    location: Optional[str] = None
    include_government: Optional[bool] = True

    @validator("skills")
    def clean_skills(cls, v):
        return [s.strip() for s in v if s.strip()]


class CareerPath(BaseModel):
    rank: int
    title: str
    match_score: float
    demand: str
    salary_range: str
    description: str
    skills_gap: List[str]
    growth_rate: str
    top_companies: List[str]
    sector: str
    roadmap: Optional[List[str]] = None
    avg_time_to_role: Optional[str] = None


class CareerPredictResponse(BaseModel):
    prediction_id: int
    careers: List[CareerPath]
    model_version: str
    processing_time_ms: float
    created_at: datetime


# ══════════════════════════════════════════════════════════════════════════════
# LIFE DECISION SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class DecisionAnalyzeRequest(BaseModel):
    current_role: str = Field(..., min_length=2)
    industry: Optional[str] = None
    monthly_salary: Optional[float] = Field(None, ge=0)
    experience_years: Optional[float] = Field(None, ge=0, le=50)
    skills: Optional[List[str]] = Field(default_factory=list)
    primary_goal: str = Field(...)
    satisfaction_score: float = Field(..., ge=1, le=10)
    demand_score: float = Field(..., ge=1, le=10)
    additional_context: Optional[str] = Field(None, max_length=1000)


class DecisionResponse(BaseModel):
    decision_id: int
    recommendation: str
    confidence: float
    reasoning: str
    action_steps: List[str]
    timeline: str
    salary_potential: str
    risk_level: str
    sector_tip: Optional[str]
    model_used: str
    created_at: datetime


# ══════════════════════════════════════════════════════════════════════════════
# RESUME SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class ResumeAnalysisResponse(BaseModel):
    analysis_id: int
    extracted_skills: List[str]
    extracted_experience: float
    extracted_education: str
    skill_match_scores: Dict[str, float]  # {role: match_percentage}
    top_roles: List[Dict[str, Any]]
    gap_analysis: Dict[str, List[str]]   # {role: [missing_skills]}
    ats_score: float
    improvement_tips: List[str]
    created_at: datetime


# ══════════════════════════════════════════════════════════════════════════════
# LOAN SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class LoanPredictRequest(BaseModel):
    loan_type: str = Field(...)   # education, home, personal, vehicle, business, gold
    amount: float = Field(..., gt=0)
    tenure_years: float = Field(..., gt=0, le=30)
    monthly_income: float = Field(..., gt=0)
    employment_type: str
    age: int = Field(..., ge=18, le=75)
    existing_emis: float = Field(default=0.0, ge=0)
    cibil_score: int = Field(..., ge=300, le=900)
    property_value: Optional[float] = None
    institute_type: Optional[str] = None

    @validator("loan_type")
    def valid_loan_type(cls, v):
        valid = ["education", "home", "personal", "vehicle", "business", "gold"]
        if v not in valid:
            raise ValueError(f"Loan type must be one of: {valid}")
        return v


class BankRecommendation(BaseModel):
    bank_name: str
    interest_rate: str
    processing_fee: str
    max_amount: str
    special_features: List[str]


class LoanPredictResponse(BaseModel):
    eligibility_score: float       # 0-100
    is_eligible: bool
    emi_amount: float
    total_interest: float
    total_payable: float
    max_eligible_amount: float
    recommended_banks: List[BankRecommendation]
    improvement_tips: List[str]
    tax_benefits: Optional[str]
    processing_time: str


# ══════════════════════════════════════════════════════════════════════════════
# MARKET SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class MarketTrend(BaseModel):
    skill: str
    demand_score: float
    growth_rate: float
    avg_salary_premium: float
    job_count: int

class MarketTrendsResponse(BaseModel):
    trending_skills: List[MarketTrend]
    top_roles: List[Dict[str, Any]]
    salary_benchmarks: Dict[str, Dict[str, float]]
    city_wise_salaries: Dict[str, float]
    last_updated: datetime


# ══════════════════════════════════════════════════════════════════════════════
# SUBSCRIPTION SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class SubscriptionPlanInfo(BaseModel):
    plan: str
    price_monthly: float
    price_annual: float
    features: List[str]
    predictions_limit: int  # -1 = unlimited

class CreateOrderRequest(BaseModel):
    plan: str = Field(...)   # pro / enterprise
    billing_cycle: str = Field(default="monthly")  # monthly / annual

class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int   # in paise
    currency: str
    key_id: str
    plan: str

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan: str
    billing_cycle: str


# ══════════════════════════════════════════════════════════════════════════════
# GENERIC SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class HistoryResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    has_more: bool

class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    field: Optional[str] = None

"""Subscription Router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import hashlib, hmac, os
from models.database import (
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
    UserRole,
    get_db,
)
from routers.auth import get_current_user

router = APIRouter()
PLANS = {
    "free":       {"price_monthly": 0,   "price_annual": 0,    "predictions_limit": 5,  "features": ["5 free predictions","Basic career paths","Job market data","Loan check"]},
    "pro":        {"price_monthly": 99,  "price_annual": 999,  "predictions_limit": -1, "features": ["Unlimited predictions","Resume AI analysis","PDF reports","Priority AI","All sectors","Email support"]},
    "enterprise": {"price_monthly": 499, "price_annual": 4999, "predictions_limit": -1, "features": ["Everything in Pro","Team dashboard","API access","Dedicated support"]},
}

@router.get("/plans")
async def list_plans():
    return {"plans": [{"plan": k, **v} for k, v in PLANS.items()]}

@router.get("/status")
async def subscription_status(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    sub = result.scalar_one_or_none()
    if not sub:
        return {"plan": "free", "status": "active", "predictions_used": 0, "predictions_limit": 5}
    return {"plan": sub.plan.value, "status": sub.status.value, "predictions_used": sub.predictions_used, "predictions_limit": sub.predictions_limit, "expires_at": sub.expires_at.isoformat() if sub.expires_at else None}

@router.post("/create-order")
async def create_order(body: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    plan = body.get("plan", "pro")
    cycle = body.get("billing_cycle", "monthly")
    if plan not in PLANS or plan == "free":
        raise HTTPException(400, "Invalid plan")
    amount = PLANS[plan]["price_annual"] if cycle == "annual" else PLANS[plan]["price_monthly"]
    RZP_KEY = os.getenv("RAZORPAY_KEY_ID", "")
    try:
        if RZP_KEY:
            import razorpay
            client = razorpay.Client(auth=(RZP_KEY, os.getenv("RAZORPAY_KEY_SECRET", "")))
            order = client.order.create({"amount": int(amount*100), "currency": "INR"})
            order_id = order["id"]
        else:
            order_id = f"order_mock_{current_user.id}_{plan}"
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"order_id": order_id, "amount": int(amount*100), "currency": "INR", "key_id": RZP_KEY or "rzp_test_mock", "plan": plan}

@router.post("/verify-payment")
async def verify_payment(body: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    plan = body.get("plan", "pro")
    cycle = body.get("billing_cycle", "monthly")
    result = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    sub = result.scalar_one_or_none()
    if not sub:
        sub = Subscription(user_id=current_user.id)
        db.add(sub)
    expires = datetime.now(timezone.utc) + timedelta(days=365 if cycle == "annual" else 30)
    sub.plan = SubscriptionPlan(plan)
    sub.status = SubscriptionStatus.active
    sub.expires_at = expires
    sub.predictions_limit = -1
    current_user.role = UserRole.pro if plan in ("pro", "enterprise") else UserRole.free
    await db.commit()
    return {"success": True, "plan": plan, "expires_at": expires.isoformat(), "message": f"Welcome to PathMind {plan.capitalize()}!"}

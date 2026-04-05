"""Admin Router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.database import (
    CareerPrediction,
    LifeDecision,
    Subscription,
    SubscriptionPlan,
    User,
    get_db,
)
from routers.auth import get_current_user

router = APIRouter()

@router.get("/stats")
async def admin_stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role.value != "admin":
        raise HTTPException(403, "Admin only")
    users_count     = await db.execute(select(func.count(User.id)))
    careers_count   = await db.execute(select(func.count(CareerPrediction.id)))
    decisions_count = await db.execute(select(func.count(LifeDecision.id)))
    pro_count       = await db.execute(select(func.count(Subscription.id)).where(Subscription.plan == SubscriptionPlan.pro))
    return {
        "total_users": users_count.scalar(),
        "career_predictions": careers_count.scalar(),
        "life_decisions": decisions_count.scalar(),
        "pro_subscribers": pro_count.scalar(),
    }

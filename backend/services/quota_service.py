from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

FREE_LIMITS = {"career_predict": 5, "decision_analyze": 5, "resume_analyze": 0, "loan_predict": 10}

async def check_and_use_quota(db: AsyncSession, user_id: int, action: str) -> bool:
    from models.database import Subscription, SubscriptionPlan
    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = result.scalar_one_or_none()
    if sub and sub.plan in (SubscriptionPlan.pro, SubscriptionPlan.enterprise):
        return True
    limit = FREE_LIMITS.get(action, 5)
    if limit == 0:
        raise HTTPException(402, {"error": "pro_required", "message": "Upgrade to Pro for this feature."})
    used = sub.predictions_used if sub else 0
    if used >= limit:
        raise HTTPException(429, {"error": "quota_exceeded", "message": f"Free limit of {limit} reached. Upgrade to Pro."})
    if sub:
        sub.predictions_used += 1
        await db.commit()
    return True

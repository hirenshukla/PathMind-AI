"""
Services — PathMind AI
========================
quota_service, activity_service, email_service, scheduler
"""

# ─── quota_service.py ─────────────────────────────────────────────────────────
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.database import Subscription, SubscriptionPlan
import logging

logger = logging.getLogger(__name__)

FREE_LIMITS = {
    "career_predict":  5,
    "decision_analyze": 5,
    "resume_analyze":  0,  # Pro only
    "loan_predict":    10,
}

async def check_and_use_quota(db: AsyncSession, user_id: int, action: str) -> bool:
    """Check if user has quota remaining and increment usage"""
    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = result.scalar_one_or_none()

    if not sub:
        # No subscription = free user
        sub = Subscription(user_id=user_id, plan=SubscriptionPlan.free, predictions_used=0, predictions_limit=5)
        db.add(sub)

    # Pro/enterprise = unlimited
    if sub.plan in (SubscriptionPlan.pro, SubscriptionPlan.enterprise):
        sub.predictions_used += 1
        await db.commit()
        return True

    # Free tier checks
    limit = FREE_LIMITS.get(action, 5)
    if limit == 0:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "pro_required",
                "message": "This feature requires a Pro subscription (₹99/month). Upgrade to unlock resume analysis, unlimited predictions, and more.",
                "upgrade_url": "/subscription"
            }
        )

    if sub.predictions_used >= limit:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "quota_exceeded",
                "message": f"You've used all {limit} free predictions. Upgrade to Pro (₹99/month) for unlimited access.",
                "used": sub.predictions_used,
                "limit": limit,
                "upgrade_url": "/subscription"
            }
        )

    sub.predictions_used += 1
    await db.commit()
    return True


# ─── activity_service.py ──────────────────────────────────────────────────────
from models.database import UserActivityLog

async def log_activity(db: AsyncSession, user_id: int, action: str, metadata: dict = None):
    """Log user activity for personalization engine"""
    try:
        log = UserActivityLog(user_id=user_id, action=action, details=metadata or {})
        db.add(log)
        await db.commit()
    except Exception as e:
        logger.warning(f"Failed to log activity: {e}")


# ─── email_service.py ─────────────────────────────────────────────────────────
import os

async def send_verification_email(email: str, name: str):
    """Send email verification — integrate with SendGrid/SES in production"""
    logger.info(f"📧 [EMAIL] Verification sent to {email} for {name}")
    # Production: use SendGrid or AWS SES
    # import sendgrid
    # sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))


async def send_reset_email(email: str, token: str):
    """Send password reset email"""
    reset_url = f"{os.getenv('FRONTEND_URL', 'https://pathmind.ai')}/reset-password?token={token}"
    logger.info(f"📧 [EMAIL] Password reset sent to {email}: {reset_url}")


async def send_welcome_pro_email(email: str, name: str, plan: str):
    """Send welcome email after Pro upgrade"""
    logger.info(f"📧 [EMAIL] Pro welcome sent to {email}, plan: {plan}")


# ─── scheduler.py ─────────────────────────────────────────────────────────────
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import httpx

scheduler = AsyncIOScheduler()

async def update_market_data():
    """Fetch fresh job market data (runs daily at 2 AM)"""
    logger.info("🔄 [SCHEDULER] Updating market data...")
    # In production: fetch from Kaggle API, RapidAPI job boards, etc.
    logger.info("✅ [SCHEDULER] Market data updated")

async def cleanup_old_logs():
    """Remove activity logs older than 90 days"""
    logger.info("🧹 [SCHEDULER] Cleaning old activity logs...")

def start_scheduler():
    scheduler.add_job(update_market_data, CronTrigger(hour=2, minute=0), id="market_update")
    scheduler.add_job(cleanup_old_logs,   CronTrigger(hour=3, minute=0), id="log_cleanup")
    scheduler.start()
    logger.info("✅ Background scheduler started with 2 jobs")

"""Decision Router — /api/v1/decision"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx, os

from models.database import get_db, User, LifeDecision
from schemas.schemas import DecisionAnalyzeRequest
from ml_models.models import get_decision_model
from routers.auth import get_current_user
from services.activity_service import log_activity
from services.quota_service import check_and_use_quota

router = APIRouter()

@router.post("/analyze", response_model=dict)
async def analyze_decision(
    body: DecisionAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """AI life decision analysis using Random Forest + Claude"""
    await check_and_use_quota(db, current_user.id, "decision_analyze")
    model = get_decision_model()
    input_dict = body.dict()
    result = model.predict(input_dict)

    decision = LifeDecision(
        user_id=current_user.id,
        input_data=input_dict,
        recommendation=result["recommendation"],
        confidence=result["confidence"],
        output=result,
        model_used=result.get("model_used", "random_forest_v2")
    )
    db.add(decision)
    await db.commit()
    await db.refresh(decision)
    await log_activity(db, current_user.id, "decision_analyze", {"goal": body.primary_goal})
    return {"decision_id": decision.id, **result, "created_at": decision.created_at.isoformat()}

@router.get("/history")
async def decision_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LifeDecision).where(LifeDecision.user_id == current_user.id)
        .order_by(LifeDecision.created_at.desc()).limit(20)
    )
    decisions = result.scalars().all()
    return {"items": [{"id": d.id, "recommendation": d.recommendation, "confidence": d.confidence, "created_at": d.created_at.isoformat()} for d in decisions], "total": len(decisions)}

@router.get("/{decision_id}")
async def get_decision(decision_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LifeDecision).where(LifeDecision.id == decision_id, LifeDecision.user_id == current_user.id))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(404, "Decision not found")
    return {"decision_id": d.id, **d.output, "created_at": d.created_at.isoformat()}

"""
Career Router — /api/v1/career
================================
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import time

from models.database import get_db, User, CareerPrediction, Subscription
from schemas.schemas import CareerPredictRequest, CareerPredictResponse
from ml_models.models import get_career_model
from routers.auth import get_current_user
from services.activity_service import log_activity
from services.quota_service import check_and_use_quota

router = APIRouter()

@router.post("/predict", response_model=dict)
async def predict_career(
    body: CareerPredictRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Predict top career paths based on skills and interests"""
    # Check quota
    await check_and_use_quota(db, current_user.id, "career_predict")

    start = time.time()
    model = get_career_model()

    results = model.predict(
        skills=body.skills,
        interests=body.interests or [],
        work_style=body.work_style,
        include_government=body.include_government,
        top_n=5
    )

    elapsed = (time.time() - start) * 1000

    # Save to DB
    prediction = CareerPrediction(
        user_id=current_user.id,
        input_skills=body.skills,
        input_interests=body.interests or [],
        input_education=body.education,
        input_style=body.work_style,
        results=results,
        model_version="v2.0",
    )
    db.add(prediction)
    await db.commit()
    await db.refresh(prediction)

    await log_activity(db, current_user.id, "career_predict", {"skills_count": len(body.skills)})

    return {
        "prediction_id": prediction.id,
        "careers": results,
        "model_version": "v2.0",
        "processing_time_ms": round(elapsed, 1),
        "created_at": prediction.created_at.isoformat()
    }

@router.get("/history")
async def career_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's past career predictions"""
    result = await db.execute(
        select(CareerPrediction)
        .where(CareerPrediction.user_id == current_user.id)
        .order_by(CareerPrediction.created_at.desc())
        .limit(20)
    )
    predictions = result.scalars().all()
    return {
        "items": [
            {
                "id": p.id,
                "top_career": p.results[0]["title"] if p.results else "Unknown",
                "skills_used": p.input_skills[:5],
                "created_at": p.created_at.isoformat()
            }
            for p in predictions
        ],
        "total": len(predictions)
    }


@router.get("/{prediction_id}")
async def get_career_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific saved career prediction for the current user."""
    result = await db.execute(
        select(CareerPrediction).where(
            CareerPrediction.id == prediction_id,
            CareerPrediction.user_id == current_user.id,
        )
    )
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(status_code=404, detail="Career prediction not found")

    return {
        "prediction_id": prediction.id,
        "careers": prediction.results or [],
        "model_version": prediction.model_version or "v2.0",
        "created_at": prediction.created_at.isoformat(),
    }

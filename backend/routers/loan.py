"""Loan Router - /api/v1/loan"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ml_models.models import get_loan_model
from models.database import User, get_db
from routers.auth import get_current_user
from schemas.schemas import LoanPredictRequest
from services.activity_service import log_activity
from services.quota_service import check_and_use_quota

router = APIRouter()


@router.post("/predict", response_model=dict)
async def predict_loan(
    body: LoanPredictRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Predict loan eligibility for Indian loan products."""
    await check_and_use_quota(db, current_user.id, "loan_predict")

    model = get_loan_model()
    result = model.predict(body.dict())

    await log_activity(
        db,
        current_user.id,
        "loan_predict",
        {"loan_type": body.loan_type, "amount": body.amount},
    )

    return result

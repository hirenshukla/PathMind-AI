"""Users Router"""

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import CareerPrediction, LifeDecision, User, UserProfile, get_db
from routers.auth import get_current_user

router = APIRouter()


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()

    return {
        "user": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email,
            "role": current_user.role.value,
        },
        "profile": {
            "age": profile.age,
            "user_type": profile.user_type,
            "education": profile.education,
            "field": profile.field,
            "skills": profile.skills or [],
            "interests": profile.interests or [],
            "current_role": profile.current_role,
            "industry": profile.industry,
            "experience_years": profile.experience_years,
            "monthly_salary": profile.monthly_salary,
            "annual_ctc": profile.annual_ctc,
            "goals": profile.goals,
            "location": profile.location,
            "profile_score": profile.profile_score,
        }
        if profile
        else {},
    }


@router.put("/profile")
async def update_profile(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(user_id=current_user.id, skills=[], interests=[])
        db.add(profile)

    for field in [
        "age",
        "user_type",
        "education",
        "field",
        "skills",
        "interests",
        "current_role",
        "industry",
        "experience_years",
        "monthly_salary",
        "annual_ctc",
        "goals",
        "location",
    ]:
        if field in body:
            setattr(profile, field, body[field])

    score = 10.0
    if profile.age:
        score += 10
    if profile.education:
        score += 10
    if profile.skills:
        score += min(len(profile.skills) * 4, 20)
    if profile.interests:
        score += 10
    if profile.current_role:
        score += 10
    if profile.goals:
        score += 10
    if profile.monthly_salary:
        score += 5
    if profile.experience_years is not None:
        score += 5
    profile.profile_score = min(98, score)

    await db.commit()
    return {"message": "Profile updated", "profile_score": profile.profile_score}


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    career_res = await db.execute(
        select(CareerPrediction)
        .where(CareerPrediction.user_id == current_user.id)
        .order_by(CareerPrediction.created_at.desc())
    )
    dec_res = await db.execute(
        select(LifeDecision)
        .where(LifeDecision.user_id == current_user.id)
        .order_by(LifeDecision.created_at.desc())
    )
    prof_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))

    profile = prof_res.scalar_one_or_none()
    careers = career_res.scalars().all()
    decisions = dec_res.scalars().all()

    return {
        "stats": {
            "career_predictions": len(careers),
            "decisions_made": len(decisions),
            "profile_score": profile.profile_score if profile else 0,
            "skills_count": len(profile.skills or []) if profile else 0,
        },
        "user": {"first_name": current_user.first_name, "role": current_user.role.value},
        "recent_career": {
            "title": careers[0].results[0]["title"],
            "date": careers[0].created_at.isoformat(),
        }
        if careers and careers[0].results
        else None,
        "recent_decision": {
            "recommendation": decisions[0].recommendation,
            "confidence": decisions[0].confidence,
            "date": decisions[0].created_at.isoformat(),
        }
        if decisions
        else None,
    }


@router.get("/history")
async def get_full_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    career_res = await db.execute(
        select(CareerPrediction)
        .where(CareerPrediction.user_id == current_user.id)
        .order_by(CareerPrediction.created_at.desc())
        .limit(50)
    )
    dec_res = await db.execute(
        select(LifeDecision)
        .where(LifeDecision.user_id == current_user.id)
        .order_by(LifeDecision.created_at.desc())
        .limit(50)
    )

    careers = [
        {
            "type": "Career Predictor",
            "title": c.results[0]["title"] if c.results else "Career Analysis",
            "date": c.created_at.isoformat(),
            "id": c.id,
        }
        for c in career_res.scalars().all()
    ]
    decisions = [
        {
            "type": "Life Decision",
            "title": d.recommendation,
            "confidence": d.confidence,
            "date": d.created_at.isoformat(),
            "id": d.id,
        }
        for d in dec_res.scalars().all()
    ]

    combined = sorted(careers + decisions, key=lambda x: x["date"], reverse=True)
    return {"items": combined, "total": len(combined)}


@router.delete("/history")
async def clear_full_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear user's saved career/decision history."""
    await db.execute(delete(CareerPrediction).where(CareerPrediction.user_id == current_user.id))
    await db.execute(delete(LifeDecision).where(LifeDecision.user_id == current_user.id))
    await db.commit()
    return {"message": "History cleared"}

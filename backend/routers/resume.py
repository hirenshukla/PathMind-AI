"""Resume Router — /api/v1/resume (Pro feature)"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import io

from models.database import get_db, User, ResumeAnalysis
from ml_models.models import get_resume_model
from routers.auth import get_current_user_pro
from services.activity_service import log_activity
from services.quota_service import check_and_use_quota

router = APIRouter()

@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_pro),
    db: AsyncSession = Depends(get_db)
):
    """Parse resume PDF/TXT and extract skills, experience, career matches — Pro only"""
    if not file.filename.lower().endswith((".pdf", ".txt", ".docx")):
        raise HTTPException(400, "Only PDF, TXT files are supported")
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(413, "File too large — max 5MB")

    await check_and_use_quota(db, current_user.id, "resume_analyze")
    content = await file.read()

    text = ""
    if file.filename.lower().endswith(".pdf"):
        try:
            import PyPDF2
            pdf = PyPDF2.PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            raise HTTPException(422, f"Could not parse PDF: {e}")
    else:
        text = content.decode("utf-8", errors="ignore")

    if len(text.strip()) < 50:
        raise HTTPException(422, "Resume text too short — ensure file contains readable text")

    model = get_resume_model()
    result = model.analyze(text)

    analysis = ResumeAnalysis(
        user_id=current_user.id,
        original_filename=file.filename,
        extracted_skills=result["extracted_skills"],
        extracted_exp=result["extracted_experience"],
        extracted_edu=result["extracted_education"],
        skill_match_scores=result["skill_match_scores"],
        top_roles=[{"title": r["title"], "match_score": r["match_score"]} for r in result["top_roles"]],
        gap_analysis=result["gap_analysis"],
        raw_text_preview=text[:500]
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    await log_activity(db, current_user.id, "resume_analyze", {"filename": file.filename})
    return {"analysis_id": analysis.id, **result, "created_at": analysis.created_at.isoformat()}

@router.get("/history")
async def resume_history(current_user: User = Depends(get_current_user_pro), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(ResumeAnalysis).where(ResumeAnalysis.user_id == current_user.id).order_by(ResumeAnalysis.created_at.desc()).limit(10))
    items = result.scalars().all()
    return {"items": [{"id": i.id, "filename": i.original_filename, "top_role": i.top_roles[0]["title"] if i.top_roles else "N/A", "ats_score": i.skill_match_scores, "date": i.created_at.isoformat()} for i in items]}

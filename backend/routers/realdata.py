"""Real data router for government datasets and Google Trends."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter

from services.govdata_service import (
    fetch_education_data,
    fetch_employment_data,
    fetch_exam_notifications,
    fetch_government_jobs,
)
from services.trends_service import fetch_trending_skills_india

router = APIRouter(prefix="/api/v1/realdata", tags=["Real Data"])


@router.get("/government-jobs")
async def get_government_jobs():
    """Returns real government job listings from data.gov.in."""
    return await fetch_government_jobs()


@router.get("/education")
async def get_education_data():
    """Returns real education statistics."""
    return await fetch_education_data()


@router.get("/employment")
async def get_employment_data():
    """Returns real employment statistics."""
    return await fetch_employment_data()


@router.get("/exam-notifications")
async def get_exam_notifications():
    """Returns latest government exam notifications."""
    return await fetch_exam_notifications()


@router.get("/trending-skills")
async def get_trending_skills():
    """Returns trending skills from Google Trends India (cached)."""
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, fetch_trending_skills_india)
    return result

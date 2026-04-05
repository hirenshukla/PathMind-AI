"""Services for fetching real public datasets from data.gov.in."""

from __future__ import annotations

import os
from typing import Any

import httpx

GOV_API_KEY = (os.getenv("DATA_GOV_IN_API_KEY") or "").strip()
GOV_BASE_URL = "https://api.data.gov.in/resource"

# Live datasets selected from current data.gov.in catalog
NCS_STATE_VACANCIES_RESOURCE_ID = os.getenv(
    "DATA_GOV_IN_JOBS_STATE_RESOURCE_ID",
    "3bdd64bb-0b41-49e1-b79f-55638daa21b4",
)
NCS_SECTOR_VACANCIES_RESOURCE_ID = os.getenv(
    "DATA_GOV_IN_JOBS_SECTOR_RESOURCE_ID",
    "de038507-bfe4-449f-88c1-ba7e385e0304",
)
EDUCATION_DROPOUT_RESOURCE_ID = os.getenv(
    "DATA_GOV_IN_EDUCATION_RESOURCE_ID",
    "7167e28b-24d6-4a35-859b-19a999f8e50d",
)
EMPLOYMENT_SKILL_RESOURCE_ID = os.getenv(
    "DATA_GOV_IN_EMPLOYMENT_RESOURCE_ID",
    "2336747c-4982-4cde-8f98-7290796c5020",
)
EXAM_NOTIFICATIONS_RESOURCE_ID = os.getenv(
    "DATA_GOV_IN_EXAM_RESOURCE_ID",
    "a1b091fc-f688-47ba-b927-4ba495f0b763",
)


def _to_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


async def _fetch_resource(
    resource_id: str,
    *,
    limit: int = 20,
    offset: int = 0,
    retries: int = 2,
) -> dict[str, Any]:
    if not GOV_API_KEY:
        return {
            "success": False,
            "data": [],
            "total": 0,
            "resource_id": resource_id,
            "source": "data.gov.in",
            "error": "Missing DATA_GOV_IN_API_KEY environment variable",
        }

    params = {
        "api-key": GOV_API_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset,
    }

    last_error = ""
    for _ in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=18.0) as client:
                response = await client.get(f"{GOV_BASE_URL}/{resource_id}", params=params)
                response.raise_for_status()
                payload = response.json()
                records = payload.get("records", []) or []
                return {
                    "success": True,
                    "data": records,
                    "total": payload.get("total", len(records)),
                    "resource_id": resource_id,
                    "source": "data.gov.in",
                }
        except Exception as exc:
            last_error = str(exc).strip() or repr(exc)

    return {
        "success": False,
        "data": [],
        "total": 0,
        "resource_id": resource_id,
        "source": "data.gov.in",
        "error": last_error,
    }


async def fetch_government_jobs() -> dict[str, Any]:
    """Fetch real government vacancy data from NCS datasets."""
    state_data, sector_data = await _fetch_resource(
        NCS_STATE_VACANCIES_RESOURCE_ID,
        limit=100,
    ), await _fetch_resource(
        NCS_SECTOR_VACANCIES_RESOURCE_ID,
        limit=100,
    )

    state_jobs: list[dict[str, Any]] = []
    sector_jobs: list[dict[str, Any]] = []

    if state_data.get("success"):
        for row in state_data.get("data", []):
            if not isinstance(row, dict):
                continue
            state = row.get("state_ut") or row.get("state") or "India"
            vacancies = _to_int(row.get("number_of_vacancies"))
            label = str(state)
            if any(
                skip in label.lower()
                for skip in ("grand total", "multiple states", "pan india", "pan-india", "all india")
            ):
                continue

            state_jobs.append(
                {
                    "post_name": f"NCS Vacancies - {state}",
                    "department": "National Career Service (MoLE)",
                    "organization": "Government of India",
                    "vacancies": vacancies,
                    "category": "State-wise",
                    "source_resource": NCS_STATE_VACANCIES_RESOURCE_ID,
                }
            )

    if sector_data.get("success"):
        for row in sector_data.get("data", []):
            if not isinstance(row, dict):
                continue
            sector = row.get("sector_wise") or row.get("sector") or "General"
            vacancies = _to_int(row.get("number_of_vacancies"))
            label = str(sector)
            if any(skip in label.lower() for skip in ("grand total", "all sectors")):
                continue

            sector_jobs.append(
                {
                    "post_name": f"{sector} Vacancies (NCS)",
                    "department": "National Career Service (MoLE)",
                    "organization": "Government of India",
                    "vacancies": vacancies,
                    "category": "Sector-wise",
                    "source_resource": NCS_SECTOR_VACANCIES_RESOURCE_ID,
                }
            )

    state_jobs.sort(key=lambda item: item.get("vacancies", 0), reverse=True)
    sector_jobs.sort(key=lambda item: item.get("vacancies", 0), reverse=True)
    jobs = (state_jobs[:14] + sector_jobs[:6]) if (state_jobs or sector_jobs) else []

    return {
        "success": len(jobs) > 0,
        "data": jobs[:20],
        "total": len(jobs),
        "source": "data.gov.in",
        "datasets": [NCS_STATE_VACANCIES_RESOURCE_ID, NCS_SECTOR_VACANCIES_RESOURCE_ID],
    }


async def fetch_education_data() -> dict[str, Any]:
    """Fetch real education statistics."""
    raw = await _fetch_resource(EDUCATION_DROPOUT_RESOURCE_ID, limit=50)
    if not raw.get("success"):
        return raw

    records = []
    for row in raw.get("data", []):
        if not isinstance(row, dict):
            continue
        records.append(
            {
                "state_ut": row.get("india_state_ut"),
                "primary_dropout_2023_24": row.get("dropout_rate_2023_24___primary"),
                "upper_primary_dropout_2023_24": row.get("dropout_rate_2023_24___upper_primary"),
                "secondary_dropout_2023_24": row.get("dropout_rate_2023_24___secondary"),
            }
        )

    return {
        "success": True,
        "data": records,
        "total": len(records),
        "source": "data.gov.in",
        "dataset": EDUCATION_DROPOUT_RESOURCE_ID,
    }


async def fetch_employment_data() -> dict[str, Any]:
    """Fetch real employment/skill statistics."""
    raw = await _fetch_resource(EMPLOYMENT_SKILL_RESOURCE_ID, limit=100)
    if not raw.get("success"):
        return raw

    records = []
    for row in raw.get("data", []):
        if not isinstance(row, dict):
            continue
        records.append(
            {
                "state_ut": row.get("state_ut"),
                "pmkvy_enrolment_2022_23": row.get("_2022_23"),
                "pmkvy_enrolment_2023_24": row.get("_2023_24"),
                "pmkvy_enrolment_2024_25": row.get("_2024_25"),
            }
        )

    return {
        "success": True,
        "data": records,
        "total": len(records),
        "source": "data.gov.in",
        "dataset": EMPLOYMENT_SKILL_RESOURCE_ID,
    }


async def fetch_exam_notifications() -> dict[str, Any]:
    """Fetch real exam notifications/updates from government exam dataset."""
    raw = await _fetch_resource(EXAM_NOTIFICATIONS_RESOURCE_ID, limit=20)
    if not raw.get("success"):
        return {
            "success": False,
            "notifications": [],
            "source": "data.gov.in",
            "dataset": EXAM_NOTIFICATIONS_RESOURCE_ID,
            "error": raw.get("error", ""),
        }

    notifications = []
    for row in raw.get("data", []):
        if not isinstance(row, dict):
            continue
        notifications.append(
            {
                "title": row.get("exam") or "Government Exam Update",
                "candidates": row.get("candidates"),
                "centres": row.get("centres_"),
                "cities": row.get("_cities_"),
                "shifts": row.get("shifts"),
                "source": "Railway Recruitment Boards (via data.gov.in)",
            }
        )

    return {
        "success": True,
        "notifications": notifications,
        "source": "data.gov.in",
        "dataset": EXAM_NOTIFICATIONS_RESOURCE_ID,
        "last_updated": "live",
    }

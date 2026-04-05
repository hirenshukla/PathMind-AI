"""Google Trends integration for live skill trends in India."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from pytrends.request import TrendReq

_cache: dict[str, Any] = {"data": None, "timestamp": 0.0}
CACHE_DURATION = 3600  # 1 hour

_TREND_QUERIES = [
    "AI Machine Learning jobs India",
    "AWS Cloud jobs India",
    "Cybersecurity jobs India",
    "Python developer jobs India",
    "React developer jobs India",
]

_TREND_LABELS = [
    "AI / Generative AI",
    "AWS / Cloud",
    "Cybersecurity",
    "Python",
    "React / Next.js",
]


def fetch_trending_skills_india() -> dict[str, Any]:
    """Fetch real trending skills from Google Trends (with in-memory cache)."""
    global _cache

    if (time.time() - _cache["timestamp"]) < CACHE_DURATION and _cache["data"] is not None:
        cached_payload = dict(_cache["data"])
        cached_payload["cached"] = True
        return cached_payload

    try:
        pytrends = TrendReq(hl="en-IN", tz=330, timeout=(10, 25))
        pytrends.build_payload(_TREND_QUERIES, cat=0, timeframe="today 1-m", geo="IN")
        interest_data = pytrends.interest_over_time()

        if interest_data.empty:
            fallback = get_fallback_skills()
            _cache = {"data": fallback, "timestamp": time.time()}
            return fallback

        latest = interest_data.iloc[-1]
        skills = []
        for idx, label in enumerate(_TREND_LABELS):
            value = int(latest.iloc[idx])
            skills.append(
                {
                    "skill": label,
                    "trend_score": value,
                    "display": f"+{value}%",
                    "source": "Google Trends India",
                    "updated": datetime.now().strftime("%Y-%m-%d"),
                }
            )

        skills.sort(key=lambda item: item["trend_score"], reverse=True)
        result = {"success": True, "skills": skills, "cached": False}
        _cache = {"data": result, "timestamp": time.time()}
        return result
    except Exception:
        fallback = get_fallback_skills()
        _cache = {"data": fallback, "timestamp": time.time()}
        return fallback


def get_fallback_skills() -> dict[str, Any]:
    """Fallback data when Google Trends is unavailable."""
    return {
        "success": False,
        "skills": [
            {"skill": "AI / Generative AI", "trend_score": 67, "display": "+67%"},
            {"skill": "AWS / Cloud", "trend_score": 42, "display": "+42%"},
            {"skill": "Cybersecurity", "trend_score": 38, "display": "+38%"},
            {"skill": "Python", "trend_score": 31, "display": "+31%"},
            {"skill": "React / Next.js", "trend_score": 22, "display": "+22%"},
        ],
        "cached": False,
    }


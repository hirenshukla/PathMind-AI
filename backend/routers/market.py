"""Market Router — /api/v1/market"""
from fastapi import APIRouter
from datetime import datetime, timezone
router = APIRouter()

MARKET_DATA = {
    "trending_skills": [
        {"skill": "Generative AI / LLMs",    "demand_score": 95, "growth_rate": 67, "avg_salary_premium": 42, "job_count": 45000},
        {"skill": "Cloud Computing (AWS)",    "demand_score": 88, "growth_rate": 42, "avg_salary_premium": 28, "job_count": 120000},
        {"skill": "Cybersecurity",            "demand_score": 82, "growth_rate": 38, "avg_salary_premium": 25, "job_count": 35000},
        {"skill": "DevOps / Kubernetes",      "demand_score": 79, "growth_rate": 41, "avg_salary_premium": 30, "job_count": 60000},
        {"skill": "React / Next.js",          "demand_score": 77, "growth_rate": 22, "avg_salary_premium": 15, "job_count": 180000},
        {"skill": "Python",                   "demand_score": 74, "growth_rate": 31, "avg_salary_premium": 20, "job_count": 220000},
        {"skill": "Data Science",             "demand_score": 80, "growth_rate": 45, "avg_salary_premium": 35, "job_count": 75000},
        {"skill": "Rust / Go",                "demand_score": 58, "growth_rate": 45, "avg_salary_premium": 38, "job_count": 8000},
    ],
    "salary_benchmarks": {
        "ML Engineer":      {"min": 12, "max": 50, "median": 22, "yoy_growth": 15},
        "Full Stack Dev":   {"min": 8,  "max": 30, "median": 14, "yoy_growth": 12},
        "Data Scientist":   {"min": 10, "max": 35, "median": 16, "yoy_growth": 13},
        "Cloud Architect":  {"min": 15, "max": 50, "median": 22, "yoy_growth": 18},
        "DevOps Engineer":  {"min": 12, "max": 42, "median": 19, "yoy_growth": 14},
        "Product Manager":  {"min": 12, "max": 40, "median": 20, "yoy_growth": 10},
        "Cybersecurity":    {"min": 10, "max": 38, "median": 17, "yoy_growth": 16},
        "UI/UX Designer":   {"min": 6,  "max": 25, "median": 12, "yoy_growth": 9},
        "IAS Officer":      {"min": 6.73, "max": 30, "median": 12, "yoy_growth": 5},
    },
    "city_wise_salaries": {
        "Bengaluru": 18.2, "Hyderabad": 16.8, "Mumbai": 15.4,
        "Pune": 14.1, "Delhi NCR": 13.8, "Chennai": 13.2,
        "Noida": 12.6, "Ahmedabad": 10.2, "Kolkata": 9.8,
    },
    "job_growth_trend": {
        "2020": {"tech_total": 850,  "ai_ml": 40},
        "2021": {"tech_total": 920,  "ai_ml": 80},
        "2022": {"tech_total": 1050, "ai_ml": 160},
        "2023": {"tech_total": 1180, "ai_ml": 310},
        "2024": {"tech_total": 1420, "ai_ml": 580},
    }
}

@router.get("/trends")
async def get_market_trends():
    return {**MARKET_DATA, "last_updated": datetime.now(timezone.utc).isoformat()}

@router.get("/salary/{role}")
async def get_salary_benchmark(role: str):
    data = MARKET_DATA["salary_benchmarks"]
    for key in data:
        if role.lower() in key.lower():
            return {**data[key], "role": key}
    return {"role": role, "min": 6, "max": 25, "median": 12, "note": "Estimate"}

@router.get("/skills/trending")
async def get_trending_skills(limit: int = 10):
    skills = sorted(MARKET_DATA["trending_skills"], key=lambda x: x["growth_rate"], reverse=True)
    return {"skills": skills[:limit]}

@router.get("/cities")
async def get_city_salaries():
    cities = [{"city": c, "avg_salary_lpa": s} for c, s in MARKET_DATA["city_wise_salaries"].items()]
    return {"cities": sorted(cities, key=lambda x: x["avg_salary_lpa"], reverse=True)}

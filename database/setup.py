import asyncio
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/pathmind_db",
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_tables():
    """Create all tables."""
    from models.database import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[ok] All tables created")


async def seed_job_market_data():
    """Seed initial job market data."""
    from models.database import DemandLevel, JobMarketData, SectorType

    job_data = [
        {
            "role": "ML / AI Engineer",
            "sector": SectorType.private,
            "industry": "Technology",
            "required_skills": ["Python", "TensorFlow", "PyTorch", "ML"],
            "min_salary": 12.0,
            "max_salary": 50.0,
            "avg_salary": 22.0,
            "demand_level": DemandLevel.high,
            "demand_score": 95.0,
            "growth_rate": 67.0,
            "top_companies": ["Google", "Microsoft", "Amazon", "Flipkart"],
            "min_experience": 2.0,
            "education_req": "B.Tech/M.Tech CS",
        },
        {
            "role": "Full Stack Developer",
            "sector": SectorType.private,
            "industry": "Technology",
            "required_skills": ["React", "Node.js", "JavaScript", "SQL"],
            "min_salary": 8.0,
            "max_salary": 30.0,
            "avg_salary": 14.0,
            "demand_level": DemandLevel.high,
            "demand_score": 88.0,
            "growth_rate": 28.0,
            "top_companies": ["Swiggy", "Zepto", "Razorpay", "Meesho"],
            "min_experience": 1.0,
            "education_req": "Any CS/IT degree",
        },
        {
            "role": "Data Scientist",
            "sector": SectorType.both,
            "industry": "Analytics",
            "required_skills": ["Python", "SQL", "Pandas", "ML", "Statistics"],
            "min_salary": 10.0,
            "max_salary": 35.0,
            "avg_salary": 16.0,
            "demand_level": DemandLevel.high,
            "demand_score": 85.0,
            "growth_rate": 45.0,
            "top_companies": ["Amazon", "Walmart Labs", "PhonePe"],
            "min_experience": 1.5,
            "education_req": "Statistics/CS degree",
        },
        {
            "role": "Cloud DevOps Engineer",
            "sector": SectorType.private,
            "industry": "Technology",
            "required_skills": ["AWS", "Kubernetes", "Docker", "Terraform"],
            "min_salary": 14.0,
            "max_salary": 45.0,
            "avg_salary": 22.0,
            "demand_level": DemandLevel.high,
            "demand_score": 85.0,
            "growth_rate": 52.0,
            "top_companies": ["Amazon", "Microsoft", "Google"],
            "min_experience": 2.0,
            "education_req": "CS/IT degree",
        },
        {
            "role": "IAS Officer",
            "sector": SectorType.government,
            "industry": "Government",
            "required_skills": ["UPSC", "Governance", "Public Policy", "GK"],
            "min_salary": 6.73,
            "max_salary": 30.0,
            "avg_salary": 12.0,
            "demand_level": DemandLevel.high,
            "demand_score": 90.0,
            "growth_rate": 2.0,
            "top_companies": ["Government of India"],
            "min_experience": 0.0,
            "education_req": "Any Degree",
        },
        {
            "role": "Product Manager",
            "sector": SectorType.private,
            "industry": "Technology",
            "required_skills": ["Product Strategy", "SQL", "Agile", "UX"],
            "min_salary": 12.0,
            "max_salary": 40.0,
            "avg_salary": 20.0,
            "demand_level": DemandLevel.medium,
            "demand_score": 75.0,
            "growth_rate": 22.0,
            "top_companies": ["Ola", "CRED", "Groww", "Razorpay"],
            "min_experience": 3.0,
            "education_req": "Any degree + MBA preferred",
        },
        {
            "role": "Cybersecurity Analyst",
            "sector": SectorType.both,
            "industry": "Security",
            "required_skills": ["Security", "SIEM", "Penetration Testing", "Network"],
            "min_salary": 10.0,
            "max_salary": 38.0,
            "avg_salary": 17.0,
            "demand_level": DemandLevel.high,
            "demand_score": 82.0,
            "growth_rate": 38.0,
            "top_companies": ["TCS", "IBM", "Wipro", "Palo Alto"],
            "min_experience": 1.0,
            "education_req": "CS/IT degree + CISSP/CEH",
        },
    ]

    async with AsyncSessionLocal() as session:
        for data in job_data:
            session.add(JobMarketData(**data))
        await session.commit()
    print(f"[ok] Seeded {len(job_data)} job market records")


async def seed_loan_data():
    """Seed bank loan products."""
    from models.database import LoanData

    loans = [
        {
            "bank_name": "SBI",
            "loan_type": "education",
            "min_rate": 8.1,
            "max_rate": 11.15,
            "max_amount": 3000000,
            "min_tenure": 12,
            "max_tenure": 180,
            "features": ["No collateral for <7.5L", "Tax benefit 80E", "Moratorium period"],
            "eligibility": {"min_age": 18, "max_age": 35, "min_marks": 50},
        },
        {
            "bank_name": "HDFC Credila",
            "loan_type": "education",
            "min_rate": 9.55,
            "max_rate": 13.0,
            "max_amount": 10000000,
            "min_tenure": 12,
            "max_tenure": 120,
            "features": ["Abroad study", "Pre-admission approval", "Co-applicant allowed"],
            "eligibility": {},
        },
        {
            "bank_name": "SBI",
            "loan_type": "home",
            "min_rate": 8.4,
            "max_rate": 8.7,
            "max_amount": 100000000,
            "min_tenure": 12,
            "max_tenure": 360,
            "features": ["Lowest rates", "Women -0.05%", "Free CIBIL"],
            "eligibility": {"min_cibil": 650},
        },
        {
            "bank_name": "HDFC",
            "loan_type": "home",
            "min_rate": 8.5,
            "max_rate": 9.0,
            "max_amount": 100000000,
            "min_tenure": 12,
            "max_tenure": 360,
            "features": ["Quick approval", "Doorstep service", "Balance transfer"],
            "eligibility": {},
        },
        {
            "bank_name": "HDFC",
            "loan_type": "personal",
            "min_rate": 10.5,
            "max_rate": 21.0,
            "max_amount": 4000000,
            "min_tenure": 12,
            "max_tenure": 60,
            "features": ["Instant disbursal", "No collateral", "Digital process"],
            "eligibility": {"min_cibil": 700},
        },
        {
            "bank_name": "SBI XPRESS Credit",
            "loan_type": "personal",
            "min_rate": 11.0,
            "max_rate": 15.0,
            "max_amount": 2000000,
            "min_tenure": 6,
            "max_tenure": 60,
            "features": ["Pre-approved for salary accounts", "Lowest rate for govt employees"],
            "eligibility": {"employment": "salaried"},
        },
    ]

    async with AsyncSessionLocal() as session:
        for data in loans:
            session.add(LoanData(**data))
        await session.commit()
    print(f"[ok] Seeded {len(loans)} loan products")


async def seed_skill_taxonomy():
    """Seed skills taxonomy for NLP matching."""
    from models.database import SkillTaxonomy

    skills = [
        {
            "skill_name": "Python",
            "category": "programming",
            "aliases": ["python3", "py"],
            "demand_score": 74.0,
            "growth_rate": 31.0,
        },
        {
            "skill_name": "JavaScript",
            "category": "programming",
            "aliases": ["js", "es6", "vanilla js"],
            "demand_score": 72.0,
            "growth_rate": 18.0,
        },
        {
            "skill_name": "React",
            "category": "web_framework",
            "aliases": ["reactjs", "react.js"],
            "demand_score": 77.0,
            "growth_rate": 22.0,
        },
        {
            "skill_name": "AWS",
            "category": "cloud",
            "aliases": ["amazon web services", "ec2", "s3", "lambda"],
            "demand_score": 88.0,
            "growth_rate": 42.0,
        },
        {
            "skill_name": "Machine Learning",
            "category": "ai_ml",
            "aliases": ["ml", "machine-learning", "supervised learning"],
            "demand_score": 95.0,
            "growth_rate": 67.0,
        },
        {
            "skill_name": "SQL",
            "category": "database",
            "aliases": ["mysql", "postgresql", "sqlite", "structured query language"],
            "demand_score": 70.0,
            "growth_rate": 10.0,
        },
        {
            "skill_name": "Docker",
            "category": "devops",
            "aliases": ["containerization", "container"],
            "demand_score": 79.0,
            "growth_rate": 38.0,
        },
        {
            "skill_name": "Kubernetes",
            "category": "devops",
            "aliases": ["k8s", "container orchestration"],
            "demand_score": 78.0,
            "growth_rate": 41.0,
        },
        {
            "skill_name": "TensorFlow",
            "category": "ai_ml",
            "aliases": ["tf", "tensorflow 2"],
            "demand_score": 82.0,
            "growth_rate": 55.0,
        },
        {
            "skill_name": "Figma",
            "category": "design",
            "aliases": ["figma design", "ui design"],
            "demand_score": 65.0,
            "growth_rate": 24.0,
        },
    ]

    async with AsyncSessionLocal() as session:
        for data in skills:
            session.add(SkillTaxonomy(**data, related_to=[]))
        await session.commit()
    print(f"[ok] Seeded {len(skills)} skill taxonomy records")


async def create_admin_user():
    """Create default admin account."""
    import bcrypt
    from models.database import (
        Subscription,
        SubscriptionPlan,
        SubscriptionStatus,
        User,
        UserProfile,
        UserRole,
    )

    async with AsyncSessionLocal() as session:
        existing = await session.execute(select(User).where(User.email == "admin@pathmind.ai"))
        if existing.scalar_one_or_none():
            print("[ok] Admin user already exists: admin@pathmind.ai")
            return

        # IMPORTANT: Change this password immediately after first login in production!
        hashed = bcrypt.hashpw(b"Adm!n@PathMind#2026Secure", bcrypt.gensalt(12)).decode()
        admin = User(
            first_name="PathMind",
            last_name="Admin",
            email="admin@pathmind.ai",
            hashed_password=hashed,
            role=UserRole.admin,
            is_active=True,
            is_verified=True,
        )
        session.add(admin)
        await session.flush()

        session.add(UserProfile(user_id=admin.id, skills=["Python", "FastAPI", "AI"], profile_score=100.0))
        session.add(
            Subscription(
                user_id=admin.id,
                plan=SubscriptionPlan.enterprise,
                status=SubscriptionStatus.active,
                predictions_limit=-1,
            )
        )
        await session.commit()

    print("[ok] Admin user created: admin@pathmind.ai / Adm!n@PathMind#2026Secure")


async def main():
    print("\n[setup] PathMind AI Database Setup")
    print("=" * 50)
    await create_tables()
    await seed_job_market_data()
    await seed_loan_data()
    await seed_skill_taxonomy()
    await create_admin_user()
    print("\n[ok] Database setup complete!")
    print("[next] Run the API: uvicorn main:app --reload")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

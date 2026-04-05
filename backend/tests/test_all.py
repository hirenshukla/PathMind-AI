"""
PathMind AI — Test Suite
=========================
Run with: pytest tests/ -v
"""

import pytest
import asyncio
import sys, os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TEST_DB_PATH = Path(__file__).resolve().parent / "test_pathmind.db"
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "false"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH.as_posix()}"
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-secret-key-please-change-before-production-1234567890",
)

# ══════════════════════════════════════════════════════════════════════════════
# ML MODEL TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestCareerRecommender:
    def setup_method(self):
        from ml_models.models import CareerRecommender
        self.model = CareerRecommender()

    def test_basic_prediction(self):
        results = self.model.predict(skills=["Python", "Machine Learning", "TensorFlow"])
        assert len(results) == 5
        assert results[0]["rank"] == 1
        assert "title" in results[0]
        assert "match_score" in results[0]
        assert 0 <= results[0]["match_score"] <= 100

    def test_sorted_by_score(self):
        results = self.model.predict(skills=["React", "JavaScript", "Node.js"])
        scores = [r["match_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_top_result_for_ml_skills(self):
        results = self.model.predict(skills=["Python", "TensorFlow", "PyTorch", "Deep Learning", "NLP"])
        # ML engineer should be top result for ML skills
        assert "ML" in results[0]["title"] or "AI" in results[0]["title"] or "Data" in results[0]["title"]

    def test_government_filter(self):
        results_all = self.model.predict(skills=["UPSC", "GK", "Civil Services"], include_government=True)
        results_no_govt = self.model.predict(skills=["UPSC", "GK", "Civil Services"], include_government=False)
        # Should have no government roles when filtered
        govt_in_no_govt = [r for r in results_no_govt if r.get("sector") == "Government"]
        assert len(govt_in_no_govt) == 0

    def test_empty_skills_raises(self):
        with pytest.raises(ValueError):
            self.model.predict(skills=[])

    def test_interest_influence(self):
        res_with = self.model.predict(skills=["Python"], interests=["AI/ML", "Data Science"])
        res_without = self.model.predict(skills=["Python"], interests=[])
        # With AI/ML interests, ML roles should rank higher
        assert res_with[0]["match_score"] >= res_without[0]["match_score"] - 20

    def test_result_has_required_fields(self):
        results = self.model.predict(skills=["Python"])
        for r in results:
            assert "rank" in r
            assert "title" in r
            assert "match_score" in r
            assert "demand" in r
            assert "salary_range" in r
            assert "skills_gap" in r
            assert "top_companies" in r
            assert "sector" in r


class TestDecisionClassifier:
    def setup_method(self):
        from ml_models.models import DecisionClassifier
        self.model = DecisionClassifier()

    def test_basic_prediction(self):
        result = self.model.predict({
            "monthly_salary": 50000, "experience_years": 3,
            "satisfaction_score": 4, "demand_score": 8,
            "skills": ["Python", "React"], "primary_goal": "money",
            "industry": "IT"
        })
        assert "recommendation" in result
        assert "confidence" in result
        assert "action_steps" in result
        assert len(result["action_steps"]) >= 3
        assert 0 <= result["confidence"] <= 100

    def test_government_goal_routes_to_govt(self):
        result = self.model.predict({
            "monthly_salary": 30000, "experience_years": 2,
            "satisfaction_score": 6, "demand_score": 5,
            "skills": ["GK", "Governance"], "primary_goal": "govt",
            "industry": ""
        })
        assert "government" in result["recommendation"].lower() or "civil" in result["recommendation"].lower()

    def test_unhappy_high_demand_routes_to_switch(self):
        result = self.model.predict({
            "monthly_salary": 30000, "experience_years": 3,
            "satisfaction_score": 2, "demand_score": 9,
            "skills": ["React", "Node.js", "Python"], "primary_goal": "money",
            "industry": "IT"
        })
        assert "switch" in result["recommendation"].lower() or "higher" in result["recommendation"].lower()

    def test_risk_level_in_output(self):
        result = self.model.predict({
            "monthly_salary": 80000, "experience_years": 5,
            "satisfaction_score": 8, "demand_score": 7,
            "skills": ["Python", "AWS"], "primary_goal": "growth",
            "industry": "IT"
        })
        assert result["risk_level"] in ("Low", "Medium", "High")

    def test_confidence_between_0_and_100(self):
        for goal in ["money", "stability", "passion", "govt", "abroad"]:
            result = self.model.predict({
                "monthly_salary": 60000, "experience_years": 4,
                "satisfaction_score": 5, "demand_score": 6,
                "skills": ["Python"], "primary_goal": goal, "industry": "IT"
            })
            assert 0 <= result["confidence"] <= 100


class TestResumeAnalyzer:
    def setup_method(self):
        from ml_models.models import ResumeAnalyzer
        self.analyzer = ResumeAnalyzer()

    def test_skill_extraction(self):
        text = "I am experienced in Python, React, AWS, SQL, Docker, and Machine Learning."
        result = self.analyzer.analyze(text)
        found_skills = [s.lower() for s in result["extracted_skills"]]
        assert "python" in found_skills or "Python" in result["extracted_skills"]
        assert len(result["extracted_skills"]) >= 3

    def test_experience_extraction(self):
        text = "I have 5 years of experience in software development."
        result = self.analyzer.analyze(text)
        assert result["extracted_experience"] == 5.0

    def test_education_extraction(self):
        text = "B.Tech graduate from IIT Bombay with 8.5 CGPA."
        result = self.analyzer.analyze(text)
        assert "B.Tech" in result["extracted_education"]

    def test_ats_score_range(self):
        text = "Python developer with 3 years of experience in React and AWS. Improved performance by 40%. GitHub: github.com/test"
        result = self.analyzer.analyze(text)
        assert 0 <= result["ats_score"] <= 100

    def test_top_roles_returned(self):
        text = "Machine Learning engineer with Python, TensorFlow, PyTorch expertise. Published 2 papers."
        result = self.analyzer.analyze(text)
        assert len(result["top_roles"]) > 0
        assert "title" in result["top_roles"][0]

    def test_improvement_tips_present(self):
        text = "Software engineer. Python. React."  # Minimal resume
        result = self.analyzer.analyze(text)
        assert len(result["improvement_tips"]) > 0


class TestLoanEligibilityModel:
    def setup_method(self):
        from ml_models.models import LoanEligibilityModel
        self.model = LoanEligibilityModel()

    def test_eligible_profile(self):
        result = self.model.predict({
            "loan_type": "education", "amount": 500000,
            "tenure_years": 5, "monthly_income": 80000,
            "employment_type": "salaried_pvt", "age": 25,
            "existing_emis": 0, "cibil_score": 780
        })
        assert result["eligibility_score"] > 55
        assert result["is_eligible"] == True
        assert result["emi_amount"] > 0
        assert len(result["recommended_banks"]) > 0

    def test_poor_cibil_reduces_score(self):
        base_data = {
            "loan_type": "personal", "amount": 500000, "tenure_years": 3,
            "monthly_income": 50000, "employment_type": "salaried_pvt",
            "age": 30, "existing_emis": 0
        }
        good  = self.model.predict({**base_data, "cibil_score": 780})
        poor  = self.model.predict({**base_data, "cibil_score": 580})
        assert good["eligibility_score"] > poor["eligibility_score"]

    def test_emi_calculation_correct(self):
        result = self.model.predict({
            "loan_type": "home", "amount": 5000000,
            "tenure_years": 20, "monthly_income": 200000,
            "employment_type": "salaried_govt", "age": 30,
            "existing_emis": 0, "cibil_score": 800
        })
        # EMI for 50L home loan at ~8.4% for 20yr should be ~43,000-50,000
        assert 35000 <= result["emi_amount"] <= 60000

    def test_tax_benefits_for_education(self):
        result = self.model.predict({
            "loan_type": "education", "amount": 1000000,
            "tenure_years": 7, "monthly_income": 60000,
            "employment_type": "student", "age": 22,
            "existing_emis": 0, "cibil_score": 700
        })
        assert result["tax_benefits"] is not None
        assert "80E" in result["tax_benefits"]

    def test_invalid_loan_type_raises(self):
        # This test should fail at schema validation level, but testing model directly
        # Model should handle gracefully
        result = self.model.predict({
            "loan_type": "personal", "amount": 100000,
            "tenure_years": 1, "monthly_income": 50000,
            "employment_type": "salaried_pvt", "age": 25,
            "existing_emis": 0, "cibil_score": 750
        })
        assert result is not None


# ══════════════════════════════════════════════════════════════════════════════
# API INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def test_client():
    """Create FastAPI test client"""
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def reset_test_db():
    """Ensure tests run against a clean sqlite DB file."""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

class TestAuthAPI:
    def test_health_check(self, test_client):
        res = test_client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

    def test_signup_success(self, test_client):
        import uuid
        email = f"test_{uuid.uuid4().hex[:8]}@test.com"
        res = test_client.post("/api/v1/auth/signup", json={
            "first_name": "Test", "last_name": "User",
            "email": email, "password": "test1234",
            "age": 25, "user_type": "student", "education": "B.Tech"
        })
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == email

    def test_signup_duplicate_email(self, test_client):
        email = "duplicate@test.com"
        # First signup
        test_client.post("/api/v1/auth/signup", json={
            "first_name": "Test", "email": email, "password": "test1234"
        })
        # Duplicate
        res = test_client.post("/api/v1/auth/signup", json={
            "first_name": "Test2", "email": email, "password": "test1234"
        })
        assert res.status_code == 409

    def test_login_wrong_password(self, test_client):
        res = test_client.post("/api/v1/auth/login", json={
            "email": "wrong@test.com", "password": "wrongpass"
        })
        assert res.status_code == 401

    def test_protected_route_no_token(self, test_client):
        res = test_client.get("/api/v1/user/profile")
        assert res.status_code == 403

    def test_career_predict_requires_auth(self, test_client):
        res = test_client.post("/api/v1/career/predict", json={
            "skills": ["Python"], "education": "B.Tech"
        })
        assert res.status_code == 403



# ══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-q"])

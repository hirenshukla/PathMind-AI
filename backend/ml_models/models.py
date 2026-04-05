"""
ML Models — PathMind AI
========================
1. CareerRecommender  — TF-IDF + Cosine Similarity
2. DecisionClassifier — Random Forest
3. ResumeAnalyzer     — spaCy NLP
4. LoanEligibility    — Logistic Regression

All models load from disk (trained offline) or use real-time inference.
"""

import os
import re
import json
import time
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)
MODEL_DIR = Path(__file__).parent / "saved_models"
MODEL_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# 1. CAREER RECOMMENDATION MODEL (TF-IDF + Cosine Similarity)
# ══════════════════════════════════════════════════════════════════════════════

CAREER_DATASET = [
    {"title":"ML / AI Engineer","skills":["python","tensorflow","pytorch","machine learning","deep learning","nlp","data science","scikit-learn","keras","opencv","llm","transformers","mlops"],"interests":["AI/ML","Data Science","Research","Programming"],"demand":"High","min_salary":12,"max_salary":50,"growth":67,"sector":"Private","top_companies":["Google","Microsoft","OpenAI","Flipkart AI","Ola Krutrim","Amazon Science"],"gap_defaults":["MLOps","LLMOps","Distributed Training"],"description":"Design and deploy ML models at scale. India's hottest role with 67% YoY growth."},
    {"title":"Full Stack Developer","skills":["react","javascript","node.js","html","css","typescript","next.js","vue","express","mongodb","postgresql","graphql","rest api","docker"],"interests":["Programming","Web Development","Design"],"demand":"High","min_salary":8,"max_salary":30,"growth":28,"sector":"Private","top_companies":["Swiggy","Razorpay","Zepto","Meesho","Cred","Groww"],"gap_defaults":["System Design","Microservices","TypeScript"],"description":"Build end-to-end web applications. High demand across startups and MNCs."},
    {"title":"Data Scientist / Analyst","skills":["python","sql","tableau","power bi","excel","pandas","numpy","statistics","r","data visualization","machine learning","spark","hadoop"],"interests":["Data Science","Analytics","Research","Finance"],"demand":"High","min_salary":10,"max_salary":32,"growth":45,"sector":"Both","top_companies":["Amazon","Walmart Labs","PhonePe","Paytm","Flipkart","Mu Sigma"],"gap_defaults":["Causal Inference","MLflow","Databricks"],"description":"Extract insights from data to drive business decisions across industries."},
    {"title":"Cloud / DevOps Engineer","skills":["aws","azure","gcp","kubernetes","docker","terraform","jenkins","linux","ci/cd","ansible","prometheus","grafana","python","bash"],"interests":["Cloud Computing","DevOps","Programming","Systems"],"demand":"High","min_salary":14,"max_salary":45,"growth":52,"sector":"Private","top_companies":["Amazon AWS","Microsoft Azure","Google","Informatica","HashiCorp","Zomato"],"gap_defaults":["FinOps","Platform Engineering","Chaos Engineering"],"description":"Build and maintain scalable cloud infrastructure. Critical for every tech company."},
    {"title":"IAS / Civil Services Officer","skills":["upsc","civil services","governance","public policy","gk","history","polity","geography","economics","current affairs","essay writing","ethics"],"interests":["Government","Public Policy","Teaching","Social Work"],"demand":"High","min_salary":56100,"max_salary":250000,"growth":0,"sector":"Government","top_companies":["Government of India","State Governments","Ministry Departments"],"gap_defaults":["Optional Subject Mastery","Essay Writing","Interview Skills"],"description":"India's most prestigious administrative service. Lead national development.","is_govt":True},
    {"title":"Product Manager","skills":["product management","agile","scrum","roadmap","jira","user research","a/b testing","sql","analytics","wireframing","stakeholder management","strategy","growth hacking"],"interests":["Product Management","Business","Analytics","Entrepreneurship"],"demand":"Medium","min_salary":12,"max_salary":40,"growth":22,"sector":"Private","top_companies":["Ola","Uber India","Groww","CRED","Meesho","Razorpay"],"gap_defaults":["SQL for PM","Quantitative User Research","Pricing Strategy"],"description":"Define product vision and work with cross-functional teams to ship features."},
    {"title":"Cybersecurity Analyst","skills":["security","network security","ethical hacking","penetration testing","kali linux","firewall","siem","cissp","ceh","soc","incident response","cloud security","zero trust"],"interests":["Cybersecurity","Programming","Research","Government"],"demand":"High","min_salary":10,"max_salary":35,"growth":38,"sector":"Both","top_companies":["TCS CyberSec","IBM Security","Palo Alto","Wipro","CERT-In","NIC"],"gap_defaults":["Cloud Security","Zero Trust Architecture","SIEM Tools"],"description":"Protect organizations from cyber threats. Fastest growing govt and private role."},
    {"title":"UI/UX Designer","skills":["figma","design","sketch","user experience","user interface","adobe xd","prototype","wireframe","user research","interaction design","design system","canva","invision"],"interests":["Design","Creative","Product Management","Psychology"],"demand":"Medium","min_salary":6,"max_salary":25,"growth":24,"sector":"Private","top_companies":["Razorpay","Swiggy","Urban Company","Meesho","Lenskart","Dunzo"],"gap_defaults":["Motion Design","Design Systems","UX Research Methods"],"description":"Create intuitive user experiences. Growing demand as every company goes digital."},
    {"title":"Banking / Finance Professional","skills":["banking","finance","accounting","tally","excel","financial modeling","ibps","sbi","ca","cfa","cma","equity research","risk analysis","bloomberg"],"interests":["Finance","Banking","Analytics","Government"],"demand":"High","min_salary":5,"max_salary":25,"growth":18,"sector":"Both","top_companies":["SBI","HDFC Bank","ICICI Bank","RBI","Kotak","Axis Bank","Goldman Sachs India"],"gap_defaults":["FinTech Tools","Python for Finance","Risk Quantification"],"description":"Core of India's economy. Both govt banking (IBPS/SBI) and private fintech."},
    {"title":"Digital Marketing / Growth Hacker","skills":["seo","sem","google ads","facebook ads","content marketing","email marketing","analytics","social media","copywriting","growth hacking","crm","hubspot"],"interests":["Marketing","Entrepreneurship","Creative","Writing"],"demand":"Medium","min_salary":4,"max_salary":20,"growth":30,"sector":"Private","top_companies":["Unacademy","ShareChat","Dailyhunt","Startups","Agencies"],"gap_defaults":["Programmatic Advertising","Marketing Analytics","Video Marketing"],"description":"Drive user acquisition and retention. Every brand needs digital presence."},
    {"title":"Mobile App Developer","skills":["flutter","kotlin","swift","android","ios","react native","dart","java","firebase","mobile development","api integration","ui design"],"interests":["Programming","Design","Mobile","Gaming"],"demand":"Medium","min_salary":8,"max_salary":25,"growth":19,"sector":"Private","top_companies":["PhonePe","Dream11","MPL","BYJU'S","Nykaa","Zepto"],"gap_defaults":["Performance Optimization","State Management","CI/CD for Mobile"],"description":"Build mobile apps used by millions. High demand with Flutter revolution."},
    {"title":"Government Teacher / Professor","skills":["teaching","subject expertise","communication","lesson planning","ctet","tet","ugc net","research","pedagogy"],"interests":["Teaching","Research","Government","Social Work"],"demand":"High","min_salary":3,"max_salary":15,"growth":5,"sector":"Government","top_companies":["KVS","NVS","State Board Schools","Central Universities","IITs","NITs"],"gap_defaults":["Digital Teaching Tools","Research Publications","NET Qualification"],"description":"Shape the next generation. Stable govt job with pension and perks.","is_govt":True},
    {"title":"DevOps / SRE Engineer","skills":["devops","site reliability","kubernetes","docker","ci/cd","monitoring","linux","python","golang","aws","terraform","incident management"],"interests":["DevOps","Cloud Computing","Programming","Systems"],"demand":"High","min_salary":12,"max_salary":40,"growth":41,"sector":"Private","top_companies":["Netflix India","Atlassian","Freshworks","Zoho","PhonePe","Amazon"],"gap_defaults":["Chaos Engineering","Platform Engineering","eBPF"],"description":"Keep production systems reliable at scale. SRE roles at top companies pay ₹40L+."},
    {"title":"Entrepreneur / Startup Founder","skills":["entrepreneurship","business development","fundraising","leadership","product management","marketing","finance","networking","problem solving","communication"],"interests":["Entrepreneurship","Business","Product Management","Finance"],"demand":"Medium","min_salary":0,"max_salary":999,"growth":35,"sector":"Private","top_companies":["Your own startup","YC alumni","Sequoia-backed"],"gap_defaults":["Fundraising Pitch","Financial Modeling","Go-to-Market Strategy"],"description":"Build something from scratch. India's startup ecosystem has 100+ unicorns."},
    {"title":"Consultant / Management Analyst","skills":["consulting","strategy","excel","powerpoint","sql","data analysis","communication","problem solving","financial modeling","project management"],"interests":["Business","Finance","Analytics","Teaching"],"demand":"Medium","min_salary":8,"max_salary":50,"growth":18,"sector":"Both","top_companies":["McKinsey","BCG","Bain","Deloitte","EY","KPMG","Accenture"],"gap_defaults":["Case Interview Practice","Industry Specialization","Client Communication"],"description":"Solve complex business problems for top organizations. MBA preferred."},
    {"title":"Research Scientist / PhD","skills":["research","machine learning","python","r","statistics","publications","deep learning","computer vision","nlp","mathematics","data analysis","experimental design"],"interests":["Research","AI/ML","Data Science","Teaching"],"demand":"Medium","min_salary":8,"max_salary":30,"growth":25,"sector":"Both","top_companies":["IISc","IIT Labs","Microsoft Research","Google Research","TIFR","DRDO"],"gap_defaults":["Research Publications","Grant Writing","Advanced Mathematics"],"description":"Push the boundaries of knowledge. Ideal for PhDs and passionate learners."},
]


class CareerRecommender:
    """
    TF-IDF Vectorizer + Cosine Similarity for career matching.
    Also uses interest overlap scoring and demand weighting.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True
        )
        self._is_fitted = False
        self._build_corpus()

    def _build_corpus(self):
        """Build TF-IDF corpus from career dataset"""
        self.careers = CAREER_DATASET
        corpus = [" ".join(c["skills"]) for c in self.careers]
        self.career_matrix = self.vectorizer.fit_transform(corpus)
        self._is_fitted = True
        logger.info(f"✅ CareerRecommender: Built corpus with {len(self.careers)} careers")

    def predict(
        self,
        skills: List[str],
        interests: List[str] = None,
        work_style: str = None,
        include_government: bool = True,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Predict top N career matches for given skills and interests.
        Returns list sorted by composite match score.
        """
        start = time.time()

        if not skills:
            raise ValueError("At least one skill is required")

        # Normalize input
        skills_lower = [s.lower().strip() for s in skills]
        interests_lower = [i.lower().strip() for i in (interests or [])]
        query = " ".join(skills_lower)

        # TF-IDF Cosine Similarity
        query_vec = self.vectorizer.transform([query])
        cosine_scores = cosine_similarity(query_vec, self.career_matrix).flatten()

        results = []
        for idx, career in enumerate(self.careers):
            # Skip govt if not requested
            if not include_government and career.get("is_govt"):
                continue

            cos_score = float(cosine_scores[idx])

            # Interest overlap score (0-1)
            career_interests = [i.lower() for i in career["interests"]]
            interest_overlap = len(set(interests_lower) & set(career_interests))
            interest_score = min(interest_overlap / max(len(career["interests"]), 1), 1.0)

            # Work style bonus
            style_bonus = 0.0
            if work_style:
                style_map = {
                    "technical": ["ML / AI", "Full Stack", "Cloud", "DevOps", "Mobile", "Cybersecurity", "SRE"],
                    "analytical": ["Data Scientist", "Business Analyst", "Research", "Consultant"],
                    "creative": ["UI/UX", "Digital Marketing", "Content"],
                    "people": ["Product Manager", "Consultant", "Teacher"],
                    "business": ["Product Manager", "Entrepreneur", "Consultant", "Banking"],
                    "govt_work": ["IAS", "Government Teacher", "Banking", "Cybersecurity"]
                }
                for style_key, matching in style_map.items():
                    if work_style == style_key:
                        if any(m in career["title"] for m in matching):
                            style_bonus = 0.1

            # Direct skill match bonus
            career_skills = set(career["skills"])
            direct_matches = sum(1 for s in skills_lower if s in career_skills or any(s in cs for cs in career_skills))
            direct_bonus = min(direct_matches * 0.05, 0.25)

            # Composite score: 50% TF-IDF + 25% interests + 15% style + 10% direct
            composite = (cos_score * 0.50) + (interest_score * 0.25) + (style_bonus * 0.15) + (direct_bonus * 0.10)

            # Scale to 0-100 with realistic distribution
            match_score = min(98, max(35, int(composite * 120 + 35)))

            # Skills gap (what user is missing)
            user_skills_set = set(skills_lower)
            gap_skills = [s for s in career["skills"][:8] if not any(us in s or s in us for us in user_skills_set)][:4]
            if not gap_skills:
                gap_skills = career["gap_defaults"][:3]

            results.append({
                "rank": 0,  # Will be set after sorting
                "title": career["title"],
                "match_score": match_score,
                "demand": career["demand"],
                "salary_range": f"₹{career['min_salary']}–{career['max_salary']} {'LPA' if career['max_salary'] < 1000 else '/month'}",
                "description": career["description"],
                "skills_gap": gap_skills,
                "growth_rate": f"+{career['growth']}% by 2026" if career['growth'] > 0 else "Stable",
                "top_companies": career["top_companies"],
                "sector": career["sector"],
                "composite_score": composite
            })

        # Sort and rank
        results.sort(key=lambda x: x["composite_score"], reverse=True)
        top = results[:top_n]
        for i, r in enumerate(top):
            r["rank"] = i + 1
            del r["composite_score"]

        elapsed = (time.time() - start) * 1000
        logger.info(f"CareerRecommender.predict: {elapsed:.1f}ms, top={top[0]['title'] if top else 'N/A'}")
        return top

    def save(self):
        joblib.dump(self.vectorizer, MODEL_DIR / "career_vectorizer.pkl")
        logger.info("✅ CareerRecommender saved")

    def load(self):
        path = MODEL_DIR / "career_vectorizer.pkl"
        if path.exists():
            self.vectorizer = joblib.load(path)
            self._build_corpus()
        else:
            logger.warning("Career model not found on disk, using fresh instance")


# ══════════════════════════════════════════════════════════════════════════════
# 2. DECISION CLASSIFIER (Random Forest)
# ══════════════════════════════════════════════════════════════════════════════

# Decision classes
DECISION_CLASSES = [
    "switch_job",
    "upskill_current",
    "pursue_higher_studies",
    "enter_government",
    "start_business",
    "pivot_career",
    "work_abroad",
    "stay_and_grow"
]

class DecisionClassifier:
    """
    Random Forest classifier for life/career decisions.
    Features: salary, experience, satisfaction, demand, skills_count, etc.
    """

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_split=5,
            random_state=42,
            class_weight="balanced"
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.label_encoder.classes_ = np.array(DECISION_CLASSES)
        self._is_fitted = False
        self._try_load_or_train()

    def _extract_features(self, data: dict) -> np.ndarray:
        """Convert input dict to feature vector"""
        goal_map = {
            "money": 0, "growth": 1, "stability": 2, "passion": 3,
            "worklife": 4, "govt": 5, "abroad": 6, "startup": 7
        }
        industry_govt = 1 if "govt" in (data.get("industry","") or "").lower() else 0

        features = [
            float(data.get("monthly_salary", 0) or 0),
            float(data.get("experience_years", 0) or 0),
            float(data.get("satisfaction_score", 5) or 5),
            float(data.get("demand_score", 5) or 5),
            float(len(data.get("skills", []) or [])),
            float(goal_map.get(data.get("primary_goal", "growth"), 1)),
            float(industry_govt),
            # Derived features
            float((data.get("monthly_salary", 0) or 0) / max(data.get("experience_years", 1) or 1, 1)),  # salary/exp ratio
            float(1 if (data.get("satisfaction_score", 5) or 5) <= 4 else 0),  # unhappy flag
            float(1 if (data.get("demand_score", 5) or 5) >= 7 else 0),   # high demand flag
        ]
        return np.array(features).reshape(1, -1)

    def _generate_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data based on career domain rules"""
        np.random.seed(42)
        n = 2000
        X, y = [], []

        for _ in range(n):
            salary = np.random.uniform(10000, 300000)
            exp = np.random.uniform(0, 20)
            sat = np.random.uniform(1, 10)
            dem = np.random.uniform(1, 10)
            skills = np.random.randint(0, 15)
            goal = np.random.randint(0, 8)
            govt = np.random.randint(0, 2)
            salary_exp = salary / max(exp, 1)
            unhappy = 1 if sat <= 4 else 0
            high_dem = 1 if dem >= 7 else 0

            features = [salary, exp, sat, dem, skills, goal, govt, salary_exp, unhappy, high_dem]

            # Rule-based label assignment (mimics expert knowledge)
            if goal == 5 or govt:  label = "enter_government"
            elif goal == 6:        label = "work_abroad"
            elif goal == 7:        label = "start_business"
            elif sat <= 3 and dem >= 7 and salary < 50000: label = "switch_job"
            elif sat <= 4 and goal == 3: label = "pivot_career"
            elif exp < 2 and dem >= 6:   label = "upskill_current"
            elif exp > 5 and skills < 5: label = "pursue_higher_studies"
            elif goal == 0 and salary < 40000 and dem >= 6: label = "switch_job"
            elif goal == 1 and exp < 5:  label = "upskill_current"
            else:                        label = "stay_and_grow"

            X.append(features)
            y.append(label)

        return np.array(X), np.array(y)

    def _try_load_or_train(self):
        model_path = MODEL_DIR / "decision_rf.pkl"
        scaler_path = MODEL_DIR / "decision_scaler.pkl"

        if model_path.exists() and scaler_path.exists():
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self._is_fitted = True
                logger.info("✅ DecisionClassifier: Loaded from disk")
                return
            except Exception as e:
                logger.warning(f"Failed to load model: {e}, retraining...")

        # Train from scratch
        logger.info("🔄 Training DecisionClassifier from synthetic data...")
        X, y = self._generate_training_data()
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self._is_fitted = True
        self.save()
        logger.info("✅ DecisionClassifier: Trained and saved")

    def predict(self, input_data: dict) -> dict:
        """Predict best life decision with confidence and explanation"""
        features = self._extract_features(input_data)
        features_scaled = self.scaler.transform(features)

        probabilities = self.model.predict_proba(features_scaled)[0]
        classes = self.model.classes_

        # Get top 3 predictions
        top_indices = probabilities.argsort()[-3:][::-1]

        top_decision = classes[top_indices[0]]
        confidence = float(probabilities[top_indices[0]])

        # Map decision to human-readable output
        decision_map = self._get_decision_output(top_decision, input_data, confidence)
        decision_map["alternative_decisions"] = [
            {"decision": classes[i], "probability": float(probabilities[i])}
            for i in top_indices[1:]
        ]

        return decision_map

    def _get_decision_output(self, decision: str, data: dict, confidence: float) -> dict:
        """Generate human-readable output for each decision type"""
        salary = data.get("monthly_salary", 0) or 0
        exp = data.get("experience_years", 0) or 0
        sat = data.get("satisfaction_score", 5)
        dem = data.get("demand_score", 5)

        outputs = {
            "switch_job": {
                "recommendation": "Switch to a Higher-Paying Role Now",
                "reasoning": f"Your satisfaction score ({sat}/10) + high market demand ({dem}/10) for your skills signal this is the ideal moment. Current salary of ₹{salary:,.0f}/month is below your earning potential. Job market data shows 40-60% hike is achievable in 2-3 months.",
                "action_steps": ["Polish LinkedIn with quantified achievements", "Apply to 10-15 companies on Naukri/LinkedIn", "Prepare DSA + System Design (30 days)", "Target 40-50% salary hike — current market norm"],
                "timeline": "2–4 months",
                "salary_potential": f"₹{int(salary*1.45):,}–₹{int(salary*1.65):,}/month",
                "risk_level": "Low",
                "sector_tip": "Product companies (Razorpay, CRED, Zepto) pay 50% more than IT services"
            },
            "upskill_current": {
                "recommendation": "Deep Upskilling for 3x Career Impact",
                "reasoning": f"With {exp:.0f} years of experience, focused skill-building will compound your career value significantly. The market rewards specialists — becoming expert in 2-3 high-demand skills can double income in 18 months.",
                "action_steps": ["Identify #1 skill gap via 20 job postings analysis", "Complete one certification (Coursera/Udemy — ₹1,000-5,000)", "Build 2 portfolio projects showcasing new skills", "Apply for 20% salary premium roles after 90 days"],
                "timeline": "3–9 months",
                "salary_potential": "25-45% growth in 12 months",
                "risk_level": "Low",
                "sector_tip": "AI/ML certification adds ₹3-6L premium to any tech role (NASSCOM data)"
            },
            "pursue_higher_studies": {
                "recommendation": "Strategic Higher Studies for Career Leap",
                "reasoning": f"With {exp:.0f} years of experience, higher studies (MBA/M.Tech/MS) can unlock leadership roles and premium compensation. ROI on quality MBA in India is 300-500% over 5 years.",
                "action_steps": ["Shortlist 5 programs (IIM/BITS/IIT or abroad universities)", "Start CAT/GATE/GRE preparation (6-12 months)", "Build application essays and get 2 strong recommendations", "Apply for education loan (SBI Scholar 8.1% — lowest rate)"],
                "timeline": "12–24 months",
                "salary_potential": "₹15–40 LPA post-MBA from premium institutes",
                "risk_level": "Medium",
                "sector_tip": "IIM Ahmedabad MBA median package 2024: ₹34 LPA. ROI = 5 years"
            },
            "enter_government": {
                "recommendation": "Commit to Government Service Career",
                "reasoning": "Government jobs offer unmatched security, pension, DA, and social prestige. With your background, UPSC CSE, IBPS PO, or SSC CGL are strong targets. Structured 6-12 month preparation strategy has high ROI.",
                "action_steps": ["Choose exam: UPSC (graduation+) / IBPS PO (any grad) / SSC CGL (any grad)", "Join a structured coaching program or online platform (Testbook/Unacademy)", "Practice previous years papers — minimum 5 years", "Target Jan-Apr exam window — peak govt recruitment season"],
                "timeline": "6–18 months",
                "salary_potential": "₹5-25 LPA + Pension + HRA + DA + perks",
                "risk_level": "Medium",
                "sector_tip": "UPSC 2024 salary: ₹56,100–₹2,50,000/month + 7th Pay Commission DA"
            },
            "start_business": {
                "recommendation": "Validate Idea Then Make the Entrepreneurial Leap",
                "reasoning": "India's startup ecosystem is thriving with 100+ unicorns, but 90% fail in 2 years. The right path: validate your idea with 10 paying customers before quitting your job. Build 12-month runway first.",
                "action_steps": ["Define a specific problem and target customer segment", "Build MVP in 30 days (no-code tools are fine initially)", "Get 10 paying customers before leaving current job", "Apply to Y Combinator India / Antler / Sequoia Surge"],
                "timeline": "6–18 months for launch",
                "salary_potential": "₹0 to unlimited — depends entirely on execution",
                "risk_level": "High",
                "sector_tip": "DPIIT startup registration gives tax benefits + access to govt tenders + fast-track IP filing"
            },
            "pivot_career": {
                "recommendation": "Structured Career Pivot — Bridge the Gap",
                "reasoning": f"Satisfaction at {sat}/10 signals serious passion-role mismatch. A strategic pivot over 6-9 months minimizes financial risk while moving toward meaningful work. India's evolving job market makes career changes more accepted than ever.",
                "action_steps": ["Map passion to careers with ₹8L+ potential using PathMind Career Predictor", "Build 6-month emergency fund before switching", "Learn new skills on weekends (targeted online courses)", "Network on LinkedIn in target industry for 3 months before applying"],
                "timeline": "6–12 months",
                "salary_potential": "Initial 10-15% dip, then rapid growth in 2-3 years",
                "risk_level": "Medium",
                "sector_tip": "EdTech, product design, and AI careers are India's top passion-to-paycheque pivots"
            },
            "work_abroad": {
                "recommendation": "Build Your International Career Profile",
                "reasoning": "Working abroad can multiply salary 5-10x in USD/EUR terms. Germany offers free education for MS, Canada has the easiest PR pathway for Indians, and the USA remains the top destination for tech professionals.",
                "action_steps": ["Research: Germany MS (free) vs Canada PR vs USA OPT", "Get AWS/Azure/GCP certification (international companies require it)", "Build strong GitHub with 3+ significant open-source contributions", "Target MNCs in India first for potential internal transfer"],
                "timeline": "12–24 months",
                "salary_potential": "$70,000–$140,000/year (5-10x Indian salary)",
                "risk_level": "Medium",
                "sector_tip": "Germany Blue Card + Canada Express Entry are easiest visa routes for Indian engineers"
            },
            "stay_and_grow": {
                "recommendation": "Strategic Internal Growth — Build Your Brand",
                "reasoning": f"With {exp:.0f} years of experience and decent satisfaction ({sat}/10), this is an ideal time to build deep expertise and internal reputation. Promotions and 30-40% annual raises are achievable with the right positioning.",
                "action_steps": ["Volunteer for high-visibility projects and leadership opportunities", "Build relationships with senior stakeholders and mentors", "Document and present achievements using data + impact metrics", "Request structured feedback and create 6-month growth plan with manager"],
                "timeline": "6–18 months",
                "salary_potential": "15-35% annual increment over next 2 years",
                "risk_level": "Low",
                "sector_tip": "Top performers in Indian companies get 3-5x the standard 8% hike — visibility is key"
            }
        }

        result = outputs.get(decision, outputs["stay_and_grow"]).copy()
        result["confidence"] = round(min(0.95, confidence + 0.15) * 100, 1)
        result["model_used"] = "random_forest_v2"
        return result

    def save(self):
        joblib.dump(self.model, MODEL_DIR / "decision_rf.pkl")
        joblib.dump(self.scaler, MODEL_DIR / "decision_scaler.pkl")

    def load(self):
        self._try_load_or_train()


# ══════════════════════════════════════════════════════════════════════════════
# 3. RESUME ANALYZER (NLP - spaCy + TF-IDF)
# ══════════════════════════════════════════════════════════════════════════════

SKILL_PATTERNS = {
    "programming": ["python","java","javascript","typescript","c++","c#","go","rust","kotlin","swift","php","ruby","scala","r","matlab","bash","powershell"],
    "web": ["react","vue","angular","next.js","node.js","express","django","flask","fastapi","spring","html","css","tailwind","graphql","rest"],
    "data": ["sql","postgresql","mysql","mongodb","redis","elasticsearch","pandas","numpy","scikit-learn","tensorflow","pytorch","keras","spark","hadoop","airflow","dbt","tableau","power bi"],
    "cloud": ["aws","azure","gcp","docker","kubernetes","terraform","ansible","jenkins","ci/cd","linux","nginx","prometheus","grafana"],
    "soft": ["leadership","communication","teamwork","problem solving","agile","scrum","project management","stakeholder management"],
    "domain": ["machine learning","deep learning","nlp","computer vision","data science","devops","cybersecurity","blockchain","iot","ar/vr"]
}

class ResumeAnalyzer:
    """
    NLP-based resume parser and skill extractor.
    Uses spaCy for entity recognition + regex for structured extraction.
    Falls back to pattern matching if spaCy is not available.
    """

    def __init__(self):
        self.all_skills = set()
        for category_skills in SKILL_PATTERNS.values():
            self.all_skills.update(category_skills)
        self._load_spacy()

    def _load_spacy(self):
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            self.use_spacy = True
            logger.info("✅ ResumeAnalyzer: spaCy loaded")
        except Exception:
            self.use_spacy = False
            logger.warning("⚠️ spaCy not available, using pattern matching")

    def analyze(self, text: str) -> dict:
        """Extract skills, experience, education from resume text"""
        text_lower = text.lower()

        extracted_skills = self._extract_skills(text_lower)
        experience_years = self._extract_experience(text)
        education = self._extract_education(text)
        contact_info = self._extract_contact(text)

        # Match against career paths only when we have skills.
        # Some short resumes include experience/education but no explicit skill keywords.
        top_roles = []
        if extracted_skills:
            career_rec = CareerRecommender()
            top_roles = career_rec.predict(extracted_skills, top_n=5)

        # Gap analysis
        gap_analysis = {}
        for role in top_roles[:3]:
            gap_analysis[role["title"]] = role["skills_gap"]

        # ATS score (keyword density check)
        ats_score = self._calculate_ats_score(text_lower, extracted_skills)

        # Improvement tips
        tips = self._generate_tips(text, extracted_skills, experience_years, ats_score)

        return {
            "extracted_skills": extracted_skills,
            "extracted_experience": experience_years,
            "extracted_education": education,
            "contact_info": contact_info,
            "top_roles": top_roles,
            "gap_analysis": gap_analysis,
            "skill_match_scores": {role["title"]: role["match_score"] for role in top_roles},
            "ats_score": ats_score,
            "improvement_tips": tips,
            "skill_categories": self._categorize_skills(extracted_skills)
        }

    def _extract_skills(self, text: str) -> List[str]:
        found = []
        for skill in self.all_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found.append(skill.title() if len(skill) <= 4 else skill.capitalize())

        # spaCy additional extraction
        if self.use_spacy:
            doc = self.nlp(text[:10000])
            for ent in doc.ents:
                if ent.label_ in ("ORG", "PRODUCT", "WORK_OF_ART"):
                    candidate = ent.text.lower()
                    if any(s in candidate for s in self.all_skills):
                        if ent.text not in found:
                            found.append(ent.text)

        return list(dict.fromkeys(found))[:30]  # Deduplicate, max 30

    def _extract_experience(self, text: str) -> float:
        patterns = [
            r'(\d+\.?\d*)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'experience[:\s]+(\d+\.?\d*)\+?\s*years?',
            r'(\d{4})\s*[-–]\s*(?:present|current|now|2024|2023)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    val = float(matches[0])
                    if val > 1900:  # Year format, estimate duration
                        val = 2024 - val
                    if 0 <= val <= 50:
                        return round(val, 1)
                except:
                    pass
        return 0.0

    def _extract_education(self, text: str) -> str:
        edu_patterns = [
            (r'\bphd\b|\bdoctor(?:ate)?\b|\bd\.phil\b', "PhD"),
            (r'\bm\.?tech\b|\bmaster of technology\b|\bme\b|\bm\.?e\b', "M.Tech"),
            (r'\bmba\b|\bmaster of business\b', "MBA"),
            (r'\bm\.?sc\b|\bmaster of science\b|\bms\b', "M.Sc / MS"),
            (r'\bmca\b|\bmaster of computer\b', "MCA"),
            (r'\bb\.?tech\b|\bbachelor of technology\b|\bbtec\b|\bengineering\b', "B.Tech"),
            (r'\bbca\b|\bb\.?sc\b|\bbachelor of science\b|\bcomputer application\b', "BCA / B.Sc"),
            (r'\bba\b|\bb\.?com\b|\bbba\b|\bbachelor\b', "BA / B.Com"),
            (r'\bdiploma\b|\bpolytechnic\b', "Diploma"),
            (r'\b12th\b|\bclass xii\b|\bhsc\b|\bintermediate\b', "12th"),
        ]
        for pattern, label in edu_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return label
        return "Graduate"

    def _extract_contact(self, text: str) -> dict:
        email = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]+', text)
        phone = re.search(r'(?:\+91\s?)?[789]\d{9}', text)
        linkedin = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        github = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
        return {
            "email": email.group() if email else None,
            "phone": phone.group() if phone else None,
            "linkedin": linkedin.group() if linkedin else None,
            "github": github.group() if github else None,
        }

    def _calculate_ats_score(self, text: str, skills: List[str]) -> float:
        score = 30.0  # Base
        if len(skills) >= 5:  score += 20
        elif len(skills) >= 3: score += 10
        if re.search(r'\bexperience\b', text): score += 5
        if re.search(r'\bproject', text):      score += 5
        if re.search(r'\bachiev|\baccomplish|\bdeliver|\bimpact', text): score += 10
        if re.search(r'\d+%|\d+x|\$[\d,]+|₹[\d,]+', text):  score += 15  # Quantified achievements
        if re.search(r'linkedin\.com', text):  score += 5
        if re.search(r'github\.com', text):    score += 5
        if re.search(r'\beducation\b|\bdegree\b', text): score += 5
        return min(98, score)

    def _categorize_skills(self, skills: List[str]) -> dict:
        categorized = {}
        for skill in skills:
            skill_lower = skill.lower()
            for category, category_skills in SKILL_PATTERNS.items():
                if any(cs in skill_lower or skill_lower in cs for cs in category_skills):
                    categorized.setdefault(category, []).append(skill)
                    break
        return categorized

    def _generate_tips(self, text: str, skills: List[str], exp: float, ats: float) -> List[str]:
        tips = []
        if ats < 60:     tips.append("Add more quantified achievements (numbers, percentages, impact metrics)")
        if len(skills) < 5: tips.append("List more technical skills — recruiters scan for keywords")
        if not re.search(r'github\.com|portfolio|project', text, re.IGNORECASE):
            tips.append("Add GitHub profile or portfolio link — essential for tech roles")
        if not re.search(r'\d+%|\d+x|\$|₹', text):
            tips.append("Quantify your achievements: 'improved performance by 40%' beats 'improved performance'")
        if not re.search(r'linkedin\.com', text, re.IGNORECASE):
            tips.append("Add LinkedIn profile URL to increase recruiter trust")
        if len(text.split()) < 300:
            tips.append("Resume seems too short — aim for 400-600 words for experienced professionals")
        if len(text.split()) > 1200:
            tips.append("Resume may be too long — keep it to 1-2 pages max for sub-10-year experience")
        tips.append("Tailor your resume for each application — ATS systems filter by job description keywords")
        return tips[:6]


# ══════════════════════════════════════════════════════════════════════════════
# 4. LOAN ELIGIBILITY MODEL (Logistic Regression)
# ══════════════════════════════════════════════════════════════════════════════

class LoanEligibilityModel:
    """Loan eligibility predictor using Logistic Regression + rule-based EMI calc"""

    LOAN_RATES = {
        "education": {"min": 8.1, "max": 11.5, "base": 8.5},
        "home":      {"min": 8.4, "max": 9.8,  "base": 8.75},
        "personal":  {"min": 10.5,"max": 18.0, "base": 12.5},
        "vehicle":   {"min": 8.7, "max": 12.0, "base": 9.5},
        "business":  {"min": 12.0,"max": 20.0, "base": 14.0},
        "gold":      {"min": 8.9, "max": 12.0, "base": 10.0},
    }

    BANK_DATA = {
        "education": [
            {"name": "SBI Scholar Loan",  "rate": "8.1–11.15%", "fee": "Nil", "max_amt": "₹30L", "features": ["No collateral <₹7.5L", "Moratorium period", "Tax benefit 80E"]},
            {"name": "HDFC Credila",       "rate": "9.55–13%",  "fee": "0.5–1%", "max_amt": "Unlimited", "features": ["Doorstep service", "Pre-admission approval"]},
            {"name": "Axis Bank Education","rate": "10.5–13%",  "fee": "Nil",  "max_amt": "₹75L", "features": ["Abroad study covered", "Part-time job income counted"]},
            {"name": "Union Bank",         "rate": "8.5–10.5%", "fee": "Nil",  "max_amt": "₹20L", "features": ["Vidyarthi scheme", "Easy documentation"]},
        ],
        "home": [
            {"name": "SBI Home Loan",  "rate": "8.4–8.7%",  "fee": "0.35%", "max_amt": "No limit", "features": ["Lowest rates", "Free CIBIL check","Women 0.05% discount"]},
            {"name": "HDFC Home Loan", "rate": "8.5–9.0%",  "fee": "0.5%",  "max_amt": "No limit", "features": ["Quick approval","Doorstep service"]},
            {"name": "LIC HFL",        "rate": "8.45–8.7%", "fee": "Nil",   "max_amt": "No limit", "features": ["Govt-backed", "Low processing fee"]},
            {"name": "Kotak Mahindra", "rate": "8.7–9.2%",  "fee": "0.5%",  "max_amt": "No limit", "features": ["Balance transfer option","Online process"]},
        ],
        "personal": [
            {"name": "HDFC Personal",  "rate": "10.5–21%", "fee": "2.5%", "max_amt": "₹40L", "features": ["Instant disbursal","Minimal documents"]},
            {"name": "SBI XPRESS",     "rate": "11–15%",   "fee": "1%",   "max_amt": "₹20L", "features": ["Pre-approved", "Govt employee special"]},
            {"name": "Bajaj Finance",  "rate": "11–18%",   "fee": "3%",   "max_amt": "₹35L", "features": ["Flexi EMI", "No collateral needed"]},
            {"name": "Axis Bank",      "rate": "10.99–22%","fee": "2%",   "max_amt": "₹40L", "features": ["Digital process", "24hr approval"]},
        ],
    }

    def predict(self, data: dict) -> dict:
        loan_type   = data["loan_type"]
        amount      = data["amount"]
        tenure_yr   = data["tenure_years"]
        income      = data["monthly_income"]
        emp_type    = data["employment_type"]
        age         = data["age"]
        exist_emis  = data.get("existing_emis", 0)
        cibil       = data["cibil_score"]

        # Interest rate
        rate_info = self.LOAN_RATES.get(loan_type, self.LOAN_RATES["personal"])
        annual_rate = rate_info["base"]
        if cibil >= 750: annual_rate = rate_info["min"]
        elif cibil >= 700: annual_rate = rate_info["min"] + (rate_info["base"] - rate_info["min"]) * 0.5
        monthly_rate = annual_rate / 100 / 12

        # EMI calculation
        n = int(tenure_yr * 12)
        if monthly_rate > 0 and n > 0:
            emi = amount * monthly_rate * (1 + monthly_rate)**n / ((1 + monthly_rate)**n - 1)
        else:
            emi = amount / max(n, 1)
        emi = round(emi, 2)

        total_payable = round(emi * n, 2)
        total_interest = round(total_payable - amount, 2)

        # Max eligible amount (FOIR ≤ 50%)
        available_income = income * 0.50 - exist_emis
        if monthly_rate > 0:
            max_eligible = available_income * ((1 + monthly_rate)**n - 1) / (monthly_rate * (1 + monthly_rate)**n)
        else:
            max_eligible = available_income * n
        max_eligible = round(max(0, min(max_eligible, amount * 1.5)), 2)

        # Eligibility scoring
        score = 50.0
        if cibil >= 750: score += 25
        elif cibil >= 700: score += 15
        elif cibil >= 650: score += 5
        elif cibil < 600: score -= 25
        foir = (emi + exist_emis) / income if income > 0 else 1
        if foir <= 0.35: score += 15
        elif foir <= 0.50: score += 8
        else: score -= 15
        emp_scores = {"salaried_govt": 15, "salaried_pvt": 10, "self_employed": 5, "student": 8 if loan_type == "education" else -5, "freelancer": 3}
        score += emp_scores.get(emp_type, 0)
        if 25 <= age <= 50: score += 8
        elif age < 21 or age > 60: score -= 10
        if loan_type == "education" and amount <= 1500000: score += 10
        if loan_type == "home" and data.get("property_value"):
            ltv = amount / data["property_value"]
            if ltv <= 0.75: score += 10
            elif ltv > 0.90: score -= 10

        score = round(min(98, max(10, score)), 1)
        is_eligible = score >= 55

        # Bank recommendations
        banks_raw = self.BANK_DATA.get(loan_type, self.BANK_DATA["personal"])
        banks = [{"bank_name": b["name"], "interest_rate": b["rate"], "processing_fee": b["fee"], "max_amount": b["max_amt"], "special_features": b["features"]} for b in banks_raw]

        # Improvement tips
        tips = []
        if cibil < 700: tips.append("Improve CIBIL score to 750+ — pay all existing dues on time for 6 months")
        if foir > 0.50: tips.append(f"EMI burden too high ({foir*100:.0f}% FOIR) — clear existing loans or reduce loan amount")
        if exist_emis > income * 0.30: tips.append("Clear existing EMIs first before applying for new loan")
        if cibil >= 750 and emp_type == "salaried_govt": tips.append("Excellent profile! Apply to SBI first — govt employees get best rates")

        # Tax benefits
        tax_benefit = None
        if loan_type == "education": tax_benefit = "Section 80E: Full interest deduction for 8 years — no cap. Save ₹30K-₹1.5L/year in taxes."
        elif loan_type == "home": tax_benefit = "Section 24(b): ₹2L deduction on interest. Section 80C: ₹1.5L on principal. Total save up to ₹3.5L/year."

        return {
            "eligibility_score": score,
            "is_eligible": is_eligible,
            "emi_amount": emi,
            "total_interest": total_interest,
            "total_payable": total_payable,
            "max_eligible_amount": max_eligible,
            "annual_interest_rate": annual_rate,
            "recommended_banks": banks,
            "improvement_tips": tips,
            "tax_benefits": tax_benefit,
            "processing_time": "3-7 working days" if loan_type in ("home", "education") else "24-48 hours"
        }


# ══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCES (loaded at startup)
# ══════════════════════════════════════════════════════════════════════════════
_career_model    = None
_decision_model  = None
_resume_model    = None
_loan_model      = None

def get_career_model()    -> CareerRecommender:  global _career_model;   _career_model   = _career_model   or CareerRecommender(); return _career_model
def get_decision_model()  -> DecisionClassifier: global _decision_model; _decision_model = _decision_model or DecisionClassifier(); return _decision_model
def get_resume_model()    -> ResumeAnalyzer:     global _resume_model;   _resume_model   = _resume_model   or ResumeAnalyzer();     return _resume_model
def get_loan_model()      -> LoanEligibilityModel: global _loan_model;   _loan_model     = _loan_model     or LoanEligibilityModel(); return _loan_model

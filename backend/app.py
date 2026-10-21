"""
Healthnexus AI - Flask Backend API
Production-ready health insurance recommendation and analysis platform.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from difflib import get_close_matches
from pathlib import Path
import json
import logging
import re
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from ranker import PlanRanker
from ml.model_registry import load_latest_metrics
from ml.train_pipeline import train_and_register
from services.chatbot_rag import ChatbotRAG
from services.bill_analyzer import analyze_bill_file, process_bill_text
from services.async_bill_jobs import BillJobManager
from services.preauth_service import PreAuthEstimator
from services.smart_preauth import SmartPreAuthService
from services.platform_service import PlatformService
from services.resources_service import ResourceSearchService
from services.llm_provider import (
    create_groq_provider_from_env,
    create_llm_provider_from_env,
)
from services.patient_report_service import PatientReportService

# Initialize Flask app
app = Flask(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent
SHARED_ROOT = PROJECT_ROOT.parent / "shared"
DATA_PATH = SHARED_ROOT / "data"
MODELS_PATH = SHARED_ROOT / "models"
OUTPUTS_PATH = PROJECT_ROOT.parent / "outputs" / "ml"
UPLOAD_PATH = SHARED_ROOT / "uploads"
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

# Environment
ENV_FILE = PROJECT_ROOT.parent / ".env"
load_dotenv(ENV_FILE)

# Config
app.config["SECRET_KEY"] = "healthnexus-ai-secret-key-2026"
app.config["JWT_SECRET_KEY"] = "jwt-secret-healthnexus-2026"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///healthnexus.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB
app.config["UPLOAD_FOLDER"] = UPLOAD_PATH

# Extensions
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)

db = SQLAlchemy(app)
jwt = JWTManager(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== DATABASE MODELS ====================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }


class SavedPlan(db.Model):
    __tablename__ = "saved_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan_id = db.Column(db.String(50), nullable=False)
    plan_name = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    premium = db.Column(db.Float, nullable=False)
    coverage_amount = db.Column(db.Float, nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="saved_plans")


# ==================== SERVICE INITIALIZATION ====================

MODEL_PATH = MODELS_PATH / "plan_ranker.pkl"

try:
    ranker = PlanRanker(MODEL_PATH, DATA_PATH)
    logger.info("✅ ML Ranker loaded")
except Exception as e:
    logger.error(f"❌ Failed to load ML model: {e}")
    ranker = None

LLM_MODEL_PATH = SHARED_ROOT / "models" / "llm" / "ggml-model-q4_0.gguf"
CHAT_INDEX_DIR = SHARED_ROOT / "chat_index"

bill_jobs = BillJobManager(
    uploads_dir=UPLOAD_PATH / "async",
    jobs_dir=SHARED_ROOT / "outputs" / "bill_jobs",
)
preauth_estimator = PreAuthEstimator()
smart_preauth = SmartPreAuthService(
    preauth_estimator, chatbot=None)  # Will set chatbot after init
platform_service = PlatformService(DATA_PATH)
resource_service = ResourceSearchService(SHARED_ROOT)
llm_provider = create_llm_provider_from_env()
groq_recommendation_provider = create_groq_provider_from_env()
patient_report_service = PatientReportService(llm_provider=llm_provider)

if groq_recommendation_provider:
    logger.info("✅ Groq recommendation provider ready")
else:
    logger.info("ℹ️ Groq recommendation provider unavailable; ML fallback only")

try:
    chatbot = ChatbotRAG(
        model_path=LLM_MODEL_PATH if LLM_MODEL_PATH.exists() else None,
        index_dir=CHAT_INDEX_DIR,
    )
    logger.info("✅ Chatbot RAG initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize chatbot: {e}")
    chatbot = None

# Inject chatbot into smart_preauth for context fallback
if chatbot:
    smart_preauth.chatbot = chatbot

PREAUTH_FEEDBACK_FILE = SHARED_ROOT / "outputs" / "preauth_feedback.jsonl"
PREAUTH_FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
PATIENT_REPORT_CORRECTIONS_FILE = SHARED_ROOT / \
    "outputs" / "patient_report_corrections.jsonl"
PATIENT_REPORT_CORRECTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
RECOMMENDATION_LOG_FILE = SHARED_ROOT / \
    "outputs" / "recommendation_events.jsonl"
RECOMMENDATION_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "heic"}
PATIENT_REPORT_ALLOWED_EXTENSIONS = {
    "pdf", "jpg", "jpeg", "png", "heic", "txt"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _allowed_patient_report_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in PATIENT_REPORT_ALLOWED_EXTENSIONS


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_greeting(text: str) -> bool:
    greetings = {
        "hi",
        "hello",
        "hey",
        "hola",
        "namaste",
        "good morning",
        "good evening",
        "good afternoon",
    }
    return text.strip().lower() in greetings


def _parse_bool(value, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return default


def _parse_recommendation_engine(value) -> str:
    engine = str(value or "ml").strip().lower()
    return engine if engine in {"ml", "groq"} else "ml"


def _rerank_with_groq(
    user_profile: dict,
    candidate_recommendations: list,
    limit: int,
) -> tuple[list | None, str | None, str | None]:
    """Return (recommendations, strategy, fallback_reason)."""
    if not candidate_recommendations:
        return None, None, "No ML candidate recommendations were available"

    if groq_recommendation_provider is None:
        return None, None, "Groq API is not configured"

    rerank = groq_recommendation_provider.rerank_recommendations(
        user_profile=user_profile,
        candidate_recommendations=candidate_recommendations,
        limit=limit,
    )

    if not rerank:
        return None, None, "Groq reranking failed"

    selected_plan_ids = rerank.get("selected_plan_ids")
    if not isinstance(selected_plan_ids, list) or not selected_plan_ids:
        return None, None, "Groq returned no ranked plans"

    candidate_by_id = {
        str(rec.get("plan_id")): dict(rec)
        for rec in candidate_recommendations
        if rec.get("plan_id")
    }
    notes_by_plan = rerank.get("plan_notes") if isinstance(
        rerank.get("plan_notes"), dict
    ) else {}

    ordered = []
    used = set()

    for plan_id in selected_plan_ids:
        pid = str(plan_id)
        rec = candidate_by_id.get(pid)
        if rec and pid not in used:
            ordered.append(rec)
            used.add(pid)
        if len(ordered) >= limit:
            break

    if len(ordered) < limit:
        for rec in candidate_recommendations:
            pid = str(rec.get("plan_id", ""))
            if pid and pid not in used:
                ordered.append(dict(rec))
                used.add(pid)
            if len(ordered) >= limit:
                break

    if not ordered:
        return None, None, "Groq reranking produced an empty recommendation set"

    for idx, rec in enumerate(ordered[:limit], 1):
        rec["rank"] = idx
        pid = str(rec.get("plan_id", ""))
        notes = notes_by_plan.get(pid)
        if isinstance(notes, list) and notes:
            groq_note = str(notes[0]).strip()
            if groq_note:
                existing_bullets = [
                    str(b).strip() for b in rec.get("bullets", []) if str(b).strip()
                ]
                merged_bullets = [
                    f"Groq insight: {groq_note}"] + existing_bullets
                # Keep order and de-duplicate while preserving readability.
                deduped = []
                seen = set()
                for bullet in merged_bullets:
                    key = bullet.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    deduped.append(bullet)
                rec["bullets"] = deduped[:5]
                rec["explain_text"] = " | ".join(rec["bullets"][:3])

    strategy = rerank.get("strategy")
    strategy_text = str(strategy).strip() if strategy is not None else None

    return ordered[:limit], strategy_text, None


INSURANCE_QUERY_HINT_TERMS = {
    "copay",
    "copayment",
    "payment",
    "premium",
    "claim",
    "cashless",
    "reimbursement",
    "deductible",
    "coverage",
    "waiting",
    "policy",
    "sum",
    "insured",
    "network",
    "hospital",
    "preexisting",
    "pre",
    "existing",
}

INSURANCE_QUERY_HINT_PHRASES = {
    "co payment",
    "co pay",
    "pre existing",
    "waiting period",
    "sum insured",
    "claim settlement",
}

SHORT_QUERY_INTENT_VERBS = {
    "explain",
    "define",
    "what",
    "how",
    "tell",
}


def _normalize_query_text(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9\s\-]", " ", (text or "").lower())
    normalized = normalized.replace("-", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _normalize_short_insurance_query(text: str) -> str:
    normalized = _normalize_query_text(text)
    tokens = normalized.split()
    repaired = []

    for token in tokens:
        if len(token) >= 4:
            closest = get_close_matches(
                token,
                list(INSURANCE_QUERY_HINT_TERMS),
                n=1,
                cutoff=0.78,
            )
            if closest:
                repaired.append(closest[0])
                continue
        repaired.append(token)

    return " ".join(repaired).strip()


def _looks_like_insurance_short_query(text: str) -> bool:
    normalized = _normalize_short_insurance_query(text)
    if not normalized:
        return False

    tokens = normalized.split()

    if any(token in INSURANCE_QUERY_HINT_TERMS for token in tokens):
        return True

    if any(phrase in normalized for phrase in INSURANCE_QUERY_HINT_PHRASES):
        return True

    if tokens and tokens[0] in SHORT_QUERY_INTENT_VERBS and len(tokens) >= 2:
        tail = tokens[1:]
        return any(token in INSURANCE_QUERY_HINT_TERMS for token in tail)

    return False


# ==================== HEALTH & AUTH ====================

@app.route("/api/health", methods=["GET"])
def health_check():
    metrics = load_latest_metrics(MODELS_PATH)
    return jsonify(
        {
            "status": "healthy",
            "message": "Healthnexus AI API is running",
            "ml_model_loaded": ranker is not None,
            "ml_model_version": getattr(ranker, "model_version", "unknown") if ranker else None,
            "latest_ndcg_at_10": metrics.get("ndcg_at_10"),
            "timestamp": _utc_now(),
        }
    )


@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json() or {}
        if not data.get("username") or not data.get("email") or not data.get("password"):
            return jsonify({"error": "Missing required fields"}), 400

        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already registered"}), 409
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "Username already taken"}), 409

        user = User(username=data["username"], email=data["email"])
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        return jsonify({"message": "User registered successfully", "access_token": access_token, "user": user.to_dict()}), 201
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}
        if not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password required"}), 400

        user = User.query.filter_by(email=data["email"]).first()
        if not user or not user.check_password(data["password"]):
            return jsonify({"error": "Invalid email or password"}), 401

        access_token = create_access_token(identity=str(user.id))
        return jsonify({"message": "Login successful", "access_token": access_token, "user": user.to_dict()}), 200
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500


# ==================== RECOMMENDATIONS + EXPLAINABILITY ====================

@app.route("/api/recommendations", methods=["POST"])
def get_recommendations():
    try:
        if ranker is None:
            return jsonify({"error": "ML model not available"}), 503

        data = request.get_json() or {}
        if not data.get("age"):
            return jsonify({"error": "Age is required"}), 400

        user_profile = {
            "user_id": data.get("user_id", "anonymous"),
            "age": int(data.get("age", 35)),
            "gender": data.get("gender", "male"),
            "annual_income": float(data.get("annual_income", 600000)),
            "income_band": data.get("income_band"),
            "city": data.get("city", "Mumbai"),
            "region": data.get("region", data.get("city", "Mumbai")),
            "state": data.get("state", "Maharashtra"),
            "marital_status": data.get("marital_status", "single"),
            "dependents": int(data.get("dependents", 0)),
            "occupation_type": data.get("occupation_type", "salaried"),
            "plan_type": data.get("plan_type", "individual"),
            "has_diabetes": data.get("has_diabetes", False),
            "has_hypertension": data.get("has_hypertension", False),
            "has_heart_disease": data.get("has_heart_disease", False),
            "has_asthma": data.get("has_asthma", False),
            "has_obesity": data.get("has_obesity", False),
            "has_thyroid": data.get("has_thyroid", False),
            "smoking_flag": data.get("smoking_flag", False),
            "coverage_amount": float(data.get("coverage_amount", 500000)),
            "premium_budget": float(data.get("premium_budget", 5000)),
            "preferred_providers": data.get("preferred_providers", []),
            "claim_history_count": int(data.get("claim_history_count", 0)),
            "renewal_loyalty_years": int(data.get("renewal_loyalty_years", 0)),
            "risk_score": float(data.get("risk_score", 0.5)),
        }

        limit = int(data.get("limit", 8))
        recommendation_engine_requested = _parse_recommendation_engine(
            data.get("recommendation_engine", "ml")
        )
        recommendation_engine_used = recommendation_engine_requested
        recommendation_engine_fallback_reason = None
        recommendation_engine_strategy = None

        explore_mode = _parse_bool(
            data.get("explore_mode", False), default=False)

        explore_seed = None
        if data.get("explore_seed") not in (None, ""):
            explore_seed = int(data.get("explore_seed"))

        explore_temperature = float(data.get("explore_temperature", 0.85))

        if recommendation_engine_requested == "groq":
            candidate_limit = min(max(limit * 4, 20), 40)
            candidate_recommendations = ranker.rank(
                user_profile,
                k=candidate_limit,
                explore_mode=False,
                explore_seed=None,
                explore_temperature=0.85,
            )

            recommendations, recommendation_engine_strategy, fallback_reason = _rerank_with_groq(
                user_profile=user_profile,
                candidate_recommendations=candidate_recommendations,
                limit=limit,
            )

            if recommendations is None:
                recommendation_engine_used = "ml"
                recommendation_engine_fallback_reason = fallback_reason or (
                    "Groq recommendation unavailable"
                )
                recommendations = candidate_recommendations[:limit]
        else:
            recommendations = ranker.rank(
                user_profile,
                k=limit,
                explore_mode=explore_mode,
                explore_seed=explore_seed,
                explore_temperature=explore_temperature,
            )

        if not recommendations:
            return jsonify({"error": "No recommendations available", "message": "Please try adjusting your preferences"}), 404

        metrics = load_latest_metrics(MODELS_PATH)

        top5 = recommendations[:5]
        top5_signature = "|".join([str(p.get("plan_id", "")) for p in top5])
        top5_providers = [str(p.get("provider", "")) for p in top5]
        top5_provider_diversity = len({p.lower() for p in top5_providers if p})

        with open(RECOMMENDATION_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": _utc_now(),
                        "user_id": user_profile.get("user_id", "anonymous"),
                        "age": user_profile["age"],
                        "city": user_profile["city"],
                        "top_plan": recommendations[0].get("plan_id") if recommendations else None,
                        "top5_signature": top5_signature,
                        "top5_provider_diversity": top5_provider_diversity,
                        "explore_mode": explore_mode,
                        "explore_seed": explore_seed,
                        "explore_temperature": explore_temperature,
                        "recommendation_engine_requested": recommendation_engine_requested,
                        "recommendation_engine_used": recommendation_engine_used,
                        "recommendation_engine_fallback_reason": recommendation_engine_fallback_reason,
                        "recommendation_engine_strategy": recommendation_engine_strategy,
                        "model_version": getattr(ranker, "model_version", "legacy-1.0"),
                    }
                )
                + "\n"
            )

        exploration_enabled = (
            recommendation_engine_used == "ml"
            and recommendation_engine_requested == "ml"
            and explore_mode
        )

        return jsonify(
            {
                "success": True,
                "recommendations": recommendations,
                "user_profile": {
                    "age": user_profile["age"],
                    "city": user_profile["city"],
                    "conditions": [k.replace("has_", "") for k, v in user_profile.items() if k.startswith("has_") and v],
                },
                "total_plans_evaluated": len(recommendations),
                "ml_model_version": getattr(ranker, "model_version", "legacy-1.0"),
                "ml_metrics": {
                    "ndcg_at_10": metrics.get("ndcg_at_10"),
                    "precision_at_5": metrics.get("precision_at_5"),
                    "coverage_at_5": metrics.get("coverage_at_5"),
                },
                "recommendation_engine": {
                    "requested": recommendation_engine_requested,
                    "used": recommendation_engine_used,
                    "fallback_reason": recommendation_engine_fallback_reason,
                    "strategy": recommendation_engine_strategy,
                },
                "exploration": {
                    "enabled": exploration_enabled,
                    "seed": explore_seed,
                    "temperature": explore_temperature if exploration_enabled else None,
                },
            }
        ), 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        return jsonify({"error": "Failed to generate recommendations"}), 500


@app.route("/api/recommendations/explain", methods=["POST"])
def explain_recommendations():
    try:
        if ranker is None:
            return jsonify({"error": "ML model not available"}), 503

        data = request.get_json() or {}
        if not data.get("age"):
            return jsonify({"error": "Age is required"}), 400

        user_profile = {
            "age": int(data.get("age", 35)),
            "gender": data.get("gender", "male"),
            "annual_income": float(data.get("annual_income", 600000)),
            "city": data.get("city", "Mumbai"),
            "region": data.get("region", data.get("city", "Mumbai")),
            "marital_status": data.get("marital_status", "single"),
            "dependents": int(data.get("dependents", 0)),
            "has_diabetes": data.get("has_diabetes", False),
            "has_hypertension": data.get("has_hypertension", False),
            "has_asthma": data.get("has_asthma", False),
            "has_heart_disease": data.get("has_heart_disease", False),
            "has_thyroid": data.get("has_thyroid", False),
            "has_obesity": data.get("has_obesity", False),
            "smoking_flag": data.get("smoking_flag", False),
            "claim_history_count": int(data.get("claim_history_count", 0)),
            "renewal_loyalty_years": int(data.get("renewal_loyalty_years", 0)),
            "risk_score": float(data.get("risk_score", 0.5)),
        }

        k = int(data.get("limit", 5))
        top_features = int(data.get("top_features", 5))

        explanations = ranker.explain_recommendations(
            user_profile, k=k, top_features=top_features)
        return jsonify({"success": True, "model_version": getattr(ranker, "model_version", "legacy-1.0"), "explanations": explanations}), 200
    except Exception as e:
        logger.error(f"Explainability error: {e}", exc_info=True)
        return jsonify({"error": "Failed to generate explanation"}), 500


@app.route("/api/plans/<plan_id>", methods=["GET"])
def get_plan_details(plan_id):
    try:
        if ranker is None:
            return jsonify({"error": "ML model not available"}), 503

        plan = ranker.get_plan_by_id(plan_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404

        return jsonify({"success": True, "plan": plan}), 200
    except Exception as e:
        logger.error(f"Error fetching plan details: {e}")
        return jsonify({"error": "Failed to fetch plan details"}), 500


@app.route("/api/plans/save", methods=["POST"])
@jwt_required()
def save_plan():
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        saved_plan = SavedPlan(
            user_id=int(user_id),
            plan_id=data["plan_id"],
            plan_name=data["plan_name"],
            provider=data["provider"],
            premium=float(data["premium"]),
            coverage_amount=float(data["coverage_amount"]),
        )

        db.session.add(saved_plan)
        db.session.commit()

        return jsonify({"success": True, "message": "Plan saved successfully"}), 201
    except Exception as e:
        logger.error(f"Error saving plan: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to save plan"}), 500


@app.route("/api/plans/saved", methods=["GET"])
@jwt_required()
def get_saved_plans():
    try:
        user_id = get_jwt_identity()
        saved_plans = SavedPlan.query.filter_by(user_id=int(
            user_id)).order_by(SavedPlan.saved_at.desc()).all()
        return jsonify(
            {
                "success": True,
                "saved_plans": [
                    {
                        "id": plan.id,
                        "plan_id": plan.plan_id,
                        "plan_name": plan.plan_name,
                        "provider": plan.provider,
                        "premium": plan.premium,
                        "coverage_amount": plan.coverage_amount,
                        "saved_at": plan.saved_at.isoformat(),
                    }
                    for plan in saved_plans
                ],
            }
        ), 200
    except Exception as e:
        logger.error(f"Failed to retrieve saved plans: {e}")
        return jsonify({"error": "Failed to retrieve plans"}), 500


# ==================== ML OPS ====================

@app.route("/api/ml/metrics/latest", methods=["GET"])
def ml_latest_metrics():
    try:
        metrics = load_latest_metrics(MODELS_PATH)
        return jsonify({"success": True, "metrics": metrics}), 200
    except Exception as e:
        logger.error(f"Metrics load error: {e}")
        return jsonify({"error": "Failed to load metrics"}), 500


@app.route("/api/ml/retrain", methods=["POST"])
def ml_retrain():
    try:
        result = train_and_register(DATA_PATH, MODELS_PATH, OUTPUTS_PATH)

        # Reload ranker to pick latest artifact
        global ranker
        ranker = PlanRanker(MODEL_PATH, DATA_PATH)

        return jsonify({"success": True, "message": "Retraining completed", **result}), 200
    except Exception as e:
        logger.error(f"Retraining failed: {e}", exc_info=True)
        return jsonify({"error": "Retraining failed", "detail": str(e)}), 500


# ==================== CHATBOT ====================

@app.route("/api/chat/query", methods=["POST"])
def chat_query():
    try:
        if chatbot is None:
            return jsonify({"error": "Chatbot not available"}), 503

        data = request.get_json() or {}
        query = data.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query is required"}), 400

        if _is_greeting(query):
            return (
                jsonify(
                    {
                        "success": True,
                        "answer": "Hello! 👋 I can help with insurance plans, claims, pre-authorization, and bill analysis. What would you like to know?",
                        "sources": [],
                        "latency_seconds": 0,
                        "suggestions": [
                            "How do I file a cashless claim?",
                            "What are pre-existing conditions?",
                            "How can I reduce my bill amount?",
                            "Which plan is best for a family?",
                        ],
                    }
                ),
                200,
            )

        is_short_query = len(query.split()) <= 2 and "?" not in query
        normalized_short_query = _normalize_short_insurance_query(query)

        if is_short_query and not _looks_like_insurance_short_query(query):
            return (
                jsonify(
                    {
                        "success": True,
                        "answer": "Could you share a bit more detail so I can help better?",
                        "sources": [],
                        "latency_seconds": 0,
                        "suggestions": [
                            "Explain co-payment",
                            "What is waiting period?",
                            "How does reimbursement work?",
                        ],
                    }
                ),
                200,
            )

        result = chatbot.query(
            query=normalized_short_query if is_short_query else query,
            top_k=int(data.get("top_k", 5)),
            page_context=data.get("page_context"),
            conversation_history=data.get("conversation_history", []),
            user_profile=data.get("user_profile"),
        )

        return jsonify({"success": True, **result}), 200
    except Exception as e:
        logger.error(f"Chat query error: {e}", exc_info=True)
        return jsonify({"error": "Failed to process query"}), 500


@app.route("/api/chat/status", methods=["GET"])
def chat_status():
    try:
        if chatbot is None:
            return jsonify({"status": "unavailable", "message": "Chatbot not initialized"}), 503
        return jsonify(chatbot.get_status()), 200
    except Exception as e:
        logger.error(f"Chat status error: {e}")
        return jsonify({"error": "Failed to get status"}), 500


@app.route("/api/chat/feedback", methods=["POST"])
def chat_feedback():
    try:
        data = request.get_json() or {}
        logger.info(f"Feedback received: {data.get('rating')}")
        return jsonify({"success": True, "message": "Feedback recorded"}), 200
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({"error": "Failed to record feedback"}), 500


@app.route("/api/chat/index", methods=["POST"])
def chat_index_docs():
    try:
        if chatbot is None:
            return jsonify({"error": "Chatbot not available"}), 503

        data = request.get_json() or {}
        docs = data.get("documents") or data.get("docs") or []
        if not docs:
            return jsonify({"error": "No documents provided"}), 400

        result = chatbot.index_documents(docs)
        return jsonify({"success": result.get("status") == "success", **result}), 200
    except Exception as e:
        logger.error(f"Chat index error: {e}", exc_info=True)
        return jsonify({"error": "Failed to index documents"}), 500


# ==================== BILL BUSTER ====================

@app.route("/api/bill-buster/upload", methods=["POST"])
def upload_bill_sync():
    """Synchronous upload+analysis endpoint (backward compatible)."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not _allowed_file(file.filename):
            return jsonify({"error": f"Invalid file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"}), 400

        filename = secure_filename(file.filename)
        extension = Path(filename).suffix
        temp_id = str(uuid.uuid4())
        temp_path = app.config["UPLOAD_FOLDER"] / f"{temp_id}{extension}"
        file.save(temp_path)

        with open(temp_path, "rb") as fp:
            result = analyze_bill_file(fp, extension)

        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass

        if result.get("status") == "error":
            return jsonify({"success": False, "error": result.get("error", "Analysis failed")}), 400

        return jsonify({"success": True, "job_id": temp_id, **result}), 200
    except Exception as e:
        logger.error(f"Bill upload error: {e}", exc_info=True)
        return jsonify({"error": "Failed to process bill"}), 500


@app.route("/api/bill-buster/analyze", methods=["POST"])
def analyze_bill_text():
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "Text is required"}), 400

        result = process_bill_text(text, 100.0)
        return jsonify({"success": True, **result}), 200
    except Exception as e:
        logger.error(f"Bill analysis error: {e}")
        return jsonify({"error": "Failed to analyze bill"}), 500


@app.route("/api/bill-buster/upload-bill", methods=["POST"])
def upload_bill_async():
    """Async upload endpoint returning job_id immediately."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not _allowed_file(file.filename):
            return jsonify({"error": f"Invalid file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"}), 400

        payload = bill_jobs.submit(file.filename, file.read())
        return jsonify(payload), 202
    except Exception as e:
        logger.error(f"Async upload error: {e}", exc_info=True)
        return jsonify({"error": "Failed to queue upload"}), 500


@app.route("/api/bill-buster/upload-status/<job_id>", methods=["GET"])
def bill_upload_status(job_id: str):
    payload = bill_jobs.status(job_id)
    if payload.get("status") == "not_found":
        return jsonify(payload), 404
    return jsonify(payload), 200


@app.route("/api/bill-buster/scan-result/<job_id>", methods=["GET"])
def bill_scan_result(job_id: str):
    payload = bill_jobs.result(job_id)
    if payload.get("status") == "not_found":
        return jsonify(payload), 404
    if payload.get("status") in {"processing", "failed"}:
        return jsonify(payload), 200
    return jsonify(payload), 200


# ==================== PATIENT REPORT PROFILE EXTRACTION ====================

@app.route("/api/patient-report/upload", methods=["POST"])
def patient_report_upload():
    """Upload patient report and auto-extract profile fields for quote form prefill."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not _allowed_patient_report_file(file.filename):
            return jsonify({"error": f"Invalid file type. Allowed: {', '.join(sorted(PATIENT_REPORT_ALLOWED_EXTENSIONS))}"}), 400

        result = patient_report_service.extract_from_upload(
            file, file.filename)
        if result.get("status") == "error":
            return jsonify({"success": False, **result}), 400

        return jsonify({"success": True, **result}), 200
    except Exception as e:
        logger.error(f"Patient report upload error: {e}", exc_info=True)
        return jsonify({"error": "Failed to process patient report"}), 500


@app.route("/api/patient-report/confirm", methods=["POST"])
def patient_report_confirm():
    """Capture user-corrected extracted profile values for future model improvements."""
    try:
        data = request.get_json() or {}
        row = {
            "timestamp": _utc_now(),
            "user_id": data.get("user_id", "anonymous"),
            "source_file": data.get("source_file"),
            "extracted_profile": data.get("extracted_profile"),
            "corrected_profile": data.get("corrected_profile"),
            "missing_fields": data.get("missing_fields", []),
        }
        with open(PATIENT_REPORT_CORRECTIONS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

        return jsonify({"success": True, "message": "Correction feedback captured"}), 200
    except Exception as e:
        logger.error(f"Patient report confirm error: {e}", exc_info=True)
        return jsonify({"error": "Failed to capture correction"}), 500


# ==================== PRE-AUTH ====================

@app.route("/api/preauth/estimate", methods=["POST"])
def preauth_estimate():
    try:
        data = request.get_json() or {}
        procedure = data.get("procedure_code") or data.get("procedure")
        insurer = data.get("insurer", "")
        hospital = data.get("hospital", "")
        room_type = data.get("room_type", "standard")

        if not procedure:
            return jsonify({"error": "procedure_code is required"}), 400

        estimate = preauth_estimator.estimate(
            procedure, insurer, hospital, room_type=room_type)
        return jsonify({"success": True, "estimate": estimate}), 200
    except Exception as e:
        logger.error(f"Preauth estimate error: {e}", exc_info=True)
        return jsonify({"error": "Failed to estimate pre-authorization cost"}), 500


@app.route("/api/preauth/feedback", methods=["POST"])
def preauth_feedback():
    try:
        data = request.get_json() or {}
        row = {
            "timestamp": _utc_now(),
            "user_id": data.get("user_id", "anonymous"),
            "procedure_code": data.get("procedure_code"),
            "plan_id": data.get("plan_id"),
            "estimated_oop": data.get("estimated_oop"),
            "actual_oop": data.get("actual_oop"),
        }
        with open(PREAUTH_FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

        return jsonify({"success": True, "message": "Feedback captured"}), 200
    except Exception as e:
        logger.error(f"Preauth feedback error: {e}", exc_info=True)
        return jsonify({"error": "Failed to capture feedback"}), 500


@app.route("/api/smart-preauth/query", methods=["POST"])
def smart_preauth_query():
    """
    Smart Pre-Auth Query endpoint.
    Combines RAG knowledge with cost estimation.

    Request:
        {
            "query": "What's the cost for knee surgery at Apollo?",
            "room_type": "standard" (optional),
            "insurer": "hdfc_ergo" (optional)
        }
    """
    try:
        data = request.get_json() or {}
        query = data.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query is required"}), 400

        room_type = data.get("room_type", "standard")
        insurer = data.get("insurer", "hdfc_ergo")

        result = smart_preauth.query_with_rag(
            query=query,
            preauth_service=preauth_estimator,
            chatbot=chatbot,
            room_type=room_type,
            insurer=insurer,
        )

        return jsonify({"success": True, **result}), 200
    except Exception as e:
        logger.error(f"Smart preauth query error: {e}", exc_info=True)
        return jsonify({"error": "Failed to process query"}), 500


@app.route("/api/smart-preauth/hospitals", methods=["GET"])
def smart_preauth_hospitals():
    """Get list of supported hospitals."""
    try:
        hospitals = smart_preauth.list_hospitals()
        return jsonify({"success": True, "hospitals": hospitals}), 200
    except Exception as e:
        logger.error(f"Hospital list error: {e}")
        return jsonify({"error": "Failed to fetch hospitals"}), 500


@app.route("/api/smart-preauth/insurers", methods=["GET"])
def smart_preauth_insurers():
    """Get list of major insurers and network acceptance counts."""
    try:
        insurers = smart_preauth.list_insurers()
        top_hospitals = smart_preauth.top_hospitals_by_acceptance(limit=10)
        return jsonify(
            {
                "success": True,
                "insurers": insurers,
                "top_network_hospitals": top_hospitals,
            }
        ), 200
    except Exception as e:
        logger.error(f"Insurer list error: {e}")
        return jsonify({"error": "Failed to fetch insurers"}), 500


@app.route("/api/smart-preauth/procedures", methods=["GET"])
def smart_preauth_procedures():
    """Get list of supported procedures."""
    try:
        procedures = smart_preauth.list_procedures()
        return jsonify({"success": True, "procedures": procedures}), 200
    except Exception as e:
        logger.error(f"Procedure list error: {e}")
        return jsonify({"error": "Failed to fetch procedures"}), 500


@app.route("/api/smart-preauth/room-types", methods=["GET"])
def smart_preauth_room_types():
    """Get list of available room types."""
    try:
        rooms = smart_preauth.get_room_types()
        return jsonify({"success": True, "room_types": rooms}), 200
    except Exception as e:
        logger.error(f"Room types error: {e}")
        return jsonify({"error": "Failed to fetch room types"}), 500


# ==================== PLATFORM INTEGRATION APIs ====================

@app.route("/api/platforms", methods=["GET"])
def list_platforms():
    try:
        return jsonify({"status": "ok", "platforms": platform_service.list_platforms()}), 200
    except Exception as e:
        logger.error(f"Platform list error: {e}")
        return jsonify({"error": "Failed to fetch platforms"}), 500


@app.route("/api/platforms/plans", methods=["GET"])
def list_platform_plans():
    try:
        source = request.args.get("source", "internal")
        limit = request.args.get("limit")
        max_premium = request.args.get("max_premium")

        result = platform_service.get_plans_with_meta(
            source=source,
            limit=int(limit) if limit else None,
            max_premium=float(max_premium) if max_premium else None,
        )

        response_payload = {
            "status": "ok",
            "source": result.get("source", source),
            "plans": result.get("plans", []),
            "is_live": bool(result.get("is_live", False)),
            "fallback_used": bool(result.get("fallback_used", False)),
            "fetched_at": result.get("fetched_at"),
            "cache_age_seconds": result.get("cache_age_seconds"),
        }

        if result.get("fallback_reason"):
            response_payload["fallback_reason"] = result.get("fallback_reason")
        if result.get("resource_id"):
            response_payload["resource_id"] = result.get("resource_id")
        if result.get("total_records") is not None:
            response_payload["total_records"] = result.get("total_records")

        return jsonify(response_payload), 200
    except Exception as e:
        logger.error(f"Platform plans error: {e}")
        return jsonify({"error": "Failed to fetch plans"}), 500


@app.route("/api/plan/<plan_id>", methods=["GET"])
def platform_plan_detail(plan_id: str):
    try:
        plan = platform_service.get_plan_by_id(plan_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404
        return jsonify({"status": "ok", "plan": plan}), 200
    except Exception as e:
        logger.error(f"Plan detail error: {e}")
        return jsonify({"error": "Failed to fetch plan"}), 500


# ==================== RESOURCES SEARCH API ====================

@app.route("/api/resources/search", methods=["GET"])
def resource_search():
    try:
        query = request.args.get("q", "")
        category = request.args.get("category")
        limit = int(request.args.get("limit", 10))
        results = resource_service.search(
            query=query, category=category, limit=limit)
        return jsonify({"success": True, "query": query, "results": results, "count": len(results)}), 200
    except Exception as e:
        logger.error(f"Resource search error: {e}")
        return jsonify({"error": "Failed to search resources"}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(_):
    return jsonify({"error": "Internal server error"}), 500


# ==================== INITIALIZATION ====================

def init_db():
    with app.app_context():
        db.create_all()
        logger.info("✅ Database initialized")


if __name__ == "__main__":
    init_db()
    print("\n" + "=" * 60)
    print("🚀 Healthnexus AI Backend Server Starting...")
    print("=" * 60)
    print(f"📊 ML Model Status: {'✅ Loaded' if ranker else '❌ Not Available'}")
    print("🌐 API Endpoint: http://localhost:5001")
    print("📚 Health Check: http://localhost:5001/api/health")
    print("=" * 60 + "\n")

    # Keep backend stable for local demo/use: single process, no watchdog reloader.
    app.run(debug=False, use_reloader=False,
            threaded=True, port=5001, host="0.0.0.0")

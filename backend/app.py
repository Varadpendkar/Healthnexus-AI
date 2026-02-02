"""
Healthnexus AI - Flask Backend API
Insurance plan recommendation system powered by LightGBM ML model
"""
from ranker import PlanRanker
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'healthnexus-ai-secret-key-2026'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-healthnexus-2026'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthnexus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for React frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import ML ranker

# Initialize ranker with model path
PROJECT_ROOT = Path(__file__).parent
MODEL_PATH = PROJECT_ROOT.parent / 'shared' / 'models' / 'plan_ranker.pkl'
DATA_PATH = PROJECT_ROOT.parent / 'shared' / 'data'

try:
    ranker = PlanRanker(MODEL_PATH, DATA_PATH)
    logger.info("✅ ML Model loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load ML model: {e}")
    ranker = None


# ==================== DATABASE MODELS ====================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class SavedPlan(db.Model):
    __tablename__ = 'saved_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.String(50), nullable=False)
    plan_name = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    premium = db.Column(db.Float, nullable=False)
    coverage_amount = db.Column(db.Float, nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='saved_plans')


# ==================== API ROUTES ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Healthnexus AI API is running',
        'ml_model_loaded': ranker is not None,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate input
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 409

        # Create new user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Generate token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400

        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Generate token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    Get personalized insurance plan recommendations using ML model

    Request body:
    {
        "age": 30,
        "annual_income": 800000,
        "gender": "male",
        "city": "Mumbai",
        "state": "Maharashtra",
        "has_diabetes": true,
        "coverage_amount": 500000,
        "premium_budget": 5000,
        "limit": 8
    }
    """
    try:
        if ranker is None:
            return jsonify({'error': 'ML model not available'}), 503

        data = request.get_json()

        # Validate required fields
        if not data.get('age'):
            return jsonify({'error': 'Age is required'}), 400

        # Extract user profile
        user_profile = {
            'user_id': data.get('user_id', 'anonymous'),
            'age': int(data.get('age', 35)),
            'gender': data.get('gender', 'male'),
            'annual_income': float(data.get('annual_income', 600000)),
            'income_band': data.get('income_band'),
            'city': data.get('city', 'Mumbai'),
            'state': data.get('state', 'Maharashtra'),
            'marital_status': data.get('marital_status', 'single'),
            'dependents': int(data.get('dependents', 0)),
            'occupation_type': data.get('occupation_type', 'salaried'),
            'plan_type': data.get('plan_type', 'individual'),

            # Health conditions
            'has_diabetes': data.get('has_diabetes', False),
            'has_hypertension': data.get('has_hypertension', False),
            'has_heart_disease': data.get('has_heart_disease', False),
            'has_asthma': data.get('has_asthma', False),
            'has_obesity': data.get('has_obesity', False),
            'has_thyroid': data.get('has_thyroid', False),

            # Preferences
            'smoking_flag': data.get('smoking_flag', False),
            'coverage_amount': float(data.get('coverage_amount', 500000)),
            'premium_budget': float(data.get('premium_budget', 5000)),
            'preferred_providers': data.get('preferred_providers', []),

            # Additional fields
            'claim_history_count': int(data.get('claim_history_count', 0)),
            'renewal_loyalty_years': int(data.get('renewal_loyalty_years', 0)),
            'risk_score': float(data.get('risk_score', 0.5)),
        }

        # Get limit
        limit = int(data.get('limit', 8))

        # Get recommendations from ML model
        logger.info(
            f"Getting recommendations for user: age={user_profile['age']}, income={user_profile['annual_income']}")
        recommendations = ranker.rank(user_profile, k=limit)

        if not recommendations:
            return jsonify({
                'error': 'No recommendations available',
                'message': 'Please try adjusting your preferences'
            }), 404

        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'user_profile': {
                'age': user_profile['age'],
                'city': user_profile['city'],
                'conditions': [k.replace('has_', '') for k, v in user_profile.items() if k.startswith('has_') and v]
            },
            'total_plans_evaluated': len(recommendations),
            'ml_model_version': '1.0'
        }), 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate recommendations'}), 500


@app.route('/api/plans/<plan_id>', methods=['GET'])
def get_plan_details(plan_id):
    """Get detailed information about a specific plan"""
    try:
        if ranker is None:
            return jsonify({'error': 'ML model not available'}), 503

        plan = ranker.get_plan_by_id(plan_id)

        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        return jsonify({
            'success': True,
            'plan': plan
        }), 200

    except Exception as e:
        logger.error(f"Error fetching plan details: {e}")
        return jsonify({'error': 'Failed to fetch plan details'}), 500


@app.route('/api/plans/save', methods=['POST'])
@jwt_required()
def save_plan():
    """Save a plan to user's favorites"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        saved_plan = SavedPlan(
            user_id=user_id,
            plan_id=data['plan_id'],
            plan_name=data['plan_name'],
            provider=data['provider'],
            premium=data['premium'],
            coverage_amount=data['coverage_amount']
        )

        db.session.add(saved_plan)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Plan saved successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error saving plan: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to save plan'}), 500


@app.route('/api/plans/saved', methods=['GET'])
@jwt_required()
def get_saved_plans():
    """Get user's saved plans"""
    try:
        user_id = get_jwt_identity()
        saved_plans = SavedPlan.query.filter_by(
            user_id=user_id).order_by(SavedPlan.saved_at.desc()).all()

        return jsonify({
            'success': True,
            'saved_plans': [{
                'id': plan.id,
                'plan_id': plan.plan_id,
                'plan_name': plan.plan_name,
                'provider': plan.provider,
                'premium': plan.premium,
                'coverage_amount': plan.coverage_amount,
                'saved_at': plan.saved_at.isoformat()
            } for plan in saved_plans]
        }), 200

    except Exception as e:
        logger.error(f"Error fetching saved plans: {e}")
        return jsonify({'error': 'Failed to fetch saved plans'}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database"""
    with app.app_context():
        db.create_all()
        logger.info("✅ Database initialized")


if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("🚀 Healthnexus AI Backend Server Starting...")
    print("="*60)
    print(f"📊 ML Model Status: {'✅ Loaded' if ranker else '❌ Not Available'}")
    print(f"🌐 API Endpoint: http://localhost:5000")
    print(f"📚 Health Check: http://localhost:5000/api/health")
    print("="*60 + "\n")

    app.run(debug=True, port=5001, host='0.0.0.0')

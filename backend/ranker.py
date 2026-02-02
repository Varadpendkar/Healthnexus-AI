"""
Plan Ranker - LightGBM ML Model Integration
Loads the trained model and provides plan ranking functionality
"""
import pickle
import logging
from pathlib import Path
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class PremiumCalculator:
    """Calculate realistic health insurance premiums"""

    BASE_PREMIUM_PER_LAKH = {
        '18-25': 500,
        '26-35': 750,
        '36-45': 1200,
        '46-55': 2000,
        '56-65': 3500,
        '65+': 5000
    }

    CONDITION_LOADING = {
        'diabetes': 25,
        'hypertension': 20,
        'heart_disease': 40,
        'obesity': 15,
        'asthma': 10,
        'thyroid': 8,
    }

    @staticmethod
    def get_age_band(age: int) -> str:
        if age <= 25:
            return '18-25'
        elif age <= 35:
            return '26-35'
        elif age <= 45:
            return '36-45'
        elif age <= 55:
            return '46-55'
        elif age <= 65:
            return '56-65'
        else:
            return '65+'

    @staticmethod
    def calculate_premium(coverage_amount: float, age: int, conditions: list) -> dict:
        """Calculate realistic premium with condition loading"""
        age_band = PremiumCalculator.get_age_band(age)
        premium_per_lakh = PremiumCalculator.BASE_PREMIUM_PER_LAKH[age_band]
        coverage_in_lakhs = coverage_amount / 100000

        base_premium = coverage_in_lakhs * premium_per_lakh

        # Apply condition loading
        total_loading = 0
        for condition in conditions:
            condition_lower = condition.lower()
            if condition_lower in PremiumCalculator.CONDITION_LOADING:
                total_loading += PremiumCalculator.CONDITION_LOADING[condition_lower]

        total_loading = min(total_loading, 100)  # Cap at 100%
        adjusted_premium = base_premium * (1 + total_loading / 100)

        return {
            'base': float(base_premium),
            'age_factor': float(premium_per_lakh),
            'condition_loading': float(total_loading),
            'annual_premium': float(adjusted_premium),
            'monthly_premium': float(adjusted_premium / 12)
        }


class PlanRanker:
    """Insurance Plan Recommender using trained LightGBM model"""

    def __init__(self, model_path: Path, data_path: Path):
        """
        Initialize the ranker with model and data

        Args:
            model_path: Path to plan_ranker.pkl file
            data_path: Path to directory containing CSV files
        """
        self.model_path = Path(model_path)
        self.data_path = Path(data_path)

        # Load model
        logger.info(f"Loading ML model from: {self.model_path}")
        with open(self.model_path, 'rb') as f:
            artifacts = pickle.load(f)
            self.model = artifacts['model']
            self.feature_columns = artifacts.get(
                'feature_cols', artifacts.get('feature_columns', []))
            self.label_encoders = artifacts.get('label_encoders', {})

        # If feature columns not in pickle, recover from model
        if not self.feature_columns:
            self.feature_columns = list(self.model.booster_.feature_name())

        logger.info(
            f"✅ Model loaded with {len(self.feature_columns)} features")

        # Load data
        self.plans = pd.read_csv(self.data_path / 'plans.csv')
        logger.info(f"✅ Loaded {len(self.plans)} plans")

        # Load network data
        plan_hospital_map = pd.read_csv(
            self.data_path / 'plan_hospital_map_large.csv')
        hospitals = pd.read_csv(self.data_path / 'hospitals_large.csv')

        # Calculate network statistics
        network_stats = plan_hospital_map.groupby('plan_id').agg({
            'hospital_id': 'count',
            'distance_score': 'mean',
            'contract_type': [
                lambda x: (x == 'cashless').sum() / len(x) * 100,
                lambda x: (x == 'reimbursement').sum() / len(x) * 100
            ]
        }).reset_index()
        network_stats.columns = ['planid', 'network_size_actual', 'avg_distance_score',
                                 'cashless_percentage', 'reimbursement_percentage']

        # Merge network stats
        self.plans = self.plans.merge(network_stats, on='planid', how='left')
        self.plans['networksize'] = self.plans['network_size_actual'].fillna(
            self.plans['networksize'])
        self.plans = self.plans.drop('network_size_actual', axis=1)

        # Filter out inappropriate plans
        exclude_categories = [
            'Government Scheme', 'PMJAY', 'Ayushman', 'Life Insurance',
            'Term Plan', 'Term Insurance', 'TROP', 'Return of Premium'
        ]

        for exclude_term in exclude_categories:
            self.plans = self.plans[
                ~self.plans['plan_category'].str.contains(exclude_term, case=False, na=False) &
                ~self.plans['plan_name'].str.contains(
                    exclude_term, case=False, na=False)
            ]

        # Filter unrealistic premiums
        self.plans = self.plans[self.plans['premium'] > 0]

        logger.info(
            f"✅ Filtered to {len(self.plans)} valid health insurance plans")

    def _create_features(self, user: dict, plans_df: pd.DataFrame) -> pd.DataFrame:
        """Create feature matrix for ML model"""
        df = plans_df.copy()

        # User attributes
        user_age = user.get('age', 35)
        user_income = user.get('annual_income', 600000)
        user_dependents = user.get('dependents', 0)
        user_smoking = user.get('smoking_flag', False)

        # Plan attributes
        df['plan_premium'] = pd.to_numeric(
            df.get('premium', 0), errors='coerce').fillna(0)
        df['plan_deductible'] = pd.to_numeric(
            df.get('deductible', 0), errors='coerce').fillna(0)
        df['plan_coverage'] = pd.to_numeric(
            df.get('coverageamount', 0), errors='coerce').fillna(0)
        df['plan_network'] = pd.to_numeric(
            df.get('networksize', 0), errors='coerce').fillna(0)

        # Feature engineering
        df['premium_income_ratio'] = df['plan_premium'] / (user_income + 1e-9)
        df['premium_coverage_ratio'] = df['plan_premium'] / \
            (df['plan_coverage'] + 1e-9)
        df['network_per_100'] = df['plan_network'] / 100.0

        # User features
        df['user_age'] = float(user_age)
        df['dependents_count'] = float(user_dependents)
        df['smoking_flag'] = 1.0 if user_smoking else 0.0
        df['claim_history'] = float(user.get('claim_history_count', 0))
        df['renewal_years'] = float(user.get('renewal_loyalty_years', 0))
        df['user_risk_score'] = float(user.get('risk_score', 0.5))

        # Age match
        df['age_match'] = 0.0

        # Risk profile
        df['risk_num'] = 1.0

        # Interaction features
        df['age_premium_interaction'] = df['user_age'] * \
            df['premium_income_ratio']
        df['income_coverage_interaction'] = (
            user_income / 1e6) * (df['plan_coverage'] / 1e6)
        df['risk_smoking_interaction'] = df['risk_num'] * df['smoking_flag']

        return df

    def _generate_explanation(self, user: dict, plan: dict, score: float) -> dict:
        """Generate explanation for plan recommendation"""
        reasons = []

        # Extract conditions
        user_conditions = []
        for condition in ['diabetes', 'hypertension', 'heart_disease', 'obesity', 'asthma']:
            if user.get(f'has_{condition}'):
                user_conditions.append(condition.title())

        # Affordability
        income = user.get('annual_income', 600000)
        premium = plan.get('premium', 0)
        premium_pct = (premium * 12 / income * 100) if income > 0 else 0

        if user_conditions and premium_pct < 10:
            reasons.append(
                f"Affordable with {', '.join(user_conditions[:2])} at {premium_pct:.1f}% of income")
        elif premium_pct < 5:
            reasons.append(
                f"Highly affordable at {premium_pct:.1f}% of annual income")
        elif premium_pct < 8:
            reasons.append(
                f"Reasonably priced at {premium_pct:.1f}% of annual income")

        # Coverage
        coverage = plan.get('coverageamount', 0)
        if user_conditions:
            if coverage >= 1000000:
                reasons.append(
                    f"₹{coverage/100000:.0f}L coverage for managing {', '.join(user_conditions[:2])}")
            elif coverage >= 500000:
                reasons.append(f"₹{coverage/100000:.0f}L adequate coverage")
        else:
            if coverage >= 1000000:
                reasons.append(
                    f"Comprehensive ₹{coverage/100000:.0f}L coverage")
            elif coverage >= 500000:
                reasons.append(f"Adequate ₹{coverage/100000:.0f}L coverage")

        # Network
        network = plan.get('networksize', 0)
        if network > 100:
            reasons.append(f"Extensive network of {int(network)} hospitals")
        elif network > 50:
            reasons.append(f"Good network of {int(network)} hospitals")

        # Claim approval
        rejection_rate = plan.get('claimrejectionrate', 0)
        if rejection_rate < 1.0:
            approval_rate = 100 - rejection_rate
            reasons.append(
                f"Excellent {approval_rate:.1f}% claim approval rate")

        # Ensure minimum reasons
        while len(reasons) < 3:
            reasons.append("AI-matched to your health profile")

        return {
            'bullets': reasons[:5],
            'explain_text': ' | '.join(reasons[:3]),
            'conditions_considered': user_conditions
        }

    def rank(self, user: dict, k: int = 8) -> list:
        """
        Rank insurance plans for a user

        Args:
            user: User profile dictionary
            k: Number of top plans to return

        Returns:
            List of top k ranked plans with scores and explanations
        """
        try:
            plans = self.plans.copy()

            # Create features
            features_df = self._create_features(user, plans)

            # Prepare feature matrix
            X_full = features_df

            # Add missing columns with zeros
            missing_cols = [
                c for c in self.feature_columns if c not in X_full.columns]
            if missing_cols:
                for col in missing_cols:
                    X_full[col] = 0.0

            # Ensure exact column order
            X_full = X_full[self.feature_columns].astype(float)

            # Predict scores
            scores = self.model.predict(X_full)

            # Add scores to plans
            plans['score'] = scores

            # Sort and get top k
            top_plans = plans.sort_values('score', ascending=False).head(k)

            # Format results
            recommendations = []
            for idx, (_, row) in enumerate(top_plans.iterrows(), 1):
                plan_dict = row.to_dict()

                # Extract user conditions
                conditions = []
                for condition in ['diabetes', 'hypertension', 'heart_disease', 'obesity', 'asthma']:
                    if user.get(f'has_{condition}'):
                        conditions.append(condition)

                # Calculate realistic premium
                coverage = float(plan_dict.get(
                    'coverageamount', user.get('coverage_amount', 500000)))
                age = int(user.get('age', 35))

                premium_calc = PremiumCalculator.calculate_premium(
                    coverage, age, conditions)

                # Generate explanation
                explanation = self._generate_explanation(
                    user,
                    {**plan_dict, 'premium': premium_calc['annual_premium']},
                    plan_dict['score']
                )

                # Build recommendation
                rec = {
                    'rank': idx,
                    'plan_id': str(plan_dict.get('planid', '')),
                    'plan_name': str(plan_dict.get('plan_name', '')),
                    'provider': str(plan_dict.get('provider', '')),
                    'premium': float(premium_calc['annual_premium']),
                    'monthly_premium': float(premium_calc['monthly_premium']),
                    'deductible': float(plan_dict.get('deductible', 0)),
                    'copay': float(plan_dict.get('copay', 0)),
                    'coverage_amount': float(coverage),
                    'network_size': int(plan_dict.get('networksize', 0)),
                    'claim_rejection_rate': float(plan_dict.get('claimrejectionrate', 0)),
                    'score': float(plan_dict['score']),
                    'confidence': float(min(plan_dict['score'] / max(scores) if max(scores) > 0 else 0, 1.0)),
                    'bullets': explanation['bullets'],
                    'explain_text': explanation['explain_text'],
                    'plan_type': str(plan_dict.get('plan_type', 'individual')),
                    'plan_category': str(plan_dict.get('plan_category', '')),
                    'premium_breakdown': {
                        'base': premium_calc['base'],
                        'age_factor': premium_calc['age_factor'],
                        'condition_loading': premium_calc['condition_loading'],
                        'total': premium_calc['annual_premium']
                    },
                    'conditions_considered': explanation.get('conditions_considered', [])
                }

                recommendations.append(rec)

            return recommendations

        except Exception as e:
            logger.error(f"Ranking failed: {e}", exc_info=True)
            return []

    def get_plan_by_id(self, plan_id: str) -> dict:
        """Get plan details by ID"""
        try:
            plan = self.plans[self.plans['planid'].astype(str) == str(plan_id)]
            if plan.empty:
                return None

            return plan.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Error fetching plan: {e}")
            return None

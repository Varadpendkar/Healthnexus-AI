from __future__ import annotations

"""
Plan Ranker - LightGBM ML Model Integration
Loads the trained model and provides plan ranking functionality
"""
import pickle
import logging
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd

from ml.model_registry import load_latest_artifact

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

        # Load model (prefer latest registered artifact, fallback to legacy pkl)
        logger.info(f"Loading ML model from: {self.model_path}")
        registry_artifact = load_latest_artifact(self.model_path.parent)

        if registry_artifact:
            artifacts = registry_artifact
            logger.info("✅ Loaded latest registered model artifact")
        else:
            with open(self.model_path, 'rb') as f:
                artifacts = pickle.load(f)

        self.model = artifacts['model']
        self.feature_columns = artifacts.get(
            'feature_cols', artifacts.get('feature_columns', []))
        self.label_encoders = artifacts.get('label_encoders', {})
        self.model_version = artifacts.get('model_version', 'legacy-1.0')

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

    def _normalize_text(self, value) -> str:
        return str(value or "").strip().lower()

    def _apply_candidate_filters(self, user: dict, plans_df: pd.DataFrame) -> pd.DataFrame:
        """Apply business constraints before ML scoring to reduce stale/same outputs."""
        if plans_df.empty:
            return plans_df

        filtered = plans_df.copy()

        # 1) Plan type alignment
        user_plan_type = self._normalize_text(user.get('plan_type'))
        if user_plan_type in {'individual', 'floater'} and 'plan_type' in filtered.columns:
            typed = filtered[filtered['plan_type'].astype(
                str).str.lower() == user_plan_type]
            if len(typed) >= 20:
                filtered = typed

        # 2) Budget alignment (soft filter)
        budget = float(user.get('premium_budget', 0) or 0)
        if budget > 0 and 'premium' in filtered.columns:
            premium_vals = pd.to_numeric(
                filtered['premium'], errors='coerce').fillna(0.0)
            upper = max(budget * 1.35, budget + 1200)
            lower = max(500.0, budget * 0.35)
            budget_filtered = filtered[(
                premium_vals >= lower) & (premium_vals <= upper)]
            if len(budget_filtered) >= 25:
                filtered = budget_filtered

        # 3) Coverage alignment (soft filter)
        coverage_pref = float(user.get('coverage_amount', 0) or 0)
        if coverage_pref > 0 and 'coverageamount' in filtered.columns:
            coverage_vals = pd.to_numeric(
                filtered['coverageamount'], errors='coerce').fillna(0.0)
            cov_filtered = filtered[(
                coverage_vals >= coverage_pref * 0.55) & (coverage_vals <= coverage_pref * 2.8)]
            if len(cov_filtered) >= 20:
                filtered = cov_filtered

        # 4) Network floor for city users (soft preference)
        if user.get('city') and 'networksize' in filtered.columns and len(filtered) > 30:
            network_vals = pd.to_numeric(
                filtered['networksize'], errors='coerce').fillna(0.0)
            floor = max(20.0, float(network_vals.quantile(0.20)))
            network_filtered = filtered[network_vals >= floor]
            if len(network_filtered) >= 20:
                filtered = network_filtered

        return filtered if len(filtered) >= 15 else plans_df

    def _apply_behavior_bias(self, user: dict, scored_df: pd.DataFrame) -> pd.DataFrame:
        """Add lightweight personalization from user preferences/history without retraining."""
        if scored_df.empty:
            return scored_df

        df = scored_df.copy()
        df['adjusted_score'] = pd.to_numeric(
            df['score'], errors='coerce').fillna(0.0)

        preferred = [self._normalize_text(p)
                     for p in (user.get('preferred_providers') or []) if self._normalize_text(p)]
        provider_series = df.get('provider', '').astype(str).str.lower()

        if preferred:
            provider_boost = provider_series.apply(
                lambda p: 0.10 if any(pref in p for pref in preferred) else 0.0)
            df['adjusted_score'] = df['adjusted_score'] + provider_boost

        # If user has claim history, slightly prefer plans with lower claim rejection rate.
        claim_history = float(user.get('claim_history_count', 0) or 0)
        if claim_history > 0 and 'claimrejectionrate' in df.columns:
            rejection = pd.to_numeric(
                df['claimrejectionrate'], errors='coerce').fillna(0.0)
            penalty = np.clip(rejection / 100.0, 0, 0.12) * \
                min(0.12, 0.02 * claim_history)
            df['adjusted_score'] = df['adjusted_score'] - penalty

        return df

    def _stable_noise(self, user_key: str, plan_key: str) -> float:
        """Small deterministic jitter for tie-breaking among near-equal plans."""
        digest = hashlib.md5(
            f"{user_key}|{plan_key}".encode('utf-8')).hexdigest()
        value = int(digest[:8], 16) / 0xFFFFFFFF
        return (value - 0.5) * 0.02

    def _rerank_with_diversity(self, ranked_df: pd.DataFrame, k: int) -> pd.DataFrame:
        """Greedy diversity reranking to avoid same-provider dominance in top-k."""
        if ranked_df.empty:
            return ranked_df

        pool_size = min(len(ranked_df), max(k * 5, 30))
        pool = ranked_df.head(pool_size).copy()
        selected_rows = []
        provider_counts = {}

        while len(selected_rows) < min(k, len(pool)):
            best_idx = None
            best_val = -10**9
            for idx, row in pool.iterrows():
                provider = self._normalize_text(row.get('provider'))
                used_count = provider_counts.get(provider, 0)
                diversity_penalty = 0.08 * used_count
                novelty_boost = 0.02 if len(
                    selected_rows) < 3 and used_count == 0 else 0.0
                val = float(row.get('adjusted_score', row.get(
                    'score', 0.0))) - diversity_penalty + novelty_boost
                if val > best_val:
                    best_val = val
                    best_idx = idx

            if best_idx is None:
                break

            picked = pool.loc[best_idx]
            selected_rows.append(picked)
            provider = self._normalize_text(picked.get('provider'))
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            pool = pool.drop(index=best_idx)

        if not selected_rows:
            return ranked_df.head(k)

        selected_df = pd.DataFrame(selected_rows)

        if len(selected_df) < k:
            already = set(selected_df.get(
                'planid', pd.Series(dtype=str)).astype(str).tolist())
            extra = ranked_df[~ranked_df.get('planid', pd.Series(dtype=str)).astype(
                str).isin(already)].head(k - len(selected_df))
            selected_df = pd.concat([selected_df, extra], ignore_index=True)

        return selected_df.head(k)

    def _explore_select_within_top(
        self,
        ranked_df: pd.DataFrame,
        k: int,
        seed: int | None = None,
        temperature: float = 0.85,
    ) -> pd.DataFrame:
        """Stochastic selection from top-quality plans for controlled recommendation variety."""
        if ranked_df.empty:
            return ranked_df

        score_col = 'adjusted_score' if 'adjusted_score' in ranked_df.columns else 'score'

        # Keep exploration constrained to high-quality candidates.
        pool_size = min(len(ranked_df), max(k * 6, 36))
        pool = ranked_df.head(pool_size).copy()

        pool_scores = pd.to_numeric(
            pool[score_col], errors='coerce').fillna(0.0)
        best_score = float(pool_scores.max()) if len(pool_scores) else 0.0
        score_std = float(pool_scores.std()) if len(pool_scores) > 1 else 0.0
        quality_floor = best_score - max(0.018, score_std * 0.75)

        quality_pool = pool[pool_scores >= quality_floor].copy()
        if len(quality_pool) < max(k, 6):
            quality_pool = pool.head(max(k * 3, 18)).copy()

        temp = float(np.clip(temperature, 0.35, 1.75))
        rng = np.random.default_rng(seed)

        selected_rows = []
        provider_counts = {}
        available = quality_pool.copy()
        target_count = min(k, len(quality_pool))

        while len(selected_rows) < target_count:
            if available.empty:
                break

            avail_scores = pd.to_numeric(
                available[score_col], errors='coerce').fillna(0.0).to_numpy(dtype=float)
            centered_scores = (avail_scores - np.max(avail_scores)) / temp
            base_weights = np.exp(centered_scores)

            provider_values = (
                available['provider'].astype(str).tolist()
                if 'provider' in available.columns
                else [''] * len(available)
            )
            provider_penalty = np.array(
                [
                    0.75 ** provider_counts.get(
                        self._normalize_text(provider), 0)
                    for provider in provider_values
                ],
                dtype=float,
            )

            weights = base_weights * provider_penalty
            weight_sum = float(weights.sum())
            if weight_sum <= 0:
                probs = np.ones(len(available), dtype=float) / len(available)
            else:
                probs = weights / weight_sum

            choice_pos = int(rng.choice(len(available), p=probs))
            choice_idx = available.index[choice_pos]
            picked = available.iloc[choice_pos]

            selected_rows.append(picked)
            provider = self._normalize_text(picked.get('provider'))
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            available = available.drop(index=choice_idx)

        if not selected_rows:
            return ranked_df.head(k)

        selected_df = pd.DataFrame(selected_rows)

        if len(selected_df) < k:
            already = set(selected_df.get(
                'planid', pd.Series(dtype=str)).astype(str).tolist())
            extra = ranked_df[~ranked_df.get('planid', pd.Series(dtype=str)).astype(
                str).isin(already)].head(k - len(selected_df))
            selected_df = pd.concat([selected_df, extra], ignore_index=True)

        return selected_df.head(k)

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

    def rank(
        self,
        user: dict,
        k: int = 8,
        explore_mode: bool = False,
        explore_seed: int | None = None,
        explore_temperature: float = 0.85,
    ) -> list:
        """
        Rank insurance plans for a user

        Args:
            user: User profile dictionary
            k: Number of top plans to return
            explore_mode: If True, sample from top-quality plans for variety
            explore_seed: Optional random seed for reproducible exploration
            explore_temperature: Exploration intensity (higher => more variety)

        Returns:
            List of top k ranked plans with scores and explanations
        """
        try:
            plans = self._apply_candidate_filters(user, self.plans.copy())

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

            # Add lightweight behavior-aware score shaping
            plans = self._apply_behavior_bias(user, plans)

            # Deterministic tie-break for near-equal candidates
            user_key = f"{user.get('user_id', 'anonymous')}|{user.get('age', 0)}|{user.get('city', '')}|{user.get('plan_type', '')}"
            best_score = float(
                plans['adjusted_score'].max()) if len(plans) else 0.0
            score_band = max(0.01, float(
                np.std(plans['adjusted_score'])) * 0.12) if len(plans) > 1 else 0.01
            near_tie_mask = (
                best_score - plans['adjusted_score']) <= score_band
            if near_tie_mask.any():
                plans.loc[near_tie_mask, 'adjusted_score'] = plans.loc[near_tie_mask].apply(
                    lambda row: float(
                        row['adjusted_score']) + self._stable_noise(user_key, str(row.get('planid', ''))),
                    axis=1,
                )

            ranked = plans.sort_values(
                ['adjusted_score', 'score'], ascending=False)

            if explore_mode:
                top_plans = self._explore_select_within_top(
                    ranked,
                    k=k,
                    seed=explore_seed,
                    temperature=explore_temperature,
                )
            else:
                top_plans = self._rerank_with_diversity(ranked, k)

            max_final_score = float(
                ranked['adjusted_score'].max()) if len(ranked) else 1.0
            max_final_score = max(max_final_score, 1e-9)

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
                    'score': float(plan_dict.get('adjusted_score', plan_dict.get('score', 0.0))),
                    'confidence': float(min(float(plan_dict.get('adjusted_score', 0.0)) / max_final_score, 1.0)),
                    'model_version': self.model_version,
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

    def explain_recommendations(self, user: dict, k: int = 5, top_features: int = 5) -> list:
        """Return top-k recommendation explanations with feature contributions."""
        try:
            plans = self.plans.copy()
            features_df = self._create_features(user, plans)

            missing_cols = [
                c for c in self.feature_columns if c not in features_df.columns]
            for col in missing_cols:
                features_df[col] = 0.0

            X = features_df[self.feature_columns].astype(float)
            scores = self.model.predict(X)

            plans['score'] = scores
            plans = plans.sort_values('score', ascending=False).head(k)

            importances = getattr(self.model, 'feature_importances_', None)
            if importances is None:
                importances = np.ones(len(self.feature_columns))

            out = []
            for _, row in plans.iterrows():
                idx = row.name
                row_x = X.iloc[idx]
                contrib = np.abs(row_x.to_numpy() * np.asarray(importances))

                top_idx = np.argsort(contrib)[::-1][:top_features]
                top = []
                for i in top_idx:
                    feat = self.feature_columns[i]
                    top.append({
                        'feature': feat,
                        'feature_value': float(row_x.iloc[i]),
                        'importance': float(importances[i]),
                        'contribution': float(contrib[i])
                    })

                out.append({
                    'plan_id': str(row.get('planid', '')),
                    'plan_name': str(row.get('plan_name', '')),
                    'provider': str(row.get('provider', '')),
                    'score': float(row.get('score', 0.0)),
                    'model_version': self.model_version,
                    'top_features': top,
                })

            return out
        except Exception as e:
            logger.error(f"Explainability failed: {e}", exc_info=True)
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

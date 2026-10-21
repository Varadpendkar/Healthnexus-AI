from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd


@dataclass
class DatasetBundle:
    dataframe: pd.DataFrame
    feature_columns: list[str]
    target_column: str
    group_column: str


def load_base_data(data_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    plans = pd.read_csv(data_dir / "plans.csv")
    users = pd.read_csv(data_dir / "users.csv")
    interactions = pd.read_csv(data_dir / "interactions.csv")
    return plans, users, interactions


def build_training_frame(data_dir: Path) -> DatasetBundle:
    plans, users, interactions = load_base_data(data_dir)

    plans = plans.rename(columns={"planid": "plan_id"})
    interactions = interactions.rename(columns={"planid": "plan_id"})

    plans_num_cols = [
        "premium",
        "deductible",
        "copay",
        "coverageamount",
        "networksize",
        "claimrejectionrate",
        "waitingperioddays",
        "max_out_of_pocket",
    ]
    for col in plans_num_cols:
        if col in plans.columns:
            plans[col] = pd.to_numeric(plans[col], errors="coerce").fillna(0.0)

    users["risk_score"] = pd.to_numeric(
        users.get("risk_score", 0.5), errors="coerce").fillna(0.5)
    users["dependents"] = pd.to_numeric(
        users.get("dependents", 0), errors="coerce").fillna(0)
    users["claim_history_count"] = pd.to_numeric(
        users.get("claim_history_count", 0), errors="coerce").fillna(0)
    users["renewal_loyalty_years"] = pd.to_numeric(
        users.get("renewal_loyalty_years", 0), errors="coerce").fillna(0)

    merged = interactions.merge(users, on="user_id", how="left").merge(
        plans, on="plan_id", how="left")

    # Robust target: explicit label if present, otherwise event weighting.
    merged["label"] = pd.to_numeric(merged.get(
        "label", 0), errors="coerce").fillna(0)
    event_bonus = {
        "purchase": 1.0,
        "buy": 1.0,
        "quote_submit": 0.8,
        "shortlist": 0.7,
        "view": 0.3,
        "click": 0.2,
    }
    merged["event_weight"] = merged.get("event_type", "").astype(
        str).str.lower().map(event_bonus).fillna(0.1)
    merged["target"] = np.maximum(
        merged["label"], merged["event_weight"])  # 0..1

    # Feature engineering
    merged["premium_income_ratio"] = merged["premium"] / \
        (merged.get("avg_annual_spend", 1).replace(0, 1) + 1)
    merged["coverage_to_premium"] = merged["coverageamount"] / \
        (merged["premium"] + 1)
    merged["network_per_copay"] = merged["networksize"] / (merged["copay"] + 1)
    merged["risk_premium_interaction"] = merged["risk_score"] * merged["premium"]
    merged["risk_coverage_interaction"] = merged["risk_score"] * \
        merged["coverageamount"]

    bool_cols = [
        "has_diabetes",
        "has_hypertension",
        "has_asthma",
        "has_heart_disease",
        "has_thyroid",
        "has_obesity",
        "has_cancer_history",
        "smoking_status",
    ]

    for col in bool_cols:
        if col not in merged.columns:
            merged[col] = 0

    if "smoking_status" in merged.columns:
        merged["smoking_status"] = merged["smoking_status"].astype(
            str).str.lower().isin(["yes", "smoker", "true", "1"]).astype(int)

    for col in bool_cols:
        if col != "smoking_status":
            merged[col] = merged[col].astype(str).str.lower().isin(
                ["true", "1", "yes"]).astype(int)

    cat_cols = ["gender", "marital_status", "region",
                "provider", "plan_type", "plan_tier", "plan_category"]
    for col in cat_cols:
        if col not in merged.columns:
            merged[col] = "unknown"
        merged[col] = merged[col].astype(str).fillna("unknown")

    # Preserve fairness slicing columns before one-hot encoding.
    merged["gender_raw"] = merged["gender"]
    merged["region_raw"] = merged["region"]

    merged = pd.get_dummies(merged, columns=cat_cols, dummy_na=False)

    feature_columns = [
        c
        for c in merged.columns
        if c
        not in {
            "target",
            "label",
            "event_type",
            "date",
            "user_id",
            "plan_id",
            "addons",
            "geos",
            "occupation",
            "preferred_providers",
            "chronic_conditions",
            "family_medical_history",
            "existing_health_policy",
            "urban_rural",
            "preferred_payment_mode",
            "age_band_18_35_premium",
            "age_band_36_50_premium",
            "age_band_51_65_premium",
            "gender_raw",
            "region_raw",
        }
    ]

    # Keep only numeric features.
    numeric_feature_columns = []
    for col in feature_columns:
        if pd.api.types.is_numeric_dtype(merged[col]):
            merged[col] = pd.to_numeric(
                merged[col], errors="coerce").fillna(0.0)
            numeric_feature_columns.append(col)

    return DatasetBundle(
        dataframe=merged,
        feature_columns=numeric_feature_columns,
        target_column="target",
        group_column="user_id",
    )


def build_inference_features(user_profile: Dict, plans_df: pd.DataFrame, training_feature_columns: list[str]) -> pd.DataFrame:
    df = plans_df.copy()
    if "planid" in df.columns and "plan_id" not in df.columns:
        df = df.rename(columns={"planid": "plan_id"})

    df["premium"] = pd.to_numeric(
        df.get("premium", 0), errors="coerce").fillna(0.0)
    df["deductible"] = pd.to_numeric(
        df.get("deductible", 0), errors="coerce").fillna(0.0)
    df["copay"] = pd.to_numeric(
        df.get("copay", 0), errors="coerce").fillna(0.0)
    df["coverageamount"] = pd.to_numeric(
        df.get("coverageamount", 0), errors="coerce").fillna(0.0)
    df["networksize"] = pd.to_numeric(
        df.get("networksize", 0), errors="coerce").fillna(0.0)
    df["claimrejectionrate"] = pd.to_numeric(
        df.get("claimrejectionrate", 0), errors="coerce").fillna(0.0)

    annual_income = float(user_profile.get("annual_income", 600000) or 600000)
    risk_score = float(user_profile.get("risk_score", 0.5) or 0.5)

    df["premium_income_ratio"] = df["premium"] / (annual_income + 1)
    df["coverage_to_premium"] = df["coverageamount"] / (df["premium"] + 1)
    df["network_per_copay"] = df["networksize"] / (df["copay"] + 1)
    df["risk_premium_interaction"] = risk_score * df["premium"]
    df["risk_coverage_interaction"] = risk_score * df["coverageamount"]

    df["risk_score"] = risk_score
    df["dependents"] = int(user_profile.get("dependents", 0) or 0)
    df["claim_history_count"] = int(
        user_profile.get("claim_history_count", 0) or 0)
    df["renewal_loyalty_years"] = int(
        user_profile.get("renewal_loyalty_years", 0) or 0)

    bool_map = {
        "has_diabetes": user_profile.get("has_diabetes", False),
        "has_hypertension": user_profile.get("has_hypertension", False),
        "has_asthma": user_profile.get("has_asthma", False),
        "has_heart_disease": user_profile.get("has_heart_disease", False),
        "has_thyroid": user_profile.get("has_thyroid", False),
        "has_obesity": user_profile.get("has_obesity", False),
        "has_cancer_history": user_profile.get("has_cancer_history", False),
        "smoking_status": user_profile.get("smoking_flag", False),
    }
    for col, value in bool_map.items():
        df[col] = int(bool(value))

    cat_base = {
        "gender": str(user_profile.get("gender", "unknown") or "unknown"),
        "marital_status": str(user_profile.get("marital_status", "unknown") or "unknown"),
        "region": str(user_profile.get("region", user_profile.get("city", "unknown")) or "unknown"),
        "provider": df.get("provider", "unknown"),
        "plan_type": df.get("plan_type", "individual"),
        "plan_tier": df.get("plan_tier", "standard"),
        "plan_category": df.get("plan_category", "health"),
    }

    for key, val in cat_base.items():
        if isinstance(val, pd.Series):
            df[key] = val.astype(str)
        else:
            df[key] = str(val)

    df = pd.get_dummies(df, columns=["gender", "marital_status", "region",
                        "provider", "plan_type", "plan_tier", "plan_category"], dummy_na=False)

    for col in training_feature_columns:
        if col not in df.columns:
            df[col] = 0.0

    features = df[training_feature_columns].copy()
    for col in features.columns:
        features[col] = pd.to_numeric(
            features[col], errors="coerce").fillna(0.0)

    return features

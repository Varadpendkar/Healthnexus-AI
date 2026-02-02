export interface UserProfile {
  age: number;
  gender: "male" | "female" | "other";
  annual_income: number;
  city: string;
  state: string;
  marital_status: string;
  dependents: number;
  occupation_type: string;
  smoking_flag: boolean;

  // Health conditions
  has_diabetes?: boolean;
  has_hypertension?: boolean;
  has_heart_disease?: boolean;
  has_asthma?: boolean;
  has_obesity?: boolean;
  has_thyroid?: boolean;

  // Preferences
  coverage_amount?: number;
  premium_budget?: number;
  plan_type: "individual" | "floater";
  preferred_providers?: string[];

  // Additional
  claim_history_count?: number;
  renewal_loyalty_years?: number;
  risk_score?: number;
}

export interface PlanRecommendation {
  rank: number;
  plan_id: string;
  plan_name: string;
  provider: string;
  premium: number;
  monthly_premium: number;
  coverage_amount: number;
  network_size: number;
  deductible: number;
  copay: number;
  claim_rejection_rate: number;
  score: number;
  confidence: number;
  bullets: string[];
  explain_text: string;
  plan_type: string;
  plan_category: string;
  premium_breakdown?: {
    base: number;
    age_factor: number;
    condition_loading: number;
    total: number;
  };
  conditions_considered: string[];
}

export interface ApiResponse {
  success: boolean;
  recommendations: PlanRecommendation[];
  user_profile?: {
    age: number;
    city: string;
    conditions: string[];
  };
  total_plans_evaluated: number;
  ml_model_version?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  message: string;
  access_token: string;
  user: User;
}

export interface SavedPlan {
  id: number;
  plan_id: string;
  plan_name: string;
  provider: string;
  premium: number;
  coverage_amount: number;
  saved_at: string;
}

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
  exploration?: {
    enabled: boolean;
    seed?: number | null;
    temperature?: number | null;
  };
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

export interface PatientConditions {
  asthma: boolean;
  hypertension: boolean;
  diabetes: boolean;
  heart_disease: boolean;
  thyroid: boolean;
  obesity: boolean;
}

export interface PatientReportProfile {
  name: string | null;
  age: number | null;
  gender: "male" | "female" | "other" | null;
  annual_income: number | null;
  city: string | null;
  state: string | null;
  marital_status: "single" | "married" | "divorced" | "widowed" | null;
  occupation_type: "salaried" | "self_employed" | "student" | "retired" | null;
  dependents: number | null;
  smoking_flag: boolean | null;
  plan_type: "individual" | "floater" | null;
  conditions: PatientConditions;
}

export interface PatientReportExtractionResponse {
  success: boolean;
  status: "success" | "error";
  profile?: PatientReportProfile;
  confidence?: Record<string, number>;
  missing_fields?: string[];
  raw_text_excerpt?: string;
  ocr_confidence?: number;
  extraction_source?: string;
  llm_used?: boolean;
  error?: string;
}

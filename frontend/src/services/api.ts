import axios from "axios";
import {
  UserProfile,
  ApiResponse,
  AuthResponse,
  SavedPlan,
  PatientReportExtractionResponse,
} from "../types/insurance";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5001";

const clearAuthStorage = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
};

const isLikelyJwt = (token: string | null): token is string => {
  if (!token || typeof token !== "string") return false;
  return token.split(".").length === 3;
};

const decodeJwtPayload = (token: string): Record<string, any> | null => {
  try {
    const payload = token.split(".")[1];
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized.padEnd(
      normalized.length + ((4 - (normalized.length % 4)) % 4),
      "=",
    );
    const decoded = atob(padded);
    return JSON.parse(decoded);
  } catch {
    return null;
  }
};

const parseApiErrorMessage = (error: any, fallback: string): string => {
  return (
    error?.userMessage ||
    error?.response?.data?.error ||
    error?.response?.data?.msg ||
    error?.response?.data?.message ||
    fallback
  );
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds for ML model processing
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (isLikelyJwt(token)) {
    config.headers.Authorization = `Bearer ${token}`;
  } else if (token) {
    // Stale/invalid token from older sessions should not be sent.
    clearAuthStorage();
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const msg = String(
      error?.response?.data?.msg || error?.response?.data?.error || "",
    ).toLowerCase();

    const looksLikeJwtIssue =
      msg.includes("token") ||
      msg.includes("jwt") ||
      msg.includes("signature") ||
      msg.includes("subject") ||
      msg.includes("header");

    if ((status === 401 || status === 422) && looksLikeJwtIssue) {
      clearAuthStorage();
      error.userMessage = "Your session has expired. Please log in again.";
    }

    return Promise.reject(error);
  },
);

// Insurance API
export const insuranceAPI = {
  getRecommendations: async (
    userProfile: UserProfile,
    limit: number = 8,
    options?: {
      exploreMode?: boolean;
      exploreSeed?: number;
      exploreTemperature?: number;
    },
  ): Promise<ApiResponse> => {
    try {
      const exploreMode = options?.exploreMode ?? true;
      const generatedSeed = Math.floor(
        (Date.now() + Math.random() * 1_000_000) % 2_147_483_647,
      );
      const exploreSeed = options?.exploreSeed ?? generatedSeed;
      const exploreTemperature = options?.exploreTemperature ?? 0.85;

      const response = await apiClient.post<ApiResponse>(
        "/api/recommendations",
        {
          ...userProfile,
          limit,
          explore_mode: exploreMode,
          explore_seed: exploreMode ? exploreSeed : undefined,
          explore_temperature: exploreMode ? exploreTemperature : undefined,
        },
      );
      return response.data;
    } catch (error: any) {
      console.error("API Error:", error);
      throw new Error(
        error.response?.data?.error || "Failed to get recommendations",
      );
    }
  },

  getPlanDetails: async (planId: string) => {
    const response = await apiClient.get(`/api/plans/${planId}`);
    return response.data;
  },

  savePlan: async (plan: any) => {
    try {
      const response = await apiClient.post("/api/plans/save", plan);
      return response.data;
    } catch (error: any) {
      throw new Error(parseApiErrorMessage(error, "Failed to save plan"));
    }
  },

  getSavedPlans: async (): Promise<SavedPlan[]> => {
    try {
      const response = await apiClient.get<{
        success: boolean;
        saved_plans: SavedPlan[];
      }>("/api/plans/saved");
      return response.data.saved_plans;
    } catch (error: any) {
      throw new Error(
        parseApiErrorMessage(error, "Failed to load saved plans"),
      );
    }
  },

  uploadPatientReport: async (
    file: File,
  ): Promise<PatientReportExtractionResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post<PatientReportExtractionResponse>(
      "/api/patient-report/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        timeout: 90000,
      },
    );

    return response.data;
  },

  confirmPatientReportCorrection: async (payload: {
    source_file?: string;
    extracted_profile?: any;
    corrected_profile?: any;
    missing_fields?: string[];
    user_id?: string;
  }) => {
    const response = await apiClient.post(
      "/api/patient-report/confirm",
      payload,
    );
    return response.data;
  },
};

// Auth API
export const authAPI = {
  register: async (
    username: string,
    email: string,
    password: string,
  ): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>("/api/auth/register", {
      username,
      email,
      password,
    });
    if (response.data.access_token) {
      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }
    return response.data;
  },

  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>("/api/auth/login", {
      email,
      password,
    });
    if (response.data.access_token) {
      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: () => {
    clearAuthStorage();
  },

  getCurrentUser: (): any | null => {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated: (): boolean => {
    const token = localStorage.getItem("token");
    if (!isLikelyJwt(token)) {
      if (token) clearAuthStorage();
      return false;
    }

    const payload = decodeJwtPayload(token);
    if (!payload) {
      clearAuthStorage();
      return false;
    }

    if (typeof payload.exp === "number" && Date.now() >= payload.exp * 1000) {
      clearAuthStorage();
      return false;
    }

    return true;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await apiClient.get("/api/health");
  return response.data;
};

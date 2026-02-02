import axios from "axios";
import {
  UserProfile,
  ApiResponse,
  AuthResponse,
  SavedPlan,
} from "../types/insurance";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5001";

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
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Insurance API
export const insuranceAPI = {
  getRecommendations: async (
    userProfile: UserProfile,
    limit: number = 8,
  ): Promise<ApiResponse> => {
    try {
      const response = await apiClient.post<ApiResponse>(
        "/api/recommendations",
        {
          ...userProfile,
          limit,
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
    const response = await apiClient.post("/api/plans/save", plan);
    return response.data;
  },

  getSavedPlans: async (): Promise<SavedPlan[]> => {
    const response = await apiClient.get<{
      success: boolean;
      saved_plans: SavedPlan[];
    }>("/api/plans/saved");
    return response.data.saved_plans;
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
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },

  getCurrentUser: (): any | null => {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem("token");
  },
};

// Health check
export const healthCheck = async () => {
  const response = await apiClient.get("/api/health");
  return response.data;
};

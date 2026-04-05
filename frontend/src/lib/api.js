/**
 * PathMind AI — Frontend API Service Layer
 * ==========================================
 * All API calls to FastAPI backend using axios.
 * Handles auth tokens, refresh, error handling.
 */

import axios from "axios";

// ─── Config ──────────────────────────────────────────────────────────────────
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "/api/v1").trim();

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// ─── Request Interceptor (attach JWT) ─────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response Interceptor (auto refresh on 401) ───────────────────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = localStorage.getItem("refresh_token");
        const { data } = await axios.post(`${API_BASE}/auth/refresh`, {
          refresh_token: refresh,
        });
        localStorage.setItem("access_token", data.access_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch {
        // Refresh failed — logout
        authService.logout();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// ══════════════════════════════════════════════════════════════════════════════
// AUTH SERVICE
// ══════════════════════════════════════════════════════════════════════════════
export const authService = {
  /**
   * Register new user
   */
  async signup(data) {
    const res = await api.post("/auth/signup", data);
    this._storeTokens(res.data);
    return res.data;
  },

  /**
   * Login with email + password
   */
  async login(email, password) {
    const res = await api.post("/auth/login", { email, password });
    this._storeTokens(res.data);
    return res.data;
  },

  /**
   * Store JWT tokens in localStorage
   */
  _storeTokens(data) {
    localStorage.setItem("access_token",  data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.setItem("user",          JSON.stringify(data.user));
  },

  /**
   * Clear all auth state
   */
  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  },

  /**
   * Get current user from localStorage
   */
  getUser() {
    try {
      return JSON.parse(localStorage.getItem("user") || "null");
    } catch {
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!localStorage.getItem("access_token");
  },

  /**
   * Fetch current user from API
   */
  async me() {
    const res = await api.get("/auth/me");
    return res.data;
  },

  /**
   * Forgot password
   */
  async forgotPassword(email) {
    const res = await api.post("/auth/forgot-password", { email });
    return res.data;
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// USER / PROFILE SERVICE
// ══════════════════════════════════════════════════════════════════════════════
export const userService = {
  async getProfile() {
    const res = await api.get("/user/profile");
    return res.data;
  },

  async updateProfile(data) {
    const res = await api.put("/user/profile", data);
    return res.data;
  },

  async getDashboard() {
    const res = await api.get("/user/dashboard");
    return res.data;
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// CAREER SERVICE
// ══════════════════════════════════════════════════════════════════════════════
export const careerService = {
  /**
   * Predict career paths
   * @param {Object} data - {skills, interests, education, work_style, target_salary}
   */
  async predict(data) {
    const res = await api.post("/career/predict", data);
    return res.data;
  },

  /**
   * Get prediction history
   */
  async getHistory() {
    const res = await api.get("/career/history");
    return res.data;
  },

  /**
   * Get a specific prediction
   */
  async getPrediction(id) {
    const res = await api.get(`/career/predict/${id}`);
    return res.data;
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// DECISION SERVICE
// ══════════════════════════════════════════════════════════════════════════════
export const decisionService = {
  /**
   * Analyze life decision
   * @param {Object} data - form inputs
   */
  async analyze(data) {
    const res = await api.post("/decision/analyze", data);
    return res.data;
  },

  async getHistory() {
    const res = await api.get("/decision/history");
    return res.data;
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// RESUME SERVICE
// ══════════════════════════════════════════════════════════════════════════════
export const resumeService = {
  /**
   * Upload and analyze resume (Pro only)
   * @param {File} file - PDF or DOCX file
   */
  async analyze(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.post("/resume/analyze", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`Upload: ${percent}%`);
      },
    });
    return res.data;
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// LOAN SERVICE
// ══════════════════════════════════════════════════════════════════════════════
export const loanService = {
  /**
   * Predict loan eligibility
   */
  async predict(data) {
    const res = await api.post("/loan/predict", data);
    return res.data;
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// MARKET SERVICE
// ══════════════════════════════════════════════════════════════════════════════
export const marketService = {
  async getTrends() {
    const res = await api.get("/market/trends");
    return res.data;
  },

  async getSalaryBenchmark(role) {
    const res = await api.get(`/market/salary/${encodeURIComponent(role)}`);
    return res.data;
  },
};

// SUBSCRIPTION SERVICE
// ══════════════════════════════════════════════════════════════════════════════
export const subscriptionService = {
  async getPlans() {
    const res = await api.get("/subscription/plans");
    return res.data;
  },

  /**
   * Initiate Razorpay payment flow
   */
  async createOrder(plan, billingCycle = "monthly") {
    const res = await api.post("/subscription/create-order", {
      plan,
      billing_cycle: billingCycle,
    });
    return res.data;
  },

  /**
   * Verify payment after Razorpay success
   */
  async verifyPayment(paymentData) {
    const res = await api.post("/subscription/verify-payment", paymentData);
    return res.data;
  },

  /**
   * Complete Razorpay checkout flow
   */
  async initiatePayment(plan, billingCycle = "monthly") {
    const order = await this.createOrder(plan, billingCycle);

    return new Promise((resolve, reject) => {
      const rzp = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: "PathMind AI",
        description: `${plan.charAt(0).toUpperCase() + plan.slice(1)} Plan — ${billingCycle}`,
        image: "https://pathmind.ai/logo.png",
        order_id: order.order_id,
        prefill: {
          name: authService.getUser()?.first_name || "",
          email: authService.getUser()?.email || "",
        },
        theme: { color: "#7c6fef" },
        handler: async (response) => {
          try {
            const result = await subscriptionService.verifyPayment({
              razorpay_order_id:   response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature:  response.razorpay_signature,
              plan,
              billing_cycle: billingCycle,
            });
            resolve(result);
          } catch (err) {
            reject(err);
          }
        },
        modal: { ondismiss: () => reject(new Error("Payment cancelled")) },
      });
      rzp.open();
    });
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// ERROR HANDLER UTILITY
// ══════════════════════════════════════════════════════════════════════════════
export const handleApiError = (error) => {
  if (error.response) {
    const detail = error.response.data?.detail;

    if (typeof detail === "object" && detail?.error === "quota_exceeded") {
      return {
        type: "quota",
        message: detail.message,
        upgradeUrl: detail.upgrade_url,
      };
    }
    if (typeof detail === "object" && detail?.error === "pro_required") {
      return {
        type: "pro_required",
        message: detail.message,
        upgradeUrl: detail.upgrade_url,
      };
    }
    return {
      type: "api_error",
      message: typeof detail === "string" ? detail : "An error occurred",
      status: error.response.status,
    };
  }
  if (error.request) {
    return { type: "network", message: "Network error — check your connection" };
  }
  return { type: "unknown", message: error.message || "Unknown error" };
};

export default api;

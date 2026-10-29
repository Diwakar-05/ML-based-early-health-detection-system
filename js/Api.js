// All backend calls live here. With MOCK_MODE on, fake responses are returned.

async function apiRequest(path, method = "GET", body = null) {
  if (CONFIG.MOCK_MODE) return mockResponse(path, body);

  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(CONFIG.BASE_URL + path, { method, headers, body: body ? JSON.stringify(body) : null });
  } catch (err) {
    throw new Error("Cannot reach the server. Check that the backend is running.");
  }
  const data = await res.json().catch(() => ({}));
  if (res.status === 401) { showToast("Session expired. Please log in again.", "warning"); setTimeout(logout, 1200); }
  if (!res.ok) throw new Error(data.message || `Request failed (${res.status})`);
  return data;
}

const Api = {
  register: (b) => apiRequest("/api/auth/register", "POST", b),
  login:    (b) => apiRequest("/api/auth/login", "POST", b),
  predict:  (disease, b) => apiRequest(`/api/predict/${disease}`, "POST", b), // "diabetes" | "heart"
  history:  () => apiRequest("/api/history"),
  remove:   (id) => apiRequest(`/api/history/${id}`, "DELETE"),
  metrics:  () => apiRequest("/api/model-metrics")
};

// ---------- Mock data (demo without a backend) ----------
function mockResponse(path, body) {
  return new Promise((resolve) => setTimeout(() => resolve(mockData(path, body)), 600));
}
function mockData(path, body) {
  if (path.includes("/auth/")) {
    return { token: "mock-jwt-token", user: { name: (body && body.name) || "Demo User", email: body.email } };
  }
  if (path.includes("/predict/")) {
    const p = +(Math.random() * 0.8 + 0.1).toFixed(2);
    return {
      risk_probability: p,
      risk_level: p < 0.35 ? "Low" : p < 0.65 ? "Moderate" : "High",
      prediction: p >= 0.5 ? 1 : 0,
      top_factors: [
        { feature: "Glucose", impact: 0.31 }, { feature: "BMI", impact: 0.18 },
        { feature: "Age", impact: 0.09 }, { feature: "Physical activity", impact: -0.12 }
      ],
      recommendations: ["Book a routine blood test", "Walk 30 minutes a day", "Reduce sugary drinks"]
    };
  }
  if (path.includes("/history")) return [];
  return {};
}
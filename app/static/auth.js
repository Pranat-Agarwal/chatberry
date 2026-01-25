// ---------- AUTH (JWT BASED) ----------

// Check if user is logged in (JWT exists)
function isLoggedIn() {
  return !!localStorage.getItem("access_token");
}

// Redirect to login page if not logged in
function requireLogin() {
  if (!isLoggedIn()) {
    window.location.href = "/static/login.html";
  }
}

// Logout user
function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("username");
  window.location.href = "/static/login.html";
}

// Get auth header for API calls
function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  return token
    ? { Authorization: `Bearer ${token}` }
    : {};
}

// ---------- HISTORY (BACKEND ONLY) ----------
// ❌ Local history is NOT used anymore
// ❌ saveToHistory() REMOVED
// ❌ getHistory() REMOVED

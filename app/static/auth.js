// ---------- AUTH ----------
function isLoggedIn() {
  return !!localStorage.getItem("chatberry_user");
}

function requireLogin() {
  if (!isLoggedIn()) {
    window.location.href = "/static/login.html";
  }
}

function logout() {
  localStorage.removeItem("chatberry_user");
  window.location.href = "/static/login.html";
}

// ---------- HISTORY ----------
function saveToHistory(userMsg, aiMsg) {
  const history = JSON.parse(localStorage.getItem("chatberry_history") || "[]");
  history.push({
    time: new Date().toISOString(),
    user: userMsg,
    ai: aiMsg
  });
  localStorage.setItem("chatberry_history", JSON.stringify(history));
}

function getHistory() {
  return JSON.parse(localStorage.getItem("chatberry_history") || "[]");
}

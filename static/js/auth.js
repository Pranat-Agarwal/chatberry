// ==========================
// 🔵 INIT GOOGLE
// ==========================
function initGoogle() {
    if (!window.google) return;

    google.accounts.id.initialize({
        client_id: "YOUR_CLIENT_ID",
        callback: handleCredentialResponse,
        auto_select: false
    });
}

// ==========================
// 🔵 HANDLE RESPONSE
// ==========================
async function handleCredentialResponse(response) {
    try {
        const decoded = JSON.parse(atob(response.credential.split('.')[1]));

        const res = await fetch("/auth/google", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: response.credential })
        });

        const data = await res.json();

        if (data.token) {
            localStorage.setItem("token", data.token);
            localStorage.setItem("user_name", data.user?.name || decoded.name);
            localStorage.setItem("user_pic", decoded.picture || "");

            updateUserUI();
            showChat();
            loadHistory();
        }

    } catch (err) {
        console.error(err);
    }
}

// ==========================
// 🚪 LOGOUT
// ==========================
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_pic");

    google.accounts.id.disableAutoSelect();

    resetChat();

    updateUserUI();
    showAuth();
}

// ==========================
// 🔄 SWITCH ACCOUNT
// ==========================
function switchAccount() {
    logout();

    // force account selection
    google.accounts.id.prompt();
}

// ==========================
// HELPERS
// ==========================
function resetChat() {
    session_id = null;

    const chatBox = document.getElementById("chat-box");
    if (chatBox) chatBox.innerHTML = "";

    const historyDiv = document.getElementById("history");
    if (historyDiv) historyDiv.innerHTML = "";
}

function handleLoginClick() {
    const token = localStorage.getItem("token");

    if (token) {
        toggleDropdown(event);
        return;
    }

    if (!window.google) {
        alert("Google not loaded");
        return;
    }

    // Trigger login popup (user action → allowed)
    google.accounts.id.prompt();
}

function showChat() {
}

function showAuth() {
}
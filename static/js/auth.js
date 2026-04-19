// ==========================
// 🔵 INIT GOOGLE
// ==========================
function initGoogle() {
    if (!window.google) return;

    google.accounts.id.initialize({
        client_id: "950880637924-2pgj63ev1hgb635s1imnjjvon9tto8n0.apps.googleusercontent.com",
        callback: handleCredentialResponse,
        auto_select: true
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
            setTimeout(() => {
                loadHistory();
            }, 500);
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

    google.accounts.id.prompt((n) => {
        if (n.isSkippedMoment()) {
            console.log("Retry login");
        }
    });
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
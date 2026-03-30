// ==========================
// 🔵 GOOGLE LOGIN INIT
// ==========================
// ==========================
// 🔵 INIT GOOGLE
// ==========================
function initGoogle() {
    if (!window.google) {
        console.error("Google SDK not loaded");
        return;
    }

    google.accounts.id.initialize({
        client_id: "950880637924-2pgj63ev1hgb635s1imnjjvon9tto8n0.apps.googleusercontent.com",
        callback: handleCredentialResponse
    });
}

// ==========================
// 🔵 HANDLE LOGIN CLICK
// ==========================
function handleUserClick() {
    const token = localStorage.getItem("token");

    if (!window.google) {
        alert("Google not loaded yet, refresh once");
        return;
    }

    if (!token) {
        google.accounts.id.prompt();
    } else {
        google.accounts.id.prompt(); // switch account
    }
}

// ==========================
// 🔵 HANDLE RESPONSE
// ==========================
async function handleCredentialResponse(response) {
    try {
        // 🔥 Decode Google token (fallback safety)
        const base64Url = response.credential.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const decoded = JSON.parse(atob(base64));

        console.log("Google Data:", decoded);

        const googleName = decoded.name;

        const res = await fetch("/auth/google", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                token: response.credential
            })
        });

        const data = await res.json();

        console.log("Backend Data:", data);

        if (data.token) {
            localStorage.setItem("token", data.token);

            // ✅ FIX: always ensure name is set
            let name = null;

            if (data.user && data.user.name) {
                name = data.user.name;
            } else if (googleName) {
                name = googleName;
            }

            if (name) {
                localStorage.setItem("user_name", name);
            }

            updateUserUI();

            // 🔥 force UI refresh
            setTimeout(updateUserUI, 100);

        } else {
            alert("Login failed");
        }

    } catch (err) {
        console.error("Login Error:", err);
    }
}
// ==========================
// 🔵 GOOGLE LOGIN BUTTON
// ==========================
function googleLogin() {
    if (!window.google) {
        alert("Google not loaded");
        return;
    }

    google.accounts.id.prompt();
}


// ==========================
// 👤 CONTINUE AS GUEST
// ==========================
function continueGuest() {
    localStorage.removeItem("token");
    localStorage.removeItem("user_name");

    showChat();

    if (typeof updateUserUI === "function") {
        updateUserUI();
    }
}


// ==========================
// 🧠 UI SWITCH FUNCTIONS
// ==========================
function showChat() {
    const auth = document.getElementById("auth-section");
    const chat = document.getElementById("chat-section");

    if (auth) auth.style.display = "none";
    if (chat) chat.style.display = "block";

    if (typeof loadHistory === "function") {
        loadHistory();
    }
}

function showAuth() {
    const auth = document.getElementById("auth-section");
    const chat = document.getElementById("chat-section");

    if (auth) auth.style.display = "block";
    if (chat) chat.style.display = "none";
}

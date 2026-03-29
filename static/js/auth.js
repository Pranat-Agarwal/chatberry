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

        if (data.token) {
            localStorage.setItem("token", data.token);

            if (data.user && data.user.name) {
                localStorage.setItem("user_name", data.user.name);
            }

            updateUserUI(); // 🔥 update name
        } else {
            alert("Login failed");
        }

    } catch (err) {
        console.error(err);
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

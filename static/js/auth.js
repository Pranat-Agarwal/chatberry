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
// 🔵 HANDLE LOGIN CLICK
// ==========================
function handleUserClick() {
    const token = localStorage.getItem("token");

    if (!window.google) {
        alert("Google not loaded");
        return;
    }

    if (!token) {
        google.accounts.id.prompt();
    } else {
        logoutAndSwitch();
    }
}

// ==========================
// 🔄 LOGOUT + SWITCH
// ==========================
function logoutAndSwitch() {
    localStorage.removeItem("token");
    localStorage.removeItem("user_name");

    google.accounts.id.disableAutoSelect();

    session_id = null;

    const chatBox = document.getElementById("chat-box");
    if (chatBox) chatBox.innerHTML = "";

    updateUserUI();
    showAuth();   // ✅ IMPORTANT


    setTimeout(() => {
        google.accounts.id.prompt();
    }, 300);
}

// ==========================
// 🚪 LOGOUT ONLY
// ==========================
function logoutOnly() {
    localStorage.removeItem("token");
    localStorage.removeItem("user_name");

    google.accounts.id.disableAutoSelect();

    updateUserUI();
    showAuth();
}

// ==========================
// 🔵 HANDLE RESPONSE
// ==========================
async function handleCredentialResponse(response) {
    try {
        const decoded = JSON.parse(atob(response.credential.split('.')[1]));
        const googleName = decoded.name;

        const res = await fetch("/auth/google", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: response.credential })
        });

        const data = await res.json();

        if (data.token) {
            localStorage.setItem("token", data.token);

            const name = data.user?.name || googleName;

            if (name) {
                localStorage.setItem("user_name", name);
            }

            updateUserUI();
        }

    } catch (err) {
        console.error(err);
    }
}

function showChat() {
    const auth = document.getElementById("auth-section");
    const chat = document.getElementById("chat-section");

    if (auth) auth.style.display = "none";
    if (chat) chat.style.display = "block";
}

function showAuth() {
    const auth = document.getElementById("auth-section");
    const chat = document.getElementById("chat-section");

    if (auth) auth.style.display = "block";
    if (chat) chat.style.display = "none";
}
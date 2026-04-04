// ==========================
// 🔵 INIT GOOGLE
// ==========================
function initGoogle() {
    if (!window.google) return;

    google.accounts.id.initialize({
        client_id: "YOUR_CLIENT_ID",
        callback: handleCredentialResponse
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

    google.accounts.id.revoke("", () => {
        console.log("Revoked");
    });

    updateUserUI();

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
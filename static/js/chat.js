// ==========================
// 🧠 AUTO LOGIN + USER UI
// ==========================
window.onload = function () {
    const token = localStorage.getItem("token");

    if (token) {
        showChat();
        loadHistory();
    } else {
        showAuth();
    }

    updateUserUI();
    setTimeout(initGoogle, 500);
};

let session_id = null;

function getToken() {
    return localStorage.getItem("token");
}

const chatBox = document.getElementById("chat-box");
const historyDiv = document.getElementById("history");

// ==========================
// 👤 USER UI UPDATE
// ==========================
function updateUserUI() {
    const userBtn = document.getElementById("user-info");
    const googleBtn = document.getElementById("google-btn");

    const token = localStorage.getItem("token");
    const name = localStorage.getItem("user_name");

    if (token && name) {
        userBtn.innerText = name;
        if (googleBtn) googleBtn.style.display = "none";
    } else {
        userBtn.innerText = "Login";
        if (googleBtn) googleBtn.style.display = "block";
    }
}

// ==========================
// 🔊 Speaker
// ==========================
let isSpeakerOn = false;
let currentAudio = null;

let searchMode = "normal";

function toggleSpeaker() {
    isSpeakerOn = !isSpeakerOn;

    const btn = document.getElementById("speaker-btn");

    if (isSpeakerOn) {
        btn.innerText = "🔊";
    } else {
        btn.innerText = "🔇";

        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
    }
}

// ==========================
// 🔊 AUTO SPEAK
// ==========================
async function autoSpeak(text) {
    if (!isSpeakerOn) return;

    const res = await fetch("/speech/tts", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + getToken()
        },
        body: JSON.stringify({ text })
    });

    const data = await res.json();

    if (!data.audio_url) return;

    if (currentAudio) currentAudio.pause();

    currentAudio = new Audio(data.audio_url);
    currentAudio.play();
}

// ==========================
// LOAD HISTORY
// ==========================
async function loadHistory() {
    const token = getToken();
    if (!token) return;

    const res = await fetch("/chat/history", {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const data = await res.json();

    historyDiv.innerHTML = "";

    data.chats.forEach(chat => {
        if (!chat.session_id) return;

        const div = document.createElement("div");
        div.className = "history-item";
        div.innerText = chat.title || "New Chat";

        div.onclick = () => loadChat(chat.session_id);

        historyDiv.appendChild(div);
    });
}

// ==========================
async function loadChat(id) {
    if (!id || id === "null") return;

    session_id = id;

    const res = await fetch(`/chat/${id}`, {
        headers: {
            "Authorization": "Bearer " + getToken()
        }
    });

    const data = await res.json();

    chatBox.innerHTML = "";

    data.messages.forEach(msg => {
        addMessage(msg.content, msg.role === "user" ? "user" : "bot");
    });
}

// ==========================
function newChat() {
    session_id = null;
    chatBox.innerHTML = "";
}

// ==========================
async function deleteAll() {
    await fetch("/chat/delete-all", {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + getToken()
        }
    });

    newChat();
    loadHistory();
}

async function deleteLast() {
    await fetch("/chat/delete-last", {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + getToken()
        }
    });

    newChat();
    loadHistory();
}

// ==========================
function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = `message ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerText = text;

    div.appendChild(bubble);
    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;
}

// ==========================
function setMode(mode) {
    searchMode = mode;

    document.getElementById("normal-btn").classList.remove("active");
    document.getElementById("deep-btn").classList.remove("active");

    document.getElementById(mode === "normal" ? "normal-btn" : "deep-btn")
        .classList.add("active");
}

// ==========================
async function sendMessage() {
    const input = document.getElementById("message");
    const message = input.value;

    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    try {
        const res = await fetch("/chat/send", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + getToken()
            },
            body: JSON.stringify({
                message,
                session_id,
                mode: searchMode
            })
        });

        const data = await res.json();

        session_id = data.session_id;

        addMessage(data.reply, "bot");

        autoSpeak(data.reply);

        loadHistory();

    } catch (err) {
        console.error(err);
        addMessage("❌ Server error", "bot");
    }
}

// ==========================
// FILE UPLOAD
// ==========================
document.getElementById("fileInput").addEventListener("change", async function () {
    const file = this.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/file/upload", {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + getToken()
        },
        body: formData
    });

    const data = await res.json();

    if (data.content) {
        document.getElementById("message").value = data.content;
    }
});

// ==========================
// DROPDOWN
// ==========================
function toggleDropdown(e) {
    e.stopPropagation();
    document.getElementById("dropdown").classList.toggle("hidden");
}

document.addEventListener("click", function () {
    document.getElementById("dropdown").classList.add("hidden");
});
// ==========================
// 🧠 AUTO LOGIN + USER UI
// ==========================
window.onload = function () {
    const token = localStorage.getItem("token");

    updateUserUI();

    setTimeout(() => {
        loadHistory();
    }, 500);
    setTimeout(initGoogle, 500);
};

// ==========================
// GLOBAL STATE
// ==========================
let session_id = null;
let searchMode = "normal";

let isSideChat = false;
let activePanel = 1;

let tempChats = { 1: [], 2: [] };

// ==========================
// TOKEN
// ==========================
function getToken() {
    return localStorage.getItem("token");
}

// ==========================
// USER UI
// ==========================
function updateUserUI() {
    const userBtn = document.getElementById("user-info");

    const token = localStorage.getItem("token");
    const name = localStorage.getItem("user_name");

    userBtn.innerText = token && name ? name : "Login";
}

// ==========================
// SIDE CHAT TOGGLE
// ==========================
function toggleSideChat() {
    activePanel = 1;
    const container = document.getElementById("chat-container");
    const main = document.getElementById("main-chat");

    if (!isSideChat) {
        isSideChat = true;

        container.classList.remove("hidden");
        main.classList.add("hidden");

        copyMainToPanels();
    } else {
        handleCloseSideChat();
    }
}

// ==========================
// COPY MAIN → SIDE
// ==========================
function copyMainToPanels() {
    const mainHTML = document.getElementById("main-chat").innerHTML;

    document.getElementById("chat-box-1").innerHTML = mainHTML;
    document.getElementById("chat-box-2").innerHTML = mainHTML;

    tempChats = { 1: [], 2: [] };
}

// ==========================
// ACTIVE PANEL
// ==========================
document.getElementById("panel-1").addEventListener("click", () => {
    activePanel = 1;
    console.log("Switched to Panel 1");
});

document.getElementById("panel-2").addEventListener("click", () => {
    activePanel = 2;
    console.log("Switched to Panel 2");
});

// ==========================
// ADD MESSAGE
// ==========================
function addMessage(text, sender) {
    let box;

    if (isSideChat) {
        if (activePanel === 1) {
            box = document.getElementById("chat-box-1");
        } else if (activePanel === 2) {
            box = document.getElementById("chat-box-2");
        } else {
            box = document.getElementById("chat-box-1");
        }
    } else {
        box = document.getElementById("main-chat");
    }

    if (!box) return;

    const div = document.createElement("div");
    div.className = `message ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerText = text;

    div.appendChild(bubble);
    box.appendChild(div);

    box.scrollTop = box.scrollHeight;

    if (isSideChat) {
        tempChats[activePanel].push({ role: sender, content: text });
    }
}

// ==========================
// SEND MESSAGE
// ==========================
async function sendMessage() {
    const input = document.getElementById("message");
    const message = input.value;

    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    // SIDE CHAT → TEMP ONLY
    if (isSideChat) {
        try {
            const res = await fetch("/chat/send", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + getToken()
                },
                body: JSON.stringify({
                    message,
                    session_id: null,   // 🔥 IMPORTANT → don't use real session
                    mode: searchMode
                })
            });

            const data = await res.json();

            addMessage(data.reply, "bot");  // ✅ show real result

        } catch (err) {
            console.error(err);
            addMessage("❌ Error", "bot");
        }

        return;
    }

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
// LOAD HISTORY
// ==========================
async function loadHistory() {
    const token = getToken();

    const headers = token
        ? { "Authorization": "Bearer " + token }
        : {};

    const res = await fetch("/chat/history", { headers });

    const data = await res.json();
    console.log("📜 HISTORY:", data); // DEBUG


    const historyDiv = document.getElementById("history");
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
// LOAD CHAT
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

    const main = document.getElementById("main-chat");
    main.innerHTML = "";

    data.messages.forEach(msg => {
        addMessage(msg.content, msg.role === "user" ? "user" : "bot");
    });
}

// ==========================
// NEW CHAT
// ==========================
function newChat() {
    if (isSideChat) handleCloseSideChat();

    session_id = null;
    document.getElementById("main-chat").innerHTML = "";
}

// ==========================
// DELETE
// ==========================
async function deleteAll() {
    if (isSideChat) handleCloseSideChat();

    await fetch("/chat/delete-all", {
        method: "DELETE",
        headers: { "Authorization": "Bearer " + getToken() }
    });

    newChat();
    loadHistory();
}

async function deleteLast() {
    if (isSideChat) handleCloseSideChat();

    await fetch("/chat/delete-last", {
        method: "DELETE",
        headers: { "Authorization": "Bearer " + getToken() }
    });

    newChat();
    loadHistory();
}

// ==========================
// SAVE SIDE CHAT
// ==========================
function handleCloseSideChat() {
    const choice = prompt("Save which window? (1 or 2)");

    if (choice === "1" || choice === "2") {
        savePanelToMain(parseInt(choice));
    }

    resetSideChatUI();
}

function savePanelToMain(panel) {
    const main = document.getElementById("main-chat");

    tempChats[panel].forEach(msg => {
        const div = document.createElement("div");
        div.className = `message ${msg.role}`;

        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.innerText = msg.content;

        div.appendChild(bubble);
        main.appendChild(div);
    });
}

// ==========================
// RESET SIDE CHAT
// ==========================
function resetSideChatUI() {
    isSideChat = false;

    document.getElementById("chat-container").classList.add("hidden");
    document.getElementById("main-chat").classList.remove("hidden");

    document.getElementById("chat-box-1").innerHTML = "";
    document.getElementById("chat-box-2").innerHTML = "";

    tempChats = { 1: [], 2: [] };
}

// ==========================
// CLOSE ON OUTSIDE CLICK
// ==========================
document.addEventListener("click", function (e) {
    if (!isSideChat) return;

    const shouldClose =
        e.target.closest("#normal-btn") ||         // Normal / Deep / Side Chat
        e.target.closest("#deep-btn") ||
        e.target.closest(".new-chat-btn") ||     // New Chat
        e.target.closest(".danger-btn") ||       // Delete buttons
        e.target.closest(".history-item") ||     // Sidebar chats
        e.target.closest("#user-info") ||        // Login click
        e.target.closest(".dropdown div");       // Logout / Switch

    if (shouldClose) {
        handleCloseSideChat();
    }
});

// ==========================
// MODE SWITCH
// ==========================
function setMode(mode) {
    if (isSideChat) handleCloseSideChat();

    searchMode = mode;

    document.getElementById("normal-btn").classList.remove("active");
    document.getElementById("deep-btn").classList.remove("active");

    document.getElementById(mode === "normal" ? "normal-btn" : "deep-btn")
        .classList.add("active");
}

// ==========================
// SPEAKER
// ==========================
let isSpeakerOn = false;
let currentAudio = null;

function toggleSpeaker() {
    isSpeakerOn = !isSpeakerOn;

    const btn = document.getElementById("speaker-btn");

    btn.innerText = isSpeakerOn ? "🔊" : "🔇";

    if (!isSpeakerOn && currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
}

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
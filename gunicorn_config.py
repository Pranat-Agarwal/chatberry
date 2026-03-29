import multiprocessing
import os


# ==========================
# 🔌 SERVER BIND
# ==========================
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"


# ==========================
# ⚙️ WORKERS
# ==========================
# Recommended: (2 x CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1


# ==========================
# 🧵 THREADS
# ==========================
threads = 2


# ==========================
# ⏱ TIMEOUTS
# ==========================
timeout = 120
keepalive = 5


# ==========================
# 📄 LOGGING
# ==========================
loglevel = "info"
accesslog = "-"   # stdout (Render logs)
errorlog = "-"    # stderr


# ==========================
# 🔁 AUTO RESTART (DEV ONLY)
# ==========================
reload = False


# ==========================
# 🧠 PRELOAD APP
# ==========================
preload_app = True


# ==========================
# 🛡 MAX REQUESTS (ANTI MEMORY LEAK)
# ==========================
max_requests = 1000
max_requests_jitter = 100


# ==========================
# 📦 WORKER CLASS
# ==========================
worker_class = "sync"
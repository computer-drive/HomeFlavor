import os

# Config Path
DEFAULT_CONFIG_PATH = os.path.join("config", "default.json")
PRODUCTION_CONFIG_PATH = os.path.join("config", "production.json")
INSTANCE_CONFIG_PATH = os.path.join("user", "config.json")

# File
DEFAULT_ENCODING = "utf-8"

# Log
LOG_PATH = os.path.join("user", "logs")

# CrashReport
CRASH_REPORT_PATH = os.path.join("user", "crash_report")

UNLOGIN_WHITELIST = [
    "/login",
    "/api/auth/login",
    "/static/"
]
import os
from dotenv import load_dotenv

load_dotenv()


def parse_bool(value: str | None) -> bool:
    if str(value).lower() in ("true", "1", "yes", "on"):
        return True
    return False

# ==========================================
# 1. APPLICATION CONFIG
# ==========================================
APP_NAME = os.getenv("APP_NAME", "FastAPI Service")
APP_ENV = os.getenv("APP_ENV", "development")  # dev | staging | prod
VERSION = os.getenv("VERSION", "1.0.0")
DEBUG = parse_bool(os.getenv("DEBUG", "false"))

# ==========================================
# 2. SERVER CONFIG
# ==========================================
try:
    PORT = int(os.getenv("PORT", 8001))
except ValueError:
    PORT = 8001
HOST = os.getenv("HOST", "127.0.0.1")
DESTINATION_DOMAIN = os.getenv("DESTINATION_DOMAIN")

# ==========================================
# 3. LOGGING
# ==========================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ==========================================
# 4. VALIDATION SAFETY (MIDDLEWARE STYLE)
# ==========================================
if not DESTINATION_DOMAIN:
    raise ValueError("🚨 FATAL ERROR: DESTINATION_DOMAIN is not set in the environment variables.")

if APP_ENV == "production" and DEBUG is True:
    print("⚠️  WARNING: APP_ENV is production but DEBUG is still enabled. This is a security risk.")
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Configuration comes from the project root, then backend-specific overrides.
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")

DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(DATA_DIR / "uploads")))
DB_FILE = os.getenv("DB_FILE", str(DATA_DIR / "family.db"))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")

SECRET_KEY = os.getenv("SECRET_KEY", "family-tree-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

SITE_TITLE = os.getenv("SITE_TITLE", "Our Family Tree")

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))
THUMB_SIZE = int(os.getenv("THUMB_SIZE", "500"))

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

# When the built interface is present, the backend serves it directly. This is what
# lets a local run be a single process on a single port, with no nginx and no Docker.
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", str(PROJECT_ROOT / "frontend" / "dist")))

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

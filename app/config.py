"""Application configuration for ByteNova Technologies recruitment portal."""
import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    """Core Flask configuration settings."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "bytenova-dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'bytenova.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Resume upload settings — PDF only, max 5 MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads", "resumes")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf"}

    # Email settings (mock by default; swap SMTP values for production)
    MAIL_ENABLED = os.environ.get("MAIL_ENABLED", "false").lower() == "true"
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "careers@bytenova.in")

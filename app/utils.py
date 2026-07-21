"""Shared utility helpers for ByteNova."""
import os
import uuid

from flask import current_app
from flask_login import current_user
from werkzeug.utils import secure_filename


def allowed_file(filename: str) -> bool:
    """Return True if the file extension is an allowed resume type (PDF)."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_resume(file_storage) -> str:
    """
    Persist an uploaded resume to disk with a unique filename.
    Returns the stored filename (not full path).
    """
    original = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{original}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file_storage.save(os.path.join(upload_dir, unique_name))
    return unique_name


def resume_path(filename: str) -> str:
    """Build absolute filesystem path for a stored resume."""
    return os.path.join(current_app.config["UPLOAD_FOLDER"], filename)


def role_required(*roles):
    """Decorator factory — restrict route access to specific user roles."""

    def decorator(view_func):
        from functools import wraps

        from flask import abort

        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator

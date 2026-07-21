"""Database models for the ByteNova recruitment platform and company website."""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


def _utcnow():
    """Return current UTC timestamp (timezone-aware)."""
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """Unified user account supporting candidates, recruiters, and admins."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="candidate")  # candidate | recruiter | admin
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=_utcnow)

    # Relationships
    applications = db.relationship("Application", backref="candidate", lazy="dynamic")
    posted_jobs = db.relationship("Job", backref="recruiter", lazy="dynamic")

    def set_password(self, password: str) -> None:
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_recruiter(self) -> bool:
        return self.role == "recruiter"

    @property
    def is_candidate(self) -> bool:
        return self.role == "candidate"


class Job(db.Model):
    """Open role published by a recruiter."""

    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(30), nullable=False)  # Full-time, Remote, etc.
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    salary_range = db.Column(db.String(60))
    is_active = db.Column(db.Boolean, default=True)
    posted_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    applications = db.relationship("Application", backref="job", lazy="dynamic")

    @property
    def application_count(self) -> int:
        return self.applications.count()


class Application(db.Model):
    """Candidate application for a specific job opening."""

    __tablename__ = "applications"

    # Valid status workflow: submitted -> under_review -> interview -> offered -> rejected
    STATUS_CHOICES = [
        "submitted",
        "under_review",
        "interview",
        "offered",
        "rejected",
    ]

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    resume_filename = db.Column(db.String(255), nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(30), default="submitted")
    applied_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    __table_args__ = (
        db.UniqueConstraint("candidate_id", "job_id", name="unique_candidate_job"),
    )

    @property
    def status_label(self) -> str:
        """Human-readable status for display in templates."""
        labels = {
            "submitted": "Submitted",
            "under_review": "Under Review",
            "interview": "Interview Scheduled",
            "offered": "Offer Extended",
            "rejected": "Not Selected",
        }
        return labels.get(self.status, self.status.title())


class ContactMessage(db.Model):
    """Contact form submissions from the company website."""

    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=_utcnow)


class NewsletterSubscriber(db.Model):
    """Newsletter email subscribers."""

    __tablename__ = "newsletter_subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    subscribed_at = db.Column(db.DateTime, default=_utcnow)

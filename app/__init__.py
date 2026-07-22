"""ByteNova Technologies Flask application factory."""
import os
from datetime import datetime, timezone

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_class=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    if config_class is None:
        from app.config import Config

        config_class = Config

    app.config.from_object(config_class)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.candidate import candidate_bp
    from app.routes.jobs import jobs_bp
    from app.routes.main import main_bp
    from app.routes.recruiter import recruiter_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(candidate_bp, url_prefix="/candidate")
    app.register_blueprint(recruiter_bp, url_prefix="/recruiter")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/404.html", error="500", message="Internal server error. Please try again later."), 500

    @app.context_processor
    def inject_globals():
        return {"company_name": "ByteNova Technologies"}

    with app.app_context():
        db.create_all()
        _seed_default_users(app)

    return app


def _seed_default_users(app):
    """Create safe demo records when they are not already present."""
    from app.models import Application, Job, User

    admin = User.query.filter_by(email="admin@bytenova.tech").first()
    if not admin:
        admin = User(
            email="admin@bytenova.tech",
            full_name="System Administrator",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)

    recruiter = User.query.filter_by(email="recruiter@bytenova.tech").first()
    if not recruiter:
        recruiter = User(
            email="recruiter@bytenova.tech",
            full_name="Aditi Sharma",
            role="recruiter",
            phone="+91 98765 43210",
        )
        recruiter.set_password("recruiter123")
        db.session.add(recruiter)

    candidate = User.query.filter_by(email="riyansh@bytenova.in").first()
    if not candidate:
        candidate = User(
            email="riyansh@bytenova.in",
            full_name="Riyansh",
            role="candidate",
            phone="+91 98765 1047",
        )
        candidate.set_password("candidate123")
        db.session.add(candidate)

    db.session.commit()

    if Job.query.count() == 0:
        sample_jobs = [
            Job(
                title="Python Developer Intern",
                department="Software Development",
                location="Indore, Madhya Pradesh (On-site)",
                job_type="Internship",
                description=(
                    "Learn Python development by contributing to APIs, automation, and "
                    "client-focused software projects with our Indore engineering team."
                ),
                requirements=(
                    "Working knowledge of Python fundamentals\n"
                    "Basic understanding of Flask, Django, or REST APIs\n"
                    "Interest in problem-solving and clean code\n"
                    "Available to work from our Indore office"
                ),
                salary_range="\u20b915,000 \u2013 \u20b920,000 per month",
                posted_by=recruiter.id,
            ),
            Job(
                title="AI Automation Engineer",
                department="Software Development",
                location="Bengaluru, Karnataka (Hybrid)",
                job_type="Full-time",
                description=(
                    "Design practical AI automation workflows using Python, APIs, and LLM "
                    "tools to solve everyday client problems."
                ),
                requirements=(
                    "2+ years of Python or automation engineering experience\n"
                    "Experience with APIs, webhooks, and workflow tools\n"
                    "Familiarity with LLM prompts or AI integrations\n"
                    "Thoughtful approach to testing and client data privacy"
                ),
                salary_range="\u20b96 LPA \u2013 \u20b910 LPA",
                posted_by=recruiter.id,
            ),
            Job(
                title="Web Developer",
                department="Software Development",
                location="Mumbai, Maharashtra (Hybrid)",
                job_type="Full-time",
                description=(
                    "Build fast, responsive web applications for founders and small business "
                    "teams, working closely with designers and Python developers."
                ),
                requirements=(
                    "2+ years of frontend or full-stack web development experience\n"
                    "Strong JavaScript, React, and modern HTML/CSS skills\n"
                    "Experience integrating REST APIs\n"
                    "Comfort turning Figma designs into polished interfaces"
                ),
                salary_range="\u20b94.5 LPA \u2013 \u20b97 LPA",
                posted_by=recruiter.id,
            ),
            Job(
                title="Business Development Intern",
                department="Business Development",
                location="Indore, Madhya Pradesh (On-site)",
                job_type="Internship",
                description=(
                    "Help us connect with local startups and small businesses through research, "
                    "outreach, and simple content that explains ByteNova's services."
                ),
                requirements=(
                    "Currently pursuing a business, marketing, or communications degree\n"
                    "Clear written and spoken English and Hindi\n"
                    "Comfort with LinkedIn, research, and outreach\n"
                    "Eager to learn in a client-focused startup environment"
                ),
                salary_range="\u20b912,000 \u2013 \u20b918,000 per month",
                posted_by=recruiter.id,
            ),
        ]
        db.session.add_all(sample_jobs)
        db.session.commit()

    first_job = Job.query.first()
    if first_job and not Application.query.filter_by(
        candidate_id=candidate.id, job_id=first_job.id
    ).first():
        application = Application(
            candidate_id=candidate.id,
            job_id=first_job.id,
            resume_filename="riyansh_python_resume.pdf",
            cover_letter=(
                "I am excited to begin my software development career with ByteNova "
                "Technologies and contribute to Python and AI automation projects."
            ),
            status="interview",
            applied_at=datetime(2026, 5, 16, 10, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 7, 21, 10, 0, tzinfo=timezone.utc),
        )
        db.session.add(application)
        db.session.commit()

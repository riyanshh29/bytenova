"""Public job listing and application routes."""
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app import db
from app.models import Application, Job
from app.services.email_service import notify_application_received
from app.utils import allowed_file, save_resume

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/")
def list_jobs():
    """Browse all active job openings with optional filters."""
    query = Job.query.filter_by(is_active=True)

    department = request.args.get("department", "").strip()
    job_type = request.args.get("job_type", "").strip()
    search = request.args.get("q", "").strip()

    if department:
        query = query.filter(Job.department == department)
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if search:
        query = query.filter(
            Job.title.ilike(f"%{search}%") | Job.description.ilike(f"%{search}%")
        )

    jobs = query.order_by(Job.created_at.desc()).all()
    departments = (
        db.session.query(Job.department)
        .filter(Job.is_active.is_(True))
        .distinct()
        .all()
    )
    job_types = (
        db.session.query(Job.job_type)
        .filter(Job.is_active.is_(True))
        .distinct()
        .all()
    )

    return render_template(
        "jobs/list.html",
        jobs=jobs,
        departments=[d[0] for d in departments],
        job_types=[t[0] for t in job_types],
        filters={"department": department, "job_type": job_type, "q": search},
    )


@jobs_bp.route("/<int:job_id>")
def job_detail(job_id):
    """Single job detail page."""
    job = db.session.get(Job, job_id)
    if not job or not job.is_active:
        abort(404)

    already_applied = False
    if current_user.is_authenticated and current_user.is_candidate:
        already_applied = (
            Application.query.filter_by(
                candidate_id=current_user.id, job_id=job.id
            ).first()
            is not None
        )

    return render_template(
        "jobs/detail.html", job=job, already_applied=already_applied
    )


@jobs_bp.route("/<int:job_id>/apply", methods=["GET", "POST"])
@login_required
def apply(job_id):
    """Submit an application with PDF resume upload."""
    job = db.session.get(Job, job_id)
    if not job or not job.is_active:
        abort(404)

    if not current_user.is_candidate:
        flash("Only candidates can apply for jobs.", "warning")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    existing = Application.query.filter_by(
        candidate_id=current_user.id, job_id=job.id
    ).first()
    if existing:
        flash("You have already applied for this position.", "info")
        return redirect(url_for("candidate.application_detail", app_id=existing.id))

    if request.method == "POST":
        cover_letter = request.form.get("cover_letter", "").strip()
        resume = request.files.get("resume")

        if not resume or resume.filename == "":
            flash("Please upload your resume (PDF only).", "danger")
            return render_template("jobs/apply.html", job=job)

        if not allowed_file(resume.filename):
            flash("Only PDF files are accepted for resume uploads.", "danger")
            return render_template("jobs/apply.html", job=job)

        filename = save_resume(resume)
        application = Application(
            candidate_id=current_user.id,
            job_id=job.id,
            resume_filename=filename,
            cover_letter=cover_letter,
        )
        db.session.add(application)
        db.session.commit()

        notify_application_received(
            current_user.email, current_user.full_name, job.title
        )

        flash("Application submitted successfully!", "success")
        return redirect(url_for("candidate.application_detail", app_id=application.id))

    return render_template("jobs/apply.html", job=job)

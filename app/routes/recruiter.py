"""Recruiter portal — job management and applicant review."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Application, Job
from app.services.email_service import notify_status_update
from app.utils import role_required

recruiter_bp = Blueprint("recruiter", __name__)


@recruiter_bp.route("/dashboard")
@login_required
@role_required("recruiter")
def dashboard():
    """Recruiter overview — jobs and recent applications."""
    jobs = Job.query.filter_by(posted_by=current_user.id).order_by(Job.created_at.desc()).all()
    recent_apps = (
        Application.query.join(Job)
        .filter(Job.posted_by == current_user.id)
        .order_by(Application.applied_at.desc())
        .limit(10)
        .all()
    )
    stats = {
        "total_jobs": len(jobs),
        "active_jobs": sum(1 for j in jobs if j.is_active),
        "total_applications": sum(j.application_count for j in jobs),
        "pending_review": Application.query.join(Job)
        .filter(Job.posted_by == current_user.id, Application.status == "submitted")
        .count(),
    }
    return render_template(
        "recruiter/dashboard.html", jobs=jobs, recent_apps=recent_apps, stats=stats
    )


@recruiter_bp.route("/jobs/new", methods=["GET", "POST"])
@login_required
@role_required("recruiter")
def create_job():
    """Post a new job opening."""
    if request.method == "POST":
        job = Job(
            title=request.form.get("title", "").strip(),
            department=request.form.get("department", "").strip(),
            location=request.form.get("location", "").strip(),
            job_type=request.form.get("job_type", "").strip(),
            description=request.form.get("description", "").strip(),
            requirements=request.form.get("requirements", "").strip(),
            salary_range=request.form.get("salary_range", "").strip(),
            posted_by=current_user.id,
        )
        if not all([job.title, job.department, job.location, job.description]):
            flash("Please fill in all required fields.", "danger")
            return render_template("recruiter/job_form.html", job=None)

        db.session.add(job)
        db.session.commit()
        flash(f'Job "{job.title}" posted successfully!', "success")
        return redirect(url_for("recruiter.dashboard"))

    return render_template("recruiter/job_form.html", job=None)


@recruiter_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("recruiter")
def edit_job(job_id):
    """Edit an existing job posting."""
    job = db.session.get(Job, job_id)
    if not job or job.posted_by != current_user.id:
        abort(404)

    if request.method == "POST":
        job.title = request.form.get("title", "").strip()
        job.department = request.form.get("department", "").strip()
        job.location = request.form.get("location", "").strip()
        job.job_type = request.form.get("job_type", "").strip()
        job.description = request.form.get("description", "").strip()
        job.requirements = request.form.get("requirements", "").strip()
        job.salary_range = request.form.get("salary_range", "").strip()
        job.is_active = request.form.get("is_active") == "on"
        db.session.commit()
        flash("Job updated successfully.", "success")
        return redirect(url_for("recruiter.dashboard"))

    return render_template("recruiter/job_form.html", job=job)


@recruiter_bp.route("/jobs/<int:job_id>/applications")
@login_required
@role_required("recruiter")
def job_applications(job_id):
    """View all applications for a specific job."""
    job = db.session.get(Job, job_id)
    if not job or job.posted_by != current_user.id:
        abort(404)

    applications = (
        Application.query.filter_by(job_id=job.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return render_template(
        "recruiter/applications.html", job=job, applications=applications
    )


@recruiter_bp.route("/applications/<int:app_id>", methods=["GET", "POST"])
@login_required
@role_required("recruiter")
def review_application(app_id):
    """Review a single application and update status."""
    application = db.session.get(Application, app_id)
    if not application or application.job.posted_by != current_user.id:
        abort(404)

    if request.method == "POST":
        new_status = request.form.get("status", "")
        if new_status in Application.STATUS_CHOICES:
            old_status = application.status
            application.status = new_status
            db.session.commit()

            if old_status != new_status:
                notify_status_update(
                    application.candidate.email,
                    application.candidate.full_name,
                    application.job.title,
                    new_status,
                )
            flash("Application status updated.", "success")
        else:
            flash("Invalid status selected.", "danger")
        return redirect(url_for("recruiter.review_application", app_id=app_id))

    return render_template(
        "recruiter/review_application.html",
        application=application,
        status_choices=Application.STATUS_CHOICES,
    )

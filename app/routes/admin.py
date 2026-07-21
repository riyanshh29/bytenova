"""Admin dashboard — platform-wide management."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Application, ContactMessage, Job, User
from app.utils import role_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    """Admin overview with platform statistics."""
    stats = {
        "total_users": User.query.count(),
        "candidates": User.query.filter_by(role="candidate").count(),
        "recruiters": User.query.filter_by(role="recruiter").count(),
        "total_jobs": Job.query.count(),
        "active_jobs": Job.query.filter_by(is_active=True).count(),
        "total_applications": Application.query.count(),
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_apps = Application.query.order_by(Application.applied_at.desc()).limit(5).all()
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_users=recent_users,
        recent_apps=recent_apps,
    )


@admin_bp.route("/users")
@login_required
@role_required("admin")
def users():
    """Manage all platform users."""
    role_filter = request.args.get("role", "")
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    all_users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users, role_filter=role_filter)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def toggle_user(user_id):
    """Activate or deactivate a user account."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "warning")
        return redirect(url_for("admin.users"))

    user.is_active = not user.is_active
    db.session.commit()
    state = "activated" if user.is_active else "deactivated"
    flash(f"User {user.full_name} has been {state}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/new-recruiter", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_recruiter():
    """Create a new recruiter account."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("admin/create_recruiter.html")

        recruiter = User(full_name=full_name, email=email, role="recruiter")
        recruiter.set_password(password)
        db.session.add(recruiter)
        db.session.commit()
        flash(f"Recruiter {full_name} created successfully.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/create_recruiter.html")


@admin_bp.route("/jobs")
@login_required
@role_required("admin")
def jobs():
    """View and manage all job listings."""
    all_jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template("admin/jobs.html", jobs=all_jobs)


@admin_bp.route("/jobs/<int:job_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def toggle_job(job_id):
    """Activate or deactivate a job listing."""
    job = db.session.get(Job, job_id)
    if not job:
        abort(404)
    job.is_active = not job.is_active
    db.session.commit()
    state = "activated" if job.is_active else "deactivated"
    flash(f'Job "{job.title}" has been {state}.', "success")
    return redirect(url_for("admin.jobs"))


@admin_bp.route("/applications")
@login_required
@role_required("admin")
def applications():
    """View all applications across the platform."""
    status_filter = request.args.get("status", "")
    query = Application.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_apps = query.order_by(Application.applied_at.desc()).all()
    return render_template(
        "admin/applications.html",
        applications=all_apps,
        status_filter=status_filter,
        statuses=Application.STATUS_CHOICES,
    )


@admin_bp.route("/contact-messages")
@login_required
@role_required("admin")
def contact_messages():
    """View contact form enquiries."""
    show_read = request.args.get("show_read", "0") == "1"
    query = ContactMessage.query
    if not show_read:
        query = query.filter_by(is_read=False)
    messages = query.order_by(ContactMessage.created_at.desc()).all()
    return render_template(
        "admin/contact_messages.html",
        messages=messages,
        show_read=show_read,
    )


@admin_bp.route("/contact-messages/<int:msg_id>/toggle-read", methods=["POST"])
@login_required
@role_required("admin")
def toggle_message_read(msg_id):
    """Mark a contact message as read/unread."""
    msg = db.session.get(ContactMessage, msg_id)
    if not msg:
        abort(404)
    msg.is_read = not msg.is_read
    db.session.commit()
    flash(f"Message from {msg.name} marked as {'read' if msg.is_read else 'unread'}.", "success")
    return redirect(url_for("admin.contact_messages"))

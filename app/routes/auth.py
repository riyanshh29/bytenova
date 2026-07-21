"""Authentication routes — registration and login for all roles."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


def _redirect_by_role(user):
    """Send authenticated users to their role-specific dashboard."""
    if user.is_admin:
        return redirect(url_for("admin.dashboard"))
    if user.is_recruiter:
        return redirect(url_for("recruiter.dashboard"))
    return redirect(url_for("candidate.dashboard"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Candidate self-registration (recruiters/admins are created by admin)."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Validation
        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not email or "@" not in email:
            errors.append("A valid email address is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("auth/register.html")

        user = User(full_name=full_name, email=email, phone=phone, role="candidate")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Unified login — role is determined from the user record."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.full_name}!", "success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return _redirect_by_role(user)

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """End the current session."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))

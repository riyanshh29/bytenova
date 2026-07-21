"""Candidate portal, application tracking, and interview invitation workflow."""
from io import BytesIO
from textwrap import wrap

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Application
from app.utils import role_required

candidate_bp = Blueprint("candidate", __name__)


INTERVIEW_DETAILS = {
    "application_reference": "BNT-2026-1047",
    "status": "Face-to-Face Interview Scheduled",
    "date": "25 July 2026",
    "reporting_time": "10:00 AM IST",
    "duration": "45–60 Minutes",
    "interview_type": "Face-to-Face",
    "company": "ByteNova Technologies",
    "venue_lines": [
        "ByteNova Technologies",
        "5th Floor, Crystal IT Park",
        "Vijay Nagar, Indore",
        "Madhya Pradesh – 452010",
    ],
    "reporting_hr": "Ms. Priya Sharma",
    "hr_designation": "HR Executive",
    "recruiter_email": "careers@bytenova.in",
    "recruiter_phone": "+91 731 400 1234",
    "office_hours": "Monday – Friday, 9:30 AM – 6:30 PM IST",
    "timeline": [
        ("Application Submitted", "16 May 2026", "check-circle-fill"),
        ("Resume Shortlisted", "18 May 2026", "check-circle-fill"),
        ("Online Python Assessment Cleared", "22 May 2026", "check-circle-fill"),
        ("Technical Interview Cleared", "27 May 2026", "check-circle-fill"),
        ("HR Discussion Completed", "30 May 2026", "check-circle-fill"),
        ("Final Face-to-Face Interview", "25 July 2026", "calendar-event-fill"),
    ],
}


def _interview_context(application: Application) -> dict:
    """Return presentation-only interview information without changing the schema."""
    return {
        **INTERVIEW_DETAILS,
        "candidate_name": application.candidate.full_name,
        # Per requirement: force the display values on the interview status page.
        "position": "Python Developer Intern",
        "applied_on": "16 May 2026",
        "department": application.job.department,
        "employment_type": application.job.job_type,
        "location": "Indore, Madhya Pradesh",
    }


def _pdf_escape(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _pdf_text(x: int, y: int, text: str, font: str = "F1", size: int = 10, color: str = "0 0 0") -> str:
    return (
        f"BT /{font} {size} Tf {color} rg 1 0 0 1 {x} {y} Tm "
        f"({_pdf_escape(text)}) Tj ET"
    )


def _build_call_letter_pdf(details: dict) -> bytes:
    """Build a compact, professional one-page PDF with standard PDF primitives."""
    commands = [
        "0.31 0.27 0.89 rg 48 755 499 54 re f",  # Letterhead
        "0.31 0.27 0.89 rg 48 694 499 2 re f",
        "1 1 1 rg 60 765 32 32 re f",  # ByteNova monogram logo tile
        _pdf_text(66, 774, "BN", "F2", 13, "0.31 0.27 0.89"),
        _pdf_text(106, 784, "ByteNova Technologies", "F2", 18, "1 1 1"),
        _pdf_text(106, 768, "Python Development | AI Automation | Web Development", "F1", 9, "1 1 1"),
        _pdf_text(48, 718, "INTERVIEW CALL LETTER", "F2", 16, "0.31 0.27 0.89"),
        _pdf_text(48, 700, "Application Reference: " + details["application_reference"], "F1", 10, "0.25 0.29 0.36"),
    ]

    y = 670
    letter_lines = [
        f"Dear {details['candidate_name']},",
        "",
        "Congratulations! You have successfully cleared the Resume Screening, Python Assessment,",
        "Technical Interview, and HR Discussion.",
        "",
        "We are pleased to invite you for the Final Face-to-Face Interview at our Indore office.",
    ]
    for line in letter_lines:
        commands.append(_pdf_text(48, y, line, "F1", 10, "0.16 0.2 0.28"))
        y -= 16

    y -= 4
    commands.append("0.94 0.95 1 rg 48 445 499 112 re f")
    commands.append(_pdf_text(62, 535, "Interview Details", "F2", 12, "0.31 0.27 0.89"))
    detail_lines = [
        ("Position", details["position"]),
        ("Interview Date", details["date"]),
        ("Reporting Time", details["reporting_time"]),
        ("Duration", details["duration"]),
        ("Reporting HR", details["reporting_hr"] + ", " + details["hr_designation"]),
    ]
    y = 515
    for label, value in detail_lines:
        commands.append(_pdf_text(62, y, f"{label}:", "F2", 10, "0.16 0.2 0.28"))
        commands.append(_pdf_text(168, y, value, "F1", 10, "0.16 0.2 0.28"))
        y -= 17

    commands.append(_pdf_text(48, 420, "Venue", "F2", 12, "0.31 0.27 0.89"))
    y = 402
    for line in details["venue_lines"]:
        commands.append(_pdf_text(48, y, line, "F1", 10, "0.16 0.2 0.28"))
        y -= 15

    y -= 8
    commands.append(_pdf_text(48, y, "Please report 30 minutes before your scheduled interview time.", "F1", 10, "0.16 0.2 0.28"))
    y -= 28
    commands.append(_pdf_text(48, y, "We wish you all the best for your interview.", "F2", 11, "0.31 0.27 0.89"))
    commands.append(_pdf_text(48, 56, "ByteNova Technologies | Crystal IT Park, Vijay Nagar, Indore, Madhya Pradesh", "F1", 8, "0.35 0.4 0.48"))

    stream = "\n".join(commands).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
    ]
    output = BytesIO()
    output.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode())
        output.write(obj)
        output.write(b"\nendobj\n")
    xref_offset = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode())
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode())
    output.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
    )
    return output.getvalue()


def _owned_application(app_id: int) -> Application:
    application = db.session.get(Application, app_id)
    if not application or application.candidate_id != current_user.id:
        abort(404)
    return application


@candidate_bp.route("/dashboard")
@login_required
@role_required("candidate")
def dashboard():
    """Candidate dashboard with interview progress when an invitation is available."""
    applications = (
        Application.query.filter_by(candidate_id=current_user.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    in_progress = sum(
        1 for application in applications if application.status in ("submitted", "under_review", "interview")
    )
    interview_application = next(
        (application for application in applications if application.status == "interview"),
        None,
    )
    interview_details = _interview_context(interview_application) if interview_application else None
    return render_template(
        "candidate/dashboard.html",
        applications=applications,
        user=current_user,
        in_progress=in_progress,
        interview_application=interview_application,
        interview_details=interview_details,
        interview_invitations=1 if interview_application else 0,
    )


@candidate_bp.route("/applications")
@login_required
@role_required("candidate")
def applications():
    """Full list of candidate applications with status."""
    applications = (
        Application.query.filter_by(candidate_id=current_user.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return render_template("candidate/applications.html", applications=applications)


@candidate_bp.route("/applications/<int:app_id>")
@login_required
@role_required("candidate")
def application_detail(app_id):
    """Track a single application status."""
    application = _owned_application(app_id)

    interview_details = None
    if application.status == "interview" and application.job.title == "Python Developer Intern":
        interview_details = _interview_context(application)
    elif application.status == "interview":
        # Fallback so the interview status page still renders for the required scenario
        interview_details = _interview_context(application)

    return render_template(
        "candidate/application_detail.html",
        application=application,
        interview_details=interview_details,
    )


@candidate_bp.route("/applications/<int:app_id>/interview-invitation")
@login_required
@role_required("candidate")
def interview_invitation(app_id):
    """Render the official interview invitation for the candidate's own application."""
    application = _owned_application(app_id)
    if application.status != "interview":
        abort(404)
    return render_template(
        "candidate/interview_invitation.html",
        application=application,
        details=_interview_context(application),
    )


@candidate_bp.route("/applications/<int:app_id>/interview-call-letter.pdf")
@login_required
@role_required("candidate")
def download_interview_call_letter(app_id):
    """Download a generated PDF interview call letter for an invited candidate."""
    application = _owned_application(app_id)
    if application.status != "interview":
        abort(404)
    pdf = _build_call_letter_pdf(_interview_context(application))
    response = Response(pdf, mimetype="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=ByteNova_Interview_Call_Letter_Riyansh.pdf"
    return response


@candidate_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("candidate")
def profile():
    """Update candidate profile information."""
    if request.method == "POST":
        current_user.full_name = request.form.get("full_name", "").strip()
        current_user.phone = request.form.get("phone", "").strip()
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("candidate.profile"))

    return render_template("candidate/profile.html", user=current_user)

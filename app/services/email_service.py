"""
Email service for ByteNova — production-ready architecture with mock delivery.

In development, emails are logged to stdout and appended to logs/emails.log.
Set MAIL_ENABLED=true and configure SMTP env vars for real delivery.
"""
import logging
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app

logger = logging.getLogger(__name__)


def _log_email(to: str, subject: str, body: str) -> None:
    """Persist mock email to log file for debugging."""
    log_dir = os.path.join(current_app.root_path, "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "emails.log")
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = f"\n{'=' * 60}\n[{timestamp}]\nTO: {to}\nSUBJECT: {subject}\n{'-' * 60}\n{body}\n"
    with open(log_file, "a", encoding="utf-8") as fh:
        fh.write(entry)
    logger.info("Mock email queued → %s | %s", to, subject)


def send_email(to: str, subject: str, body: str, html: str | None = None) -> bool:
    """
    Send an email via SMTP when enabled, otherwise mock/log it.
    Returns True on success.
    """
    sender = current_app.config["MAIL_DEFAULT_SENDER"]

    if not current_app.config.get("MAIL_ENABLED"):
        _log_email(to, subject, body)
        print(f"\n[MOCK EMAIL]\nTo: {to}\nSubject: {subject}\n{body}\n")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to
        msg.attach(MIMEText(body, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(
            current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"]
        ) as server:
            if current_app.config["MAIL_USE_TLS"]:
                server.starttls()
            username = current_app.config["MAIL_USERNAME"]
            password = current_app.config["MAIL_PASSWORD"]
            if username and password:
                server.login(username, password)
            server.sendmail(sender, to, msg.as_string())
        return True
    except Exception as exc:
        logger.exception("Failed to send email to %s: %s", to, exc)
        return False


def notify_application_received(candidate_email: str, candidate_name: str, job_title: str) -> None:
    """Notify candidate that their application was received."""
    subject = f"Application Received — {job_title} at ByteNova"
    body = (
        f"Hi {candidate_name},\n\n"
        f"Thank you for applying for the {job_title} position at ByteNova Technologies. "
        f"Our recruiting team will review your application and get back to you soon.\n\n"
        f"Best regards,\nByteNova Talent Team"
    )
    send_email(candidate_email, subject, body)


def notify_status_update(
    candidate_email: str, candidate_name: str, job_title: str, new_status: str
) -> None:
    """Notify candidate when their application status changes."""
    status_messages = {
        "under_review": "Your application is now under review by our hiring team.",
        "interview": "Congratulations! We'd like to invite you to an interview.",
        "offered": "Great news! We're extending an offer for this role.",
        "rejected": "After careful consideration, we've decided to move forward with other candidates.",
    }
    message = status_messages.get(new_status, f"Your application status is now: {new_status}")
    subject = f"Application Update — {job_title} at ByteNova"
    body = f"Hi {candidate_name},\n\n{message}\n\nBest regards,\nByteNova Talent Team"
    send_email(candidate_email, subject, body)

"""Public pages — home, about, services, portfolio, contact, careers landing."""
import json
import traceback

from flask import Blueprint, Response, current_app, jsonify, render_template, request

from app import db
from app.models import ContactMessage, Job, NewsletterSubscriber

main_bp = Blueprint("main", __name__)

SERVICES_DATA = {
    "python-development": {
        "title": "Python Development",
        "icon": "bi-filetype-py",
        "short": "Automations, backend services, and production-ready Python solutions.",
        "overview": "We build clean, scalable Python solutions for automation, backend services, and product features. Our team writes maintainable code with testing coverage and clear documentation.",
        "benefits": [
            "Rapid prototyping and iteration cycles",
            "Clean, maintainable code with testing",
            "Integration with existing business systems",
            "Scalable architecture ready for growth",
        ],
        "technologies": ["Python 3", "Flask", "FastAPI", "SQLAlchemy", "Celery", "Pandas", "NumPy"],
        "cta": "Need Python expertise? Let's discuss your project.",
        "image_icon": "bi-filetype-py",
    },
    "ai-automation": {
        "title": "AI Automation",
        "icon": "bi-cpu",
        "short": "Practical AI workflows that help teams save time and reduce manual work.",
        "overview": "We design practical AI automation workflows using Python, APIs, and LLM tools to solve everyday client problems. From document processing to intelligent data extraction, we make AI work for your business.",
        "benefits": [
            "Reduce manual data entry by up to 80%",
            "Automate repetitive business workflows",
            "Intelligent document processing and extraction",
            "LLM-powered customer support automation",
        ],
        "technologies": ["OpenAI APIs", "LangChain", "Python", "Natural Language Processing", "RPA Tools", "Vector Databases"],
        "cta": "Automate your workflows with practical AI solutions.",
        "image_icon": "bi-cpu",
    },
    "web-development": {
        "title": "Web Development",
        "icon": "bi-window",
        "short": "Responsive web apps and dashboards tailored to your operations.",
        "overview": "We build fast, responsive web applications for founders and small business teams. From marketing websites to full-featured SaaS platforms, our web solutions are designed for performance and conversion.",
        "benefits": [
            "Mobile-first responsive design",
            "SEO-optimized architecture",
            "Fast loading and performance tuned",
            "Easy content management integration",
        ],
        "technologies": ["React", "Flask", "Bootstrap 5", "HTML5/CSS3", "JavaScript", "REST APIs"],
        "cta": "Launch your web presence with a modern, responsive site.",
        "image_icon": "bi-window",
    },
    "rest-apis": {
        "title": "REST API Development",
        "icon": "bi-diagram-3",
        "short": "Reliable APIs with clean design, performance considerations, and docs.",
        "overview": "We design and build reliable REST APIs that power your applications and integrations. Our APIs follow best practices for security, performance, and developer experience.",
        "benefits": [
            "Well-documented endpoints with OpenAPI/Swagger",
            "Authentication and authorization built-in",
            "Rate limiting and performance optimization",
            "Versioned APIs for backward compatibility",
        ],
        "technologies": ["Flask RESTful", "FastAPI", "PostgreSQL", "JWT Auth", "Redis Caching", "Docker"],
        "cta": "Build reliable APIs that scale with your business.",
        "image_icon": "bi-diagram-3",
    },
    "dashboards": {
        "title": "Business Dashboards",
        "icon": "bi-bar-chart",
        "short": "Actionable dashboards for sales, operations, finance and HR.",
        "overview": "We build actionable dashboards that help decision-makers stay on top of key metrics. Real-time data visualization, custom reports, and intuitive interfaces for your team.",
        "benefits": [
            "Real-time business intelligence",
            "Custom KPI tracking and alerts",
            "Interactive data visualizations",
            "Exportable reports and scheduled summaries",
        ],
        "technologies": ["Chart.js", "D3.js", "Flask", "SQL", "REST APIs", "Bootstrap 5"],
        "cta": "Get the insights you need with a custom business dashboard.",
        "image_icon": "bi-bar-chart",
    },
    "desktop-applications": {
        "title": "Desktop Applications",
        "icon": "bi-display",
        "short": "Utility-grade desktop applications for internal teams and operations.",
        "overview": "We develop utility-grade desktop applications for internal operations and specialized workflows. Cross-platform compatibility and intuitive interfaces for your team's daily tools.",
        "benefits": [
            "Cross-platform compatibility (Windows, Mac, Linux)",
            "Offline-capable applications",
            "Integration with existing business tools",
            "Custom UI/UX tailored to your workflow",
        ],
        "technologies": ["Python", "PyQt", "Tkinter", "Electron", "SQLite", "REST API Integration"],
        "cta": "Streamline your operations with a custom desktop application.",
        "image_icon": "bi-display",
    },
}

PORTFOLIO_DATA = {
    "hospital-management": {
        "title": "Hospital Management System",
        "icon": "bi-hospital",
        "short": "Patient scheduling, billing workflows, and role-based access.",
        "description": "A comprehensive hospital management system designed to streamline patient registration, appointment scheduling, billing, and doctor workflows. Built with role-based access for administrators, doctors, nurses, and reception staff.",
        "features": [
            "Patient registration and medical history tracking",
            "Appointment scheduling with calendar integration",
            "Billing and invoice generation",
            "Doctor and staff management",
            "Pharmacy inventory management",
            "Lab report integration",
        ],
        "technologies": ["Python", "Flask", "REST API", "SQLite", "Bootstrap 5", "Chart.js"],
        "duration": "4 Months",
        "client_industry": "Healthcare",
    },
    "restaurant-pos": {
        "title": "Restaurant POS",
        "icon": "bi-cup-hot",
        "short": "Fast billing, menu management, and daily reports.",
        "description": "A modern Point of Sale system designed for restaurants and cafes. Features include fast order entry, table management, kitchen display integration, and comprehensive daily sales reporting.",
        "features": [
            "Visual table layout and management",
            "Menu management with categories and modifiers",
            "Fast order entry with touch-screen support",
            "Multiple payment methods (Cash, Card, UPI)",
            "Kitchen order display system",
            "Daily and monthly sales reports",
        ],
        "technologies": ["JavaScript", "Python", "Dashboards", "SQLite", "REST API"],
        "duration": "3 Months",
        "client_industry": "Food & Beverage",
    },
    "college-erp": {
        "title": "College ERP",
        "icon": "bi-mortarboard",
        "short": "Admissions, attendance, and faculty portals with secure workflows.",
        "description": "An Enterprise Resource Planning system designed for educational institutions. Manages the entire student lifecycle from admissions through graduation, with dedicated portals for students, faculty, and administration.",
        "features": [
            "Online admission application and management",
            "Student attendance tracking with reports",
            "Faculty portal for grade entry and scheduling",
            "Fee management with payment tracking",
            "Timetable and exam scheduling",
            "Library management integration",
        ],
        "technologies": ["Python", "Role-based Access", "Flask", "SQLite", "Bootstrap 5"],
        "duration": "6 Months",
        "client_industry": "Education",
    },
    "inventory-management": {
        "title": "Inventory Management System",
        "icon": "bi-bag-check",
        "short": "Stock tracking, purchase orders, and audit-friendly exports.",
        "description": "A robust inventory management solution for businesses that need real-time stock tracking, automated purchase orders, and detailed audit trails. Built for warehouses, retail stores, and distribution centers.",
        "features": [
            "Real-time stock level tracking",
            "Automated low-stock alerts and reorder suggestions",
            "Purchase order generation and management",
            "Barcode scanning support",
            "Multi-warehouse management",
            "Audit-friendly export and reporting",
        ],
        "technologies": ["Flask", "SQLite", "Python", "REST API", "Bootstrap 5"],
        "duration": "3 Months",
        "client_industry": "Retail & Distribution",
    },
    "billing-software": {
        "title": "Billing Software",
        "icon": "bi-receipt",
        "short": "Invoice generation, GST-ready formats, and automated numbering.",
        "description": "A professional billing and invoicing software designed for Indian businesses. Supports GST-compliant invoice formats, automated numbering sequences, and comprehensive customer and vendor management.",
        "features": [
            "GST-ready invoice generation",
            "Automated invoice numbering",
            "Customer and vendor management",
            "Payment tracking and reconciliation",
            "Credit note and debit note management",
            "Financial reports and tax summaries",
        ],
        "technologies": ["REST API", "SQLite", "Python", "Flask", "Bootstrap 5"],
        "duration": "2 Months",
        "client_industry": "Finance & Accounting",
    },
    "hr-management": {
        "title": "HR Management Portal",
        "icon": "bi-people",
        "short": "Leave requests, hiring pipeline review, and employee records.",
        "description": "A comprehensive HR management portal that streamlines employee management, leave tracking, recruitment pipeline, and performance reviews. Built for growing teams that need organized HR operations.",
        "features": [
            "Employee directory with detailed profiles",
            "Leave management with approval workflows",
            "Recruitment and hiring pipeline tracking",
            "Attendance and timesheet management",
            "Performance review scheduling",
            "Document and compliance management",
        ],
        "technologies": ["Flask", "Admin UI", "Python", "SQLite", "Bootstrap 5"],
        "duration": "4 Months",
        "client_industry": "Human Resources",
    },
}


@main_bp.route("/")
def index():
    """Landing page with featured open roles."""
    featured_jobs = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).limit(3).all()
    total_jobs = Job.query.filter_by(is_active=True).count()
    return render_template("index.html", featured_jobs=featured_jobs, total_jobs=total_jobs)


@main_bp.route("/about")
def about():
    """Company culture and mission page."""
    return render_template("about.html")


@main_bp.route("/careers")
def careers():
    """Careers overview with link to job listings."""
    open_positions = Job.query.filter_by(is_active=True).count()
    return render_template("careers.html", open_positions=open_positions)


@main_bp.route("/services")
def services():
    """Services overview page."""
    return render_template("services/index.html", services=SERVICES_DATA)


@main_bp.route("/services/<slug>")
def service_detail(slug):
    """Individual service detail page."""
    service = SERVICES_DATA.get(slug)
    if not service:
        return render_template("errors/404.html"), 404
    return render_template("services/detail.html", service=service, slug=slug)


@main_bp.route("/portfolio")
def portfolio():
    """Portfolio overview page."""
    return render_template("portfolio/index.html", projects=PORTFOLIO_DATA)


@main_bp.route("/portfolio/<slug>")
def portfolio_detail(slug):
    """Individual portfolio project detail page."""
    project = PORTFOLIO_DATA.get(slug)
    if not project:
        return render_template("errors/404.html"), 404
    return render_template("portfolio/detail.html", project=project, slug=slug)


@main_bp.route("/contact")
def contact():
    """Contact page with form."""
    return render_template("contact.html")


@main_bp.route("/contact/submit", methods=["POST"])
def contact_submit():
    """Handle contact form submission via AJAX."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid request data."}), 400

        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()
        subject = (data.get("subject") or data.get("messageTitle") or "").strip()
        message = (data.get("message") or "").strip()

        if not all([name, email, subject, message]):
            return jsonify({"success": False, "message": "Please fill all required fields."}), 400

        contact_msg = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
        )
        db.session.add(contact_msg)
        db.session.commit()

        return jsonify({"success": True, "message": "Message received! We'll get back to you within 1-2 business days."})

    except Exception:
        current_app.logger.error(f"Contact form error: {traceback.format_exc()}")
        return jsonify({"success": False, "message": "An error occurred. Please try again later."}), 500


@main_bp.route("/team")
def team():
    """Meet the team page."""
    return render_template("team.html")


@main_bp.route("/testimonials")
def testimonials():
    """Client testimonials page."""
    return render_template("testimonials.html")


@main_bp.route("/faq")
def faq():
    """Frequently asked questions page."""
    return render_template("faq.html")


@main_bp.route("/privacy-policy")
def privacy_policy():
    """Privacy policy page."""
    return render_template("privacy_policy.html")


@main_bp.route("/newsletter/subscribe", methods=["POST"])
def newsletter_subscribe():
    """Handle newsletter subscription via AJAX."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid request."}), 400

        email = (data.get("email") or "").strip()

        if not email:
            return jsonify({"success": False, "message": "Email is required."}), 400

        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            return jsonify({"success": True, "message": "You're already subscribed!"})

        subscriber = NewsletterSubscriber(email=email)
        db.session.add(subscriber)
        db.session.commit()

        return jsonify({"success": True, "message": "Subscribed successfully! Check your inbox for updates."})

    except Exception:
        current_app.logger.error(f"Newsletter error: {traceback.format_exc()}")
        return jsonify({"success": False, "message": "An error occurred. Please try again later."}), 500


from flask import Flask, render_template, request, redirect, send_file, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
def log_action(action):

    if "user" not in session:
        return

    log = AuditLog(
        user=session.get("user"),
        action=action,
        timestamp=datetime.now()
    )

    db.session.add(log)
    db.session.commit()
import os
import pandas as pd
from reportlab.pdfgen import canvas

from models import db, User, Risk, Control, ComplianceGap, AuditWorkflow, Asset, Incident, Vendor, VendorScore, MonitoringEvent, AuditLog, ReportLog

import re

# ======================
# PASSWORD VALIDATION
# ======================

PASSWORD_MODE = "strong"   # default setting: "strong" or "very_strong"

def validate_password(password):

    min_length = 8 if PASSWORD_MODE == "strong" else 15

    if len(password) < min_length:
        return f"Password must be at least {min_length} characters."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."

    return None

app = Flask(__name__)
app.secret_key = "secretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///grc.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ======================
# THEME
# ======================

@app.context_processor
def inject_theme():
    return dict(theme=session.get("theme", "dark"))


# ======================
# AUTH
# ======================

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session["user"] = user.username
            session["role"] = user.role

            return redirect("/dashboard")

    return render_template("pages/login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ======================
# DASHBOARD
# ======================

@app.route("/")
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    risks = Risk.query.all()
    controls = Control.query.all()

    total_risks = len(risks)
    high_risks = len([r for r in risks if r.score >= 15])

    low_count = len([r for r in risks if r.score <= 5])
    medium_count = len([r for r in risks if 6 <= r.score <= 14])
    high_count = len([r for r in risks if r.score >= 15])

    implemented = len([c for c in controls if c.status == "Implemented"])
    compliance_score = int((implemented / len(controls)) * 100) if controls else 0

    return render_template(
        "pages/dashboard_global.html",
        total_risks=total_risks,
        high_risks=high_risks,
        compliance_score=compliance_score,
        low_count=low_count,
        medium_count=medium_count,
        high_count=high_count
    )


# ======================
# RISK
# ======================

@app.route("/create-risk", methods=["GET","POST"])
def create_risk():

    if request.method == "POST":

        impact = int(request.form["impact"])
        likelihood = int(request.form["likelihood"])
        score = impact * likelihood

        level = "Low"
        if score >= 15:
            level = "High"
        elif score >= 6:
            level = "Medium"

        risk = Risk(
            risk_name=request.form["risk_name"],
            asset=request.form["asset"],
            impact=impact,
            likelihood=likelihood,
            score=score,
            level=level,
            owner=request.form["owner"]
        )

        db.session.add(risk)
        db.session.commit()

        log_action("Created Risk: " + request.form["risk_name"])

        return redirect("/risk-register")

    return render_template("pages/risk_create.html")


@app.route("/risk-register")
def risk_register():
    risks = Risk.query.all()
    return render_template("pages/risk_register.html", risks=risks)


@app.route("/risk-dashboard")
def risk_dashboard():

    risks = Risk.query.all()

    low = len([r for r in risks if r.score <= 5])
    medium = len([r for r in risks if 6 <= r.score <= 14])
    high = len([r for r in risks if r.score >= 15])

    return render_template(
        "pages/risk_dashboard.html",
        low=low,
        medium=medium,
        high=high
    )


# ======================
# PAGE ROUTES
# ======================

from iso_controls import ISO_CONTROLS

@app.route("/controls-library")
def controls_library():

    search = request.args.get("search","")

    if search:
        filtered = [c for c in ISO_CONTROLS if search.lower() in c.lower()]
    else:
        filtered = ISO_CONTROLS

    return render_template(
        "pages/controls_library.html",
        controls=filtered,
        search=search
    )


@app.route("/compliance-gap")
def compliance_gap():
    gaps = ComplianceGap.query.all()
    return render_template("pages/compliance_gap.html", gaps=gaps)


@app.route("/audit-management")
def audit_management():
    audits = AuditWorkflow.query.all()
    return render_template("pages/audit_management.html", audits=audits)


@app.route("/audit-workflow")
def audit_workflow():
    audits = AuditWorkflow.query.all()
    return render_template("pages/audit_workflow.html", audits=audits)


@app.route("/maturity-dashboard")
def maturity_dashboard():
    controls = Control.query.all()
    return render_template("pages/maturity_dashboard.html", controls=controls)


@app.route("/assets")
def assets():
    assets = Asset.query.all()
    return render_template("pages/assets.html", assets=assets)


@app.route("/incidents")
def incidents():
    incidents = Incident.query.all()
    return render_template("pages/incidents.html", incidents=incidents)


@app.route("/incident-lifecycle")
def incident_lifecycle():
    incidents = Incident.query.all()
    return render_template("pages/incident_lifecycle.html", incidents=incidents)


@app.route("/live-monitoring")
def live_monitoring():
    events = MonitoringEvent.query.order_by(MonitoringEvent.timestamp.desc()).all()
    return render_template("pages/live_monitoring.html", events=events)


@app.route("/vendors")
def vendors():
    vendors = Vendor.query.all()
    return render_template("pages/vendors.html", vendors=vendors)


@app.route("/vendor-scoring")
def vendor_scoring():
    scores = VendorScore.query.all()
    return render_template("pages/vendor_scoring.html", scores=scores)


@app.route("/reports")
def reports():
    return render_template("pages/reports.html")


@app.route("/executive-reporting")
def executive_reporting():
    risks = Risk.query.all()
    controls = Control.query.all()
    return render_template("pages/executive_reporting.html", risks=risks, controls=controls)


# ======================
# ADD FUNCTIONS
# ======================

@app.route("/add-control", methods=["POST"])
def add_control():

    control = Control(
        control_name=request.form["control_name"],
        framework=request.form["framework"],
        status=request.form["status"]
    )

    db.session.add(control)
    db.session.commit()
    log_action("Added Control: " + request.form["control_name"])

    return redirect("/controls-library")


@app.route("/add-gap", methods=["POST"])
def add_gap():

    gap = ComplianceGap(
        control_name=request.form["control_name"],
        gap_description=request.form["gap_description"],
        remediation=request.form["remediation"],
        status=request.form["status"]
    )

    db.session.add(gap)
    db.session.commit()
    log_action("Added Compliance Gap for Control: " + request.form["control_name"])

    return redirect("/compliance-gap")


@app.route("/add-audit", methods=["POST"])
def add_audit():

    audit_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()

    audit = AuditWorkflow(
        audit_name=request.form["audit_name"],
        auditor=request.form["auditor"],
        status=request.form["status"],
        date=audit_date
    )

    db.session.add(audit)
    db.session.commit()
    log_action("Created Audit: " + request.form["audit_name"])

    return redirect("/audit-management")


@app.route("/add-asset", methods=["POST"])
def add_asset():

    asset = Asset(
        asset_name=request.form["asset_name"],
        asset_type=request.form["asset_type"],
        owner=request.form["owner"],
        criticality=request.form["criticality"]
    )

    db.session.add(asset)
    db.session.commit()
    log_action("Added Asset: " + request.form["asset_name"])

    return redirect("/assets")


@app.route("/add-incident", methods=["POST"])
def add_incident():

    incident = Incident(
        title=request.form["title"],
        severity=request.form["severity"],
        status=request.form["status"],
        description=request.form["description"]
    )

    db.session.add(incident)
    db.session.commit()
    log_action("Submitted Incident: " + request.form["title"])

    return redirect("/incidents")


@app.route("/add-event", methods=["POST"])
def add_event():

    event = MonitoringEvent(
        event_name=request.form["event_name"],
        severity=request.form["severity"],
        timestamp=datetime.now()
    )

    db.session.add(event)
    db.session.commit()
    log_action("Logged Monitoring Event: " + request.form["event_name"])

    return redirect("/live-monitoring")


@app.route("/add-vendor", methods=["POST"])
def add_vendor():

    vendor = Vendor(
        vendor_name=request.form["vendor_name"],
        service=request.form["service"],
        risk_level=request.form["risk_level"],
        contact_email=request.form["contact_email"]
    )

    db.session.add(vendor)
    db.session.commit()
    log_action("Added Vendor: " + request.form["vendor_name"])

    return redirect("/vendors")


@app.route("/add-score", methods=["POST"])
def add_score():

    security = int(request.form["security_score"])
    compliance = int(request.form["compliance_score"])
    overall = int((security + compliance) / 2)

    score = VendorScore(
        vendor_name=request.form["vendor_name"],
        security_score=security,
        compliance_score=compliance,
        overall_score=overall
    )

    db.session.add(score)
    db.session.commit()
    log_action("Calculated Vendor Score: " + request.form["vendor_name"])

    return redirect("/vendor-scoring")


# ======================
# DELETE FUNCTIONS
# ======================

def admin_only():
    role = session.get("role","").lower()
    return role not in ["admin", "superadmin"]


@app.route("/delete-risk/<int:id>")
def delete_risk(id):

    if admin_only():
        return "Access Denied"

    risk = Risk.query.get_or_404(id)
    db.session.delete(risk)
    db.session.commit()
    log_action("Deleted Risk: " + risk.risk_name)

    return redirect("/risk-register")


@app.route("/delete-control/<int:id>")
def delete_control(id):

    if admin_only():
        return "Access Denied"

    control = Control.query.get_or_404(id)
    db.session.delete(control)
    db.session.commit()
    log_action("Deleted Control: " + control.control_name)

    return redirect("/controls-library")


@app.route("/delete-gap/<int:id>")
def delete_gap(id):

    if admin_only():
        return "Access Denied"

    gap = ComplianceGap.query.get_or_404(id)
    db.session.delete(gap)
    db.session.commit()
    log_action("Deleted Compliance Gap")

    return redirect("/compliance-gap")


@app.route("/delete-audit/<int:id>")
def delete_audit(id):

    if admin_only():
        return "Access Denied"

    audit = AuditWorkflow.query.get_or_404(id)
    db.session.delete(audit)
    db.session.commit()
    log_action("Deleted Audit: " + audit.audit_name)

    return redirect("/audit-management")


@app.route("/delete-asset/<int:id>")
def delete_asset(id):

    if admin_only():
        return "Access Denied"

    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    log_action("Deleted Asset: " + asset.asset_name)

    return redirect("/assets")


@app.route("/delete-incident/<int:id>")
def delete_incident(id):

    if admin_only():
        return "Access Denied"

    incident = Incident.query.get_or_404(id)
    db.session.delete(incident)
    db.session.commit()
    log_action("Deleted Incident")

    return redirect("/incidents")


@app.route("/delete-event/<int:id>")
def delete_event(id):

    if admin_only():
        return "Access Denied"

    event = MonitoringEvent.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    log_action("Deleted Monitoring Event")

    return redirect("/live-monitoring")


@app.route("/delete-vendor/<int:id>")
def delete_vendor(id):

    if admin_only():
        return "Access Denied"

    vendor = Vendor.query.get_or_404(id)
    db.session.delete(vendor)
    db.session.commit()
    log_action("Deleted Vendor: " + vendor.vendor_name)

    return redirect("/vendors")


@app.route("/delete-score/<int:id>")
def delete_score(id):

    if admin_only():
        return "Access Denied"

    score = VendorScore.query.get_or_404(id)
    db.session.delete(score)
    db.session.commit()

    return redirect("/vendor-scoring")

@app.route("/iso-report-page")
def iso_report_page():
    return render_template("pages/iso_report.html")


@app.route("/excel-report-page")
def excel_report_page():
    return render_template("pages/excel_report.html")


@app.route("/pdf-report-page")
def pdf_report_page():
    return render_template("pages/pdf_report.html")


@app.route("/generate-iso-report")
def generate_iso_report():

    risks = Risk.query.all()
    controls = Control.query.all()

    filename = "ISO_Report.txt"

    with open(filename, "w") as f:
        f.write("ISO 27001 Compliance Report\n\n")
        f.write(f"Total Risks: {len(risks)}\n")
        f.write(f"Total Controls: {len(controls)}\n")
    log_action("Generated ISO Report")

    return send_file(filename, as_attachment=True)


@app.route("/export-excel")
def export_excel():

    level = request.args.get("level")
    asset = request.args.get("asset")
    owner = request.args.get("owner")

    query = Risk.query

    if level:
        query = query.filter_by(level=level)

    if asset:
        query = query.filter(Risk.asset.contains(asset))

    if owner:
        query = query.filter(Risk.owner.contains(owner))

    risks = query.all()

    data = []

    for r in risks:
        data.append({
            "Risk Name": r.risk_name,
            "Asset": r.asset,
            "Score": r.score,
            "Level": r.level,
            "Owner": r.owner
        })

    df = pd.DataFrame(data)

    file = "risk_report.xlsx"
    df.to_excel(file, index=False)
    # REPORT HISTORY LOG
    log = ReportLog(
    user=session["user"],
    report_type="Risk Excel Report",
    timestamp=datetime.now()
)
    db.session.add(log)
    db.session.commit()

    return send_file(file, as_attachment=True)


@app.route("/export-pdf")
def export_pdf():

    risks = Risk.query.all()

    file = "risk_report.pdf"
    c = canvas.Canvas(file)

    y = 800

    for r in risks:
        c.drawString(50, y, f"{r.risk_name} | {r.asset} | {r.level}")
        y -= 20

    c.save()
    log_action("Exported PDF Report")

    return send_file(file, as_attachment=True)

@app.route("/delete-user/<int:id>")
def delete_user(id):

    if session.get("role","").lower() != "superadmin":
        return "Access Denied"

    user = User.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()
    log_action("Deleted User: " + "user.username")

    return redirect("/users")

@app.route("/update-role/<int:id>", methods=["POST"])
def update_role(id):

    if session.get("role","").lower() != "superadmin":
        return "Access Denied"

    user = User.query.get_or_404(id)

    new_role = request.form["role"]
    user.role = new_role

    db.session.commit()

    return redirect("/users")

# ======================
# ADMINISTRATION
# ======================

# USER MANAGEMENT
@app.route("/users")
def users():

    if "user" not in session:
        return redirect("/login")

    if session.get("role","").lower() not in ["admin", "superadmin"]:
        return "Access Denied"

    users = User.query.all()

    return render_template("pages/users.html", users=users)


# CREATE USER
@app.route("/create-user", methods=["GET","POST"])
def create_user():

    if session.get("role","").lower() != "superadmin":
        return "Access Denied"

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        # check if username already exists
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template(
                "pages/create_user.html",
                error="Username already exists. Please choose another."
            )

        error = validate_password(password)

        if error:
            return render_template("pages/create_user.html", error=error)

        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/users")

    return render_template("pages/create_user.html")


# ROLES & PERMISSIONS
@app.route("/roles-permissions")
def roles_permissions():

    if "user" not in session:
        return redirect("/login")

    if session.get("role","").lower() not in ["admin","superadmin"]:
        return "Access Denied"

    users = User.query.all()

    return render_template("pages/roles_permissions.html", users=users)


# SETTINGS
@app.route("/settings", methods=["GET","POST"])
def settings():

    global PASSWORD_MODE

    if request.method == "POST":

        PASSWORD_MODE = request.form.get("password_policy")

        session["theme"] = request.form.get("theme")

    return render_template("pages/settings.html", password_mode=PASSWORD_MODE)

@app.route("/audit-logs")
def audit_logs():

    if "user" not in session:
        return redirect("/login")

    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()

    return render_template("pages/audit_logs.html", logs=logs)


@app.route("/report-history")
def report_history():

    logs = ReportLog.query.order_by(ReportLog.timestamp.desc()).all()

    return render_template("pages/report_history.html", logs=logs)


@app.route("/statement-of-applicability", methods=["GET","POST"])
def statement_of_applicability():

    from iso_controls import ISO_CONTROLS

    if request.method == "POST":

        for control in ISO_CONTROLS:

            checked = request.form.get(control)

            record = SoAControl.query.filter_by(control_name=control).first()

            if not record:
                record = SoAControl(control_name=control)

            record.applicable = True if checked else False

            db.session.add(record)

        db.session.commit()

        return redirect("/statement-of-applicability")

    records = SoAControl.query.all()

    status = {r.control_name: r.applicable for r in records}

    return render_template(
        "pages/soa.html",
        controls=ISO_CONTROLS,
        status=status
    )

# ======================
# RUN
# ======================

import os

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username="admin").first()

        if not admin:
            admin = User(
                username="admin",
                password=generate_password_hash("admin123"),
                role="SuperAdmin"
            )

            db.session.add(admin)
            db.session.commit()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

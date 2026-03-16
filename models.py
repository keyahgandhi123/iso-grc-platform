from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ======================
# USERS
# ======================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))


# ======================
# RISKS
# ======================

class Risk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    risk_name = db.Column(db.String(200))
    asset = db.Column(db.String(200))
    likelihood = db.Column(db.Integer)
    impact = db.Column(db.Integer)
    score = db.Column(db.Integer)
    level = db.Column(db.String(50))
    owner = db.Column(db.String(100))


# ======================
# CONTROLS
# ======================

class Control(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    control_name = db.Column(db.String(200))
    framework = db.Column(db.String(100))
    status = db.Column(db.String(50))


# ======================
# AUDIT LOG
# ======================

class AuditLog(db.Model):
    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    action = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime)


# ======================
# ASSETS
# ======================

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(200))
    asset_type = db.Column(db.String(100))
    owner = db.Column(db.String(100))
    criticality = db.Column(db.String(50))


# ======================
# INCIDENTS
# ======================

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    severity = db.Column(db.String(50))
    status = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ======================
# VENDORS
# ======================

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(200))
    service = db.Column(db.String(200))
    risk_level = db.Column(db.String(50))
    contact_email = db.Column(db.String(200))


# ======================
# VENDOR SCORING
# ======================

class VendorScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(200))
    security_score = db.Column(db.Integer)
    compliance_score = db.Column(db.Integer)
    overall_score = db.Column(db.Integer)


# ======================
# COMPLIANCE GAP
# ======================

class ComplianceGap(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    control_id = db.Column(db.String(20))
    control_name = db.Column(db.String(200))

    gap_description = db.Column(db.String(500))
    remediation = db.Column(db.String(500))
    status = db.Column(db.String(100))


# ======================
# AUDIT WORKFLOW
# ======================

class AuditWorkflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    audit_name = db.Column(db.String(200))
    auditor = db.Column(db.String(100))
    status = db.Column(db.String(50))
    date = db.Column(db.Date)


# ======================
# LIVE MONITORING
# ======================

class MonitoringEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(200))
    severity = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ReportLog(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user = db.Column(db.String(100))

    report_type = db.Column(db.String(100))

    timestamp = db.Column(db.DateTime)

# =================
# DATABASE MODELS
# =================

class SoAControl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    control_name = db.Column(db.String(200), unique=True)
    applicable = db.Column(db.Boolean, default=True)
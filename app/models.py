from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


# ==========================================
# USER LOADER (required by Flask-Login)
# ==========================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==========================================
# USER MODEL (base identity for everyone)
# ==========================================
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'doctor', 'patient'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes the plain-text password before storing it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


# ==========================================
# DOCTOR MODEL
# ==========================================
class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    specialization = db.Column(db.String(100))
    qualification = db.Column(db.String(150))
    availability = db.Column(db.String(200))

    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    medical_records = db.relationship('MedicalRecord', backref='doctor', lazy=True)
    reviews = db.relationship('Review', backref='doctor', lazy=True)
    def __repr__(self):
        return f'<Doctor {self.user.name if self.user else "Unknown"}>'


# ==========================================
# PATIENT MODEL
# ==========================================
class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    blood_group = db.Column(db.String(10))

    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True)
    symptom_logs = db.relationship('SymptomLog', backref='patient', lazy=True)

    def __repr__(self):
        return f'<Patient {self.user.name if self.user else "Unknown"}>'


# ==========================================
# APPOINTMENT MODEL
# ==========================================
class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')
    reason = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.id} - {self.status}>'


# ==========================================
# MEDICAL RECORD MODEL
# ==========================================
class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    diagnosis = db.Column(db.String(300))
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MedicalRecord {self.id}>'


# ==========================================
# SYMPTOM LOG MODEL (for AI Symptom Analyzer)
# ==========================================
class SymptomLog(db.Model):
    __tablename__ = 'symptom_logs'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    symptoms_text = db.Column(db.Text, nullable=False)
    predicted_disease = db.Column(db.String(150))
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SymptomLog {self.id}>'


# ==========================================
# NOTIFICATION MODEL
# ==========================================
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id}>'
# ==========================================
# REVIEW MODEL (Patient rates Doctor)
# ==========================================
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} - {self.rating} stars>'    
       # ==========================================
# DIAGNOSTIC TEST (Master list of test types)
# ==========================================
class DiagnosticTest(db.Model):
    __tablename__ = 'diagnostic_tests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g. "MRI", "CT Scan"
    category = db.Column(db.String(100))  # e.g. "Imaging", "Radiology"
    base_price = db.Column(db.Float, nullable=False, default=0.0)
    preparation_instructions = db.Column(db.Text)  # e.g. "Fasting for 4 hours..."
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<DiagnosticTest {self.name}>'


# ==========================================
# MACHINE (Radiology equipment)
# ==========================================
class Machine(db.Model):
    __tablename__ = 'machines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g. "MRI Machine 2"
    test_type = db.Column(db.String(100), nullable=False)  # which test category it handles
    room_number = db.Column(db.String(20))
    is_available = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Machine {self.name}>'


# ==========================================
# RADIOLOGIST (Specialist who performs/interprets scans)
# ==========================================
class Radiologist(db.Model):
    __tablename__ = 'radiologists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    specialization = db.Column(db.String(100))  # e.g. "MRI Specialist"

    user = db.relationship('User', backref='radiologist_profile', uselist=False)

    def __repr__(self):
        return f'<Radiologist {self.user.name if self.user else "Unknown"}>'


# ==========================================
# PRESCRIPTION (Uploaded doctor prescription for the test)
# ==========================================
class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # UUID-based stored filename
    original_filename = db.Column(db.String(255))  # original name for display
    file_type = db.Column(db.String(10))  # jpg, png, pdf
    extracted_text = db.Column(db.Text)  # OCR output
    verification_status = db.Column(db.String(30), default='pending_verification')
    # possible values: pending_verification, verified, rejected
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='prescriptions')

    def __repr__(self):
        return f'<Prescription {self.id} - {self.verification_status}>'


# ==========================================
# RADIOLOGY APPOINTMENT (Core booking record)
# ==========================================
class RadiologyAppointment(db.Model):
    __tablename__ = 'radiology_appointments'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(20), unique=True, nullable=False)  # e.g. "RAD-A1B2C3"
    token_number = db.Column(db.String(20))

    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('diagnostic_tests.id'), nullable=False)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)

    # Patient-provided contact/demographic info (may differ from account info)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    mobile_number = db.Column(db.String(20))
    email = db.Column(db.String(120))

    hospital_branch = db.Column(db.String(100))
    department = db.Column(db.String(100))
    preferred_date = db.Column(db.Date)
    preferred_time_slot = db.Column(db.String(50))
    remarks = db.Column(db.Text)

    # Assigned after admin approval
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=True)
    radiologist_id = db.Column(db.Integer, db.ForeignKey('radiologists.id'), nullable=True)
    scheduled_date = db.Column(db.Date, nullable=True)
    scheduled_time = db.Column(db.String(20), nullable=True)
    room_number = db.Column(db.String(20), nullable=True)

    status = db.Column(db.String(30), default='request_submitted')
    # possible values: request_submitted, prescription_verified, payment_completed,
    #                   pending_approval, approved, rejected, slot_assigned,
    #                   test_completed, report_ready, collected

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient = db.relationship('Patient', backref='radiology_appointments')
    test = db.relationship('DiagnosticTest', backref='appointments')
    prescription = db.relationship('Prescription', backref='radiology_appointment', uselist=False)
    machine = db.relationship('Machine', backref='appointments')
    radiologist = db.relationship('Radiologist', backref='appointments')

    def __repr__(self):
        return f'<RadiologyAppointment {self.booking_id} - {self.status}>'


# ==========================================
# PAYMENT (Simulated payment tracking)
# ==========================================
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    radiology_appointment_id = db.Column(db.Integer, db.ForeignKey('radiology_appointments.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    transaction_id = db.Column(db.String(50))  # simulated fake transaction ID
    paid_at = db.Column(db.DateTime)
    appointment = db.relationship('RadiologyAppointment', backref=db.backref('payment', uselist=False))
   

    def __repr__(self):
        return f'<Payment {self.id} - {self.status}>'


# ==========================================
# INVOICE (Generated bill)
# ==========================================
class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(30), unique=True, nullable=False)
    radiology_appointment_id = db.Column(db.Integer, db.ForeignKey('radiology_appointments.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship('RadiologyAppointment', backref=db.backref('invoice', uselist=False))

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


# ==========================================
# REPORT (Final diagnostic report from radiologist)
# ==========================================
class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    radiology_appointment_id = db.Column(db.Integer, db.ForeignKey('radiology_appointments.id'), nullable=False)
    findings = db.Column(db.Text)
    filename = db.Column(db.String(255))  # uploaded report file (PDF/image)
    uploaded_by_radiologist_id = db.Column(db.Integer, db.ForeignKey('radiologists.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship('RadiologyAppointment', backref=db.backref('report', uselist=False))

    def __repr__(self):
        return f'<Report {self.id}>' 
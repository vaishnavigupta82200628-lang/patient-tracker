from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app.models import Appointment, MedicalRecord, SymptomLog, Doctor, Patient
from app.utils import role_required

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# ==========================================
# HELPER: Serialize objects to JSON-friendly dicts
# ==========================================
def appointment_to_dict(appt):
    return {
        'id': appt.id,
        'patient_name': appt.patient.user.name,
        'doctor_name': appt.doctor.user.name,
        'date_time': appt.date_time.strftime('%Y-%m-%d %H:%M'),
        'status': appt.status,
        'reason': appt.reason
    }


def record_to_dict(record):
    return {
        'id': record.id,
        'patient_name': record.patient.user.name,
        'doctor_name': record.doctor.user.name,
        'diagnosis': record.diagnosis,
        'prescription': record.prescription,
        'created_at': record.created_at.strftime('%Y-%m-%d')
    }


# ==========================================
# APPOINTMENTS API
# ==========================================
@api_bp.route('/appointments', methods=['GET'])
@login_required
def get_appointments():
    """
    Returns appointments scoped to the logged-in user's role:
    - Admin sees all appointments
    - Doctor sees only their own
    - Patient sees only their own
    """
    if current_user.role == 'admin':
        appointments = Appointment.query.all()

    elif current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()

    elif current_user.role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        appointments = Appointment.query.filter_by(patient_id=patient.id).all()

    else:
        return jsonify({'error': 'Unknown role'}), 400

    return jsonify({
        'count': len(appointments),
        'appointments': [appointment_to_dict(a) for a in appointments]
    }), 200


@api_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@login_required
def get_single_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    # Authorization check: make sure this user is allowed to see this appointment
    if current_user.role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            return jsonify({'error': 'Forbidden'}), 403

    elif current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor or appointment.doctor_id != doctor.id:
            return jsonify({'error': 'Forbidden'}), 403

    # Admins can view any appointment (no extra check needed)

    return jsonify(appointment_to_dict(appointment)), 200


# ==========================================
# MEDICAL RECORDS API
# ==========================================
@api_bp.route('/records', methods=['GET'])
@login_required
def get_records():
    if current_user.role == 'admin':
        records = MedicalRecord.query.all()

    elif current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        records = MedicalRecord.query.filter_by(doctor_id=doctor.id).all() if doctor else []

    elif current_user.role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        records = MedicalRecord.query.filter_by(patient_id=patient.id).all() if patient else []

    else:
        return jsonify({'error': 'Unknown role'}), 400

    return jsonify({
        'count': len(records),
        'records': [record_to_dict(r) for r in records]
    }), 200


# ==========================================
# ADMIN-ONLY: SYSTEM STATS API
# ==========================================
@api_bp.route('/stats', methods=['GET'])
@login_required
@role_required('admin')
def get_system_stats():
    return jsonify({
        'total_doctors': Doctor.query.count(),
        'total_patients': Patient.query.count(),
        'total_appointments': Appointment.query.count(),
        'pending_appointments': Appointment.query.filter_by(status='pending').count(),
        'approved_appointments': Appointment.query.filter_by(status='approved').count(),
        'completed_appointments': Appointment.query.filter_by(status='completed').count(),
        'total_records': MedicalRecord.query.count(),
        'total_symptom_logs': SymptomLog.query.count()
    }), 200
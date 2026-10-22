from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models import Appointment, MedicalRecord, SymptomLog, Doctor, Patient, Payment, Review
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

    if current_user.role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            return jsonify({'error': 'Forbidden'}), 403

    elif current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor or appointment.doctor_id != doctor.id:
            return jsonify({'error': 'Forbidden'}), 403

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


# ==========================================
# ANALYTICS API
# ==========================================
@api_bp.route('/analytics/revenue', methods=['GET'])
@login_required
@role_required('admin')
def get_revenue_analytics():
    payments = Payment.query.filter_by(status='paid').all()

    revenue_by_month = {}
    for p in payments:
        if p.paid_at:
            month_key = p.paid_at.strftime('%Y-%m')
            revenue_by_month[month_key] = revenue_by_month.get(month_key, 0) + p.amount

    sorted_months = sorted(revenue_by_month.keys())

    return jsonify({
        'total_revenue': sum(revenue_by_month.values()),
        'total_transactions': len(payments),
        'labels': sorted_months,
        'values': [revenue_by_month[m] for m in sorted_months]
    }), 200


@api_bp.route('/analytics/disease-trends', methods=['GET'])
@login_required
@role_required('admin')
def get_disease_trends():
    logs = SymptomLog.query.filter(SymptomLog.predicted_disease.isnot(None)).all()

    disease_counts = {}
    for log in logs:
        disease_counts[log.predicted_disease] = disease_counts.get(log.predicted_disease, 0) + 1

    sorted_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return jsonify({
        'labels': [d[0] for d in sorted_diseases],
        'values': [d[1] for d in sorted_diseases]
    }), 200


@api_bp.route('/analytics/top-doctors', methods=['GET'])
@login_required
@role_required('admin')
def get_top_doctors():
    results = db.session.query(
        Doctor.id,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).join(Review, Review.doctor_id == Doctor.id).group_by(Doctor.id).order_by(func.avg(Review.rating).desc()).limit(5).all()

    doctors_data = []
    for doctor_id, avg_rating, review_count in results:
        doctor = Doctor.query.get(doctor_id)
        doctors_data.append({
            'name': doctor.user.name,
            'specialization': doctor.specialization or 'General',
            'avg_rating': round(avg_rating, 1),
            'review_count': review_count
        })

    return jsonify({'doctors': doctors_data}), 200
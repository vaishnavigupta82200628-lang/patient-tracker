from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models import Patient, Doctor, Appointment, MedicalRecord, SymptomLog
from app.utils import role_required, generate_pdf_report, create_notification
from app.ai.symptom_analyzer import extract_symptoms
from app.ai.disease_predictor import predict_disease

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


def get_current_patient():
    """Helper function: gets the Patient profile linked to the logged-in User."""
    return Patient.query.filter_by(user_id=current_user.id).first()


@patient_bp.route('/dashboard')
@login_required
@role_required('patient')
def dashboard():
    patient = get_current_patient()

    total_appointments = Appointment.query.filter_by(patient_id=patient.id).count()
    upcoming_count = Appointment.query.filter_by(patient_id=patient.id, status='approved').count()
    total_records = MedicalRecord.query.filter_by(patient_id=patient.id).count()

    return render_template(
        'patient/dashboard.html',
        patient=patient,
        total_appointments=total_appointments,
        upcoming_count=upcoming_count,
        total_records=total_records
    )


@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def profile():
    patient = get_current_patient()

    if request.method == 'POST':
        age_value = request.form.get('age')
        patient.age = int(age_value) if age_value else None
        patient.gender = request.form.get('gender')
        patient.blood_group = request.form.get('blood_group')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('patient.profile'))

    return render_template('patient/profile.html', patient=patient)


@patient_bp.route('/appointments')
@login_required
@role_required('patient')
def appointments():
    patient = get_current_patient()
    all_appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.date_time.desc()).all()
    return render_template('patient/appointments.html', appointments=all_appointments)


@patient_bp.route('/records')
@login_required
@role_required('patient')
def records():
    patient = get_current_patient()
    all_records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.created_at.desc()).all()
    return render_template('patient/records.html', records=all_records)


@patient_bp.route('/book-appointment', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def book_appointment():
    patient = get_current_patient()

    # Get distinct list of specializations from doctors who have set one
    specializations = db.session.query(Doctor.specialization)\
        .filter(Doctor.specialization.isnot(None))\
        .filter(Doctor.specialization != '')\
        .distinct().all()
    specializations = [s[0] for s in specializations]  # unpack from list of tuples

    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date_str = request.form.get('date_time')
        reason = request.form.get('reason')

        if not doctor_id or not date_str:
            flash('Please select a doctor and date/time.', 'danger')
            return render_template('patient/book_appointment.html', specializations=specializations)

        # Convert the string from the HTML datetime-local input into a Python datetime object
        appointment_datetime = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')

        # Validation: appointment must be in the future
        if appointment_datetime < datetime.now():
            flash('You cannot book an appointment in the past. Please select a future date and time.', 'danger')
            return render_template('patient/book_appointment.html', specializations=specializations)

        new_appointment = Appointment(
            patient_id=patient.id,
            doctor_id=int(doctor_id),
            date_time=appointment_datetime,
            reason=reason,
            status='pending'
        )
        db.session.add(new_appointment)
        db.session.commit()

        doctor_obj = Doctor.query.get(int(doctor_id))
        create_notification(
            user_id=doctor_obj.user_id,
            message=f"New appointment request from {current_user.name} on "
                    f"{appointment_datetime.strftime('%d %b, %I:%M %p')}."
        )

        flash('Appointment request submitted! Waiting for doctor approval.', 'success')
        return redirect(url_for('patient.appointments'))

    return render_template('patient/book_appointment.html', specializations=specializations)


# ==========================================
# MINI REST API — returns doctors as JSON
# ==========================================
@patient_bp.route('/api/doctors')
@login_required
@role_required('patient')
def api_doctors_by_specialization():
    specialization = request.args.get('specialization')

    if not specialization:
        return jsonify([])

    doctors = Doctor.query.filter_by(specialization=specialization).all()

    doctors_list = [
        {'id': doc.id, 'name': doc.user.name, 'qualification': doc.qualification}
        for doc in doctors
    ]
    return jsonify(doctors_list)


@patient_bp.route('/symptom-checker', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def symptom_checker():
    if request.method == 'POST':
        symptoms_text = request.form.get('symptoms_text', '').strip()

        if not symptoms_text:
            flash('Please describe your symptoms.', 'warning')
            return render_template('patient/symptom_checker.html')

        extracted = extract_symptoms(symptoms_text)
        predicted_disease, confidence = predict_disease(extracted)

        patient = get_current_patient()
        new_log = SymptomLog(
            patient_id=patient.id,
            symptoms_text=symptoms_text,
            predicted_disease=predicted_disease,
            confidence_score=confidence
        )
        db.session.add(new_log)
        db.session.commit()

        return render_template(
            'patient/symptom_result.html',
            symptoms_text=symptoms_text,
            extracted_symptoms=extracted,
            predicted_disease=predicted_disease,
            confidence=confidence,
            log_id=new_log.id
        )

    return render_template('patient/symptom_checker.html')


@patient_bp.route('/records/download-pdf')
@login_required
@role_required('patient')
def download_records_pdf():
    patient = get_current_patient()
    records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.created_at.desc()).all()

    headers = ['Date', 'Doctor', 'Diagnosis', 'Prescription']
    rows = [
        [
            r.created_at.strftime('%d %b %Y'),
            f"Dr. {r.doctor.user.name}",
            r.diagnosis or '-',
            r.prescription or '-'
        ]
        for r in records
    ]

    pdf_buffer = generate_pdf_report(
        title="Medical Records Report",
        subtitle=f"Patient: {current_user.name}",
        headers=headers,
        rows=rows if rows else [['-', '-', 'No records found', '-']]
    )

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"medical_records_{current_user.name.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )
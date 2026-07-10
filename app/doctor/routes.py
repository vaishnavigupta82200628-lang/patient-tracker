from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models import Doctor, Appointment, Patient, MedicalRecord, Review
from app.utils import role_required, generate_pdf_report, create_notification, generate_csv

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')


def get_current_doctor():
    """Helper function: gets the Doctor profile linked to the logged-in User."""
    return Doctor.query.filter_by(user_id=current_user.id).first()


@doctor_bp.route('/dashboard')
@login_required
@role_required('doctor')
def dashboard():
    doctor = get_current_doctor()

    total_appointments = Appointment.query.filter_by(doctor_id=doctor.id).count()
    pending_count = Appointment.query.filter_by(doctor_id=doctor.id, status='pending').count()
    approved_count = Appointment.query.filter_by(doctor_id=doctor.id, status='approved').count()
    completed_count = Appointment.query.filter_by(doctor_id=doctor.id, status='completed').count()

    avg_rating_result = db.session.query(func.avg(Review.rating)).filter_by(doctor_id=doctor.id).scalar()
    avg_rating = round(avg_rating_result, 1) if avg_rating_result else None
    total_reviews = Review.query.filter_by(doctor_id=doctor.id).count()

    return render_template(
        'doctor/dashboard.html',
        doctor=doctor,
        total_appointments=total_appointments,
        pending_count=pending_count,
        approved_count=approved_count,
        completed_count=completed_count,
        avg_rating=avg_rating,
        total_reviews=total_reviews
    )


@doctor_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def profile():
    doctor = get_current_doctor()

    if request.method == 'POST':
        doctor.specialization = request.form.get('specialization')
        doctor.qualification = request.form.get('qualification')
        doctor.availability = request.form.get('availability')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('doctor.profile'))

    return render_template('doctor/profile.html', doctor=doctor)


@doctor_bp.route('/appointments')
@login_required
@role_required('doctor')
def appointments():
    doctor = get_current_doctor()
    all_appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.date_time.desc()).all()
    return render_template('doctor/appointments.html', appointments=all_appointments)


@doctor_bp.route('/appointments/update/<int:appointment_id>/<string:new_status>', methods=['POST'])
@login_required
@role_required('doctor')
def update_appointment_status(appointment_id, new_status):
    doctor = get_current_doctor()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != doctor.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('doctor.appointments'))

    valid_statuses = ['approved', 'rejected', 'completed']
    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('doctor.appointments'))

    appointment.status = new_status
    db.session.commit()

    if new_status in ['approved', 'rejected']:
        create_notification(
            user_id=appointment.patient.user_id,
            message=f"Your appointment with Dr. {doctor.user.name} on "
                    f"{appointment.date_time.strftime('%d %b, %I:%M %p')} was {new_status}."
        )

    flash(f'Appointment marked as {new_status}.', 'success')
    return redirect(url_for('doctor.appointments'))


@doctor_bp.route('/appointments/<int:appointment_id>/add-record', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def add_record(appointment_id):
    doctor = get_current_doctor()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != doctor.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('doctor.appointments'))

    if appointment.status != 'completed':
        flash('You can only add records for completed appointments.', 'warning')
        return redirect(url_for('doctor.appointments'))

    existing_record = MedicalRecord.query.filter_by(appointment_id=appointment.id).first()
    if existing_record:
        flash('A record already exists for this appointment.', 'info')
        return redirect(url_for('doctor.appointments'))

    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')

        new_record = MedicalRecord(
            patient_id=appointment.patient_id,
            doctor_id=doctor.id,
            appointment_id=appointment.id,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes
        )
        db.session.add(new_record)
        db.session.commit()

        create_notification(
            user_id=appointment.patient.user_id,
            message=f"Dr. {doctor.user.name} added a new medical record for your visit on "
                    f"{appointment.date_time.strftime('%d %b')}."
        )

        flash('Medical record added successfully!', 'success')
        return redirect(url_for('doctor.appointments'))

    return render_template('doctor/add_record.html', appointment=appointment)


@doctor_bp.route('/appointments/download-pdf')
@login_required
@role_required('doctor')
def download_appointments_pdf():
    doctor = get_current_doctor()
    all_appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.date_time.desc()).all()

    headers = ['Date & Time', 'Patient', 'Status', 'Reason']
    rows = [
        [
            a.date_time.strftime('%d %b %Y, %I:%M %p'),
            a.patient.user.name,
            a.status.capitalize(),
            a.reason or '-'
        ]
        for a in all_appointments
    ]

    pdf_buffer = generate_pdf_report(
        title="Appointments Report",
        subtitle=f"Doctor: Dr. {current_user.name}",
        headers=headers,
        rows=rows if rows else [['-', 'No appointments found', '-', '-']]
    )

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"appointments_{current_user.name.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )


@doctor_bp.route('/appointments/export-csv')
@login_required
@role_required('doctor')
def export_appointments_csv():
    doctor = get_current_doctor()
    all_appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.date_time.desc()).all()

    headers = ['Date & Time', 'Patient', 'Status', 'Reason']
    rows = [
        [a.date_time.strftime('%d %b %Y, %I:%M %p'), a.patient.user.name, a.status.capitalize(), a.reason or '-']
        for a in all_appointments
    ]

    csv_buffer = generate_csv(headers, rows)
    return send_file(
        csv_buffer,
        as_attachment=True,
        download_name='my_appointments.csv',
        mimetype='text/csv'
    )
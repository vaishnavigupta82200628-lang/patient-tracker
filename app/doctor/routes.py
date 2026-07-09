from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Doctor, Appointment, Patient, MedicalRecord   # ← MedicalRecord add kiya
from app.utils import role_required

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

    return render_template(
        'doctor/dashboard.html',
        doctor=doctor,
        total_appointments=total_appointments,
        pending_count=pending_count,
        approved_count=approved_count,
        completed_count=completed_count
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

    # Security check: make sure this appointment actually belongs to this doctor
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('doctor.appointments'))

    valid_statuses = ['approved', 'rejected', 'completed']
    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('doctor.appointments'))

    appointment.status = new_status
    db.session.commit()
    flash(f'Appointment marked as {new_status}.', 'success')
    return redirect(url_for('doctor.appointments'))
@doctor_bp.route('/appointments/<int:appointment_id>/add-record', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def add_record(appointment_id):
    doctor = get_current_doctor()
    appointment = Appointment.query.get_or_404(appointment_id)

    # Security check: appointment must belong to this doctor
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('doctor.appointments'))

    # Business rule check: can only add records for completed appointments
    if appointment.status != 'completed':
        flash('You can only add records for completed appointments.', 'warning')
        return redirect(url_for('doctor.appointments'))

    # Check if a record already exists for this appointment
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

        flash('Medical record added successfully!', 'success')
        return redirect(url_for('doctor.appointments'))

    return render_template('doctor/add_record.html', appointment=appointment)
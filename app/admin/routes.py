from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models import User, Doctor, Patient, Appointment, MedicalRecord, RadiologyAppointment, Machine, Radiologist
from app.utils import role_required, generate_csv, create_notification

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='pending').count()

    return render_template(
        'admin/dashboard.html',
        total_doctors=total_doctors,
        total_patients=total_patients,
        total_appointments=total_appointments,
        pending_appointments=pending_appointments
    )


@admin_bp.route('/doctors')
@login_required
@role_required('admin')
def manage_doctors():
    doctors = Doctor.query.all()
    return render_template('admin/manage_doctors.html', doctors=doctors)


@admin_bp.route('/doctors/delete/<int:doctor_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    user = User.query.get(doctor.user_id)

    db.session.delete(doctor)
    if user:
        db.session.delete(user)
    db.session.commit()

    flash('Doctor removed successfully.', 'success')
    return redirect(url_for('admin.manage_doctors'))


@admin_bp.route('/patients')
@login_required
@role_required('admin')
def manage_patients():
    patients = Patient.query.all()
    return render_template('admin/manage_patients.html', patients=patients)


@admin_bp.route('/doctors/export-csv')
@login_required
@role_required('admin')
def export_doctors_csv():
    doctors = Doctor.query.all()

    headers = ['Name', 'Email', 'Specialization', 'Qualification', 'Availability']
    rows = [
        [d.user.name, d.user.email, d.specialization or '-', d.qualification or '-', d.availability or '-']
        for d in doctors
    ]

    csv_buffer = generate_csv(headers, rows)
    return send_file(
        csv_buffer,
        as_attachment=True,
        download_name='doctors_list.csv',
        mimetype='text/csv'
    )


@admin_bp.route('/patients/export-csv')
@login_required
@role_required('admin')
def export_patients_csv():
    patients = Patient.query.all()

    headers = ['Name', 'Email', 'Age', 'Gender', 'Blood Group']
    rows = [
        [p.user.name, p.user.email, p.age or '-', p.gender or '-', p.blood_group or '-']
        for p in patients
    ]

    csv_buffer = generate_csv(headers, rows)
    return send_file(
        csv_buffer,
        as_attachment=True,
        download_name='patients_list.csv',
        mimetype='text/csv'
    )

@admin_bp.route('/radiology-requests')
@login_required
@role_required('admin')
def radiology_requests():
    status_filter = request.args.get('status', 'all')

    query = RadiologyAppointment.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    requests_list = query.order_by(RadiologyAppointment.created_at.desc()).all()

    return render_template('admin/radiology_requests.html', requests_list=requests_list, status_filter=status_filter)


@admin_bp.route('/radiology-requests/<int:appointment_id>')
@login_required
@role_required('admin')
def radiology_request_detail(appointment_id):
    appointment = RadiologyAppointment.query.get_or_404(appointment_id)

    # Machines matching this test type, for the assignment dropdown
    matching_machines = Machine.query.filter_by(test_type=appointment.test.name, is_available=True).all()
    radiologists = Radiologist.query.all()

    return render_template(
        'admin/radiology_request_detail.html',
        appointment=appointment,
        matching_machines=matching_machines,
        radiologists=radiologists
    )


@admin_bp.route('/radiology-requests/<int:appointment_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_radiology_request(appointment_id):
    appointment = RadiologyAppointment.query.get_or_404(appointment_id)

    machine_id = request.form.get('machine_id')
    radiologist_id = request.form.get('radiologist_id')
    scheduled_date = request.form.get('scheduled_date')
    scheduled_time = request.form.get('scheduled_time')
    room_number = request.form.get('room_number')

    if not all([machine_id, radiologist_id, scheduled_date, scheduled_time, room_number]):
        flash('Please fill in all slot assignment fields.', 'danger')
        return redirect(url_for('admin.radiology_request_detail', appointment_id=appointment_id))

    appointment.machine_id = int(machine_id)
    appointment.radiologist_id = int(radiologist_id)
    appointment.scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
    appointment.scheduled_time = scheduled_time
    appointment.room_number = room_number
    appointment.status = 'slot_assigned'

    db.session.commit()

    create_notification(
        user_id=appointment.patient.user_id,
        message=f"Your {appointment.test.name} appointment has been approved and scheduled for "
                f"{scheduled_date} at {scheduled_time}, Room {room_number}."
    )

    flash('Appointment approved and slot assigned successfully!', 'success')
    return redirect(url_for('admin.radiology_requests'))


@admin_bp.route('/radiology-requests/<int:appointment_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def reject_radiology_request(appointment_id):
    appointment = RadiologyAppointment.query.get_or_404(appointment_id)
    appointment.status = 'rejected'
    db.session.commit()

    create_notification(
        user_id=appointment.patient.user_id,
        message=f"Your {appointment.test.name} appointment request was rejected. Please contact the hospital for more information."
    )

    flash('Appointment request rejected.', 'info')
    return redirect(url_for('admin.radiology_requests'))


@admin_bp.route('/radiology-requests/<int:appointment_id>/request-new-prescription', methods=['POST'])
@login_required
@role_required('admin')
def request_new_prescription(appointment_id):
    appointment = RadiologyAppointment.query.get_or_404(appointment_id)
    appointment.status = 'request_submitted'
    appointment.prescription.verification_status = 'rejected'
    db.session.commit()

    create_notification(
        user_id=appointment.patient.user_id,
        message=f"Your prescription for {appointment.test.name} could not be verified. Please upload a new, clearer prescription."
    )

    flash('Patient has been asked to re-upload their prescription.', 'info')
    return redirect(url_for('admin.radiology_requests'))

@admin_bp.route('/radiologists', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def manage_radiologists():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        specialization = request.form.get('specialization')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'warning')
            return redirect(url_for('admin.manage_radiologists'))

        new_user = User(name=name, email=email, role='radiologist')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        new_radiologist = Radiologist(user_id=new_user.id, specialization=specialization)
        db.session.add(new_radiologist)
        db.session.commit()

        flash(f'Radiologist Dr. {name} added successfully!', 'success')
        return redirect(url_for('admin.manage_radiologists'))

    radiologists = Radiologist.query.all()
    return render_template('admin/manage_radiologists.html', radiologists=radiologists)
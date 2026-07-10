from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user

from app.extensions import db
from app.models import User, Doctor, Patient, Appointment, MedicalRecord
from app.utils import role_required, generate_csv

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
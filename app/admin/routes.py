from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import User, Doctor, Patient, Appointment, MedicalRecord
from app.utils import role_required

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
        db.session.delete(user)  # Deletes the linked User account too
    db.session.commit()

    flash('Doctor removed successfully.', 'success')
    return redirect(url_for('admin.manage_doctors'))


@admin_bp.route('/patients')
@login_required
@role_required('admin')
def manage_patients():
    patients = Patient.query.all()
    return render_template('admin/manage_patients.html', patients=patients)
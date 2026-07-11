from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Radiologist, RadiologyAppointment, Report
from app.utils import role_required, create_notification

radiologist_bp = Blueprint('radiologist', __name__, url_prefix='/radiologist')


def get_current_radiologist():
    return Radiologist.query.filter_by(user_id=current_user.id).first()


@radiologist_bp.route('/dashboard')
@login_required
@role_required('radiologist')
def dashboard():
    radiologist = get_current_radiologist()

    if not radiologist:
        flash('Radiologist profile not found. Please contact admin.', 'danger')
        return redirect(url_for('main.home'))

    upcoming = RadiologyAppointment.query.filter_by(
        radiologist_id=radiologist.id, status='slot_assigned'
    ).order_by(RadiologyAppointment.scheduled_date).all()

    completed_count = RadiologyAppointment.query.filter_by(
        radiologist_id=radiologist.id, status='report_ready'
    ).count()

    return render_template(
        'radiologist/dashboard.html',
        radiologist=radiologist,
        upcoming=upcoming,
        completed_count=completed_count
    )


@radiologist_bp.route('/appointment/<int:appointment_id>/upload-report', methods=['GET', 'POST'])
@login_required
@role_required('radiologist')
def upload_report(appointment_id):
    radiologist = get_current_radiologist()
    appointment = RadiologyAppointment.query.get_or_404(appointment_id)

    if appointment.radiologist_id != radiologist.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('radiologist.dashboard'))

    if request.method == 'POST':
        findings = request.form.get('findings')

        new_report = Report(
            radiology_appointment_id=appointment.id,
            findings=findings,
            uploaded_by_radiologist_id=radiologist.id
        )
        db.session.add(new_report)

        appointment.status = 'report_ready'
        db.session.commit()

        create_notification(
            user_id=appointment.patient.user_id,
            message=f"Your {appointment.test.name} report is ready. Please check your dashboard."
        )

        flash('Report uploaded successfully!', 'success')
        return redirect(url_for('radiologist.dashboard'))

    return render_template('radiologist/upload_report.html', appointment=appointment)
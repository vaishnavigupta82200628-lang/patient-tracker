import os
import uuid
import random
import string
import qrcode
from io import BytesIO
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Patient, DiagnosticTest, Prescription, RadiologyAppointment, Payment, Invoice
from app.utils import role_required, generate_pdf_report
from app.radiology.ocr_utils import extract_text_from_file, check_diagnostic_keywords

radiology_bp = Blueprint('radiology', __name__, url_prefix='/radiology')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def get_current_patient():
    return Patient.query.filter_by(user_id=current_user.id).first()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_booking_id():
    """Generates a unique, human-readable booking ID like RAD-A1B2C3"""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"RAD-{random_part}"


def generate_token_number():
    """Generates a short daily token number"""
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"TKN-{random_part}"


def generate_invoice_number():
    random_part = ''.join(random.choices(string.digits, k=8))
    return f"INV-{random_part}"


@radiology_bp.route('/book-test', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def book_test():
    tests = DiagnosticTest.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        mobile_number = request.form.get('mobile_number')
        email = request.form.get('email')
        hospital_branch = request.form.get('hospital_branch')
        department = request.form.get('department')
        test_id = request.form.get('test_id')
        preferred_date = request.form.get('preferred_date')
        preferred_time_slot = request.form.get('preferred_time_slot')
        remarks = request.form.get('remarks')

        if not all([full_name, age, gender, mobile_number, test_id, preferred_date, preferred_time_slot]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('radiology/book_test.html', tests=tests)

        session['radiology_booking'] = {
            'full_name': full_name,
            'age': age,
            'gender': gender,
            'mobile_number': mobile_number,
            'email': email,
            'hospital_branch': hospital_branch,
            'department': department,
            'test_id': test_id,
            'preferred_date': preferred_date,
            'preferred_time_slot': preferred_time_slot,
            'remarks': remarks
        }

        flash('Details saved! Now please upload your doctor\'s prescription.', 'success')
        return redirect(url_for('radiology.upload_prescription'))

    return render_template('radiology/book_test.html', tests=tests)


@radiology_bp.route('/upload-prescription', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def upload_prescription():
    if 'radiology_booking' not in session:
        flash('Please fill in the booking details first.', 'warning')
        return redirect(url_for('radiology.book_test'))

    if request.method == 'POST':
        if 'prescription_file' not in request.files:
            flash('Please select a file to upload.', 'danger')
            return render_template('radiology/upload_prescription.html')

        file = request.files['prescription_file']

        if file.filename == '':
            flash('No file selected.', 'danger')
            return render_template('radiology/upload_prescription.html')

        if not allowed_file(file.filename):
            flash('Invalid file type. Only JPG, PNG, and PDF are allowed.', 'danger')
            return render_template('radiology/upload_prescription.html')

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > MAX_FILE_SIZE_BYTES:
            flash('File is too large. Maximum size allowed is 10 MB.', 'danger')
            return render_template('radiology/upload_prescription.html')

        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)

        extracted_text = extract_text_from_file(upload_path, file_extension)
        keywords_found = check_diagnostic_keywords(extracted_text)

        verification_status = 'verified' if keywords_found else 'pending_verification'

        patient = get_current_patient()
        new_prescription = Prescription(
            patient_id=patient.id,
            filename=unique_filename,
            original_filename=original_filename,
            file_type=file_extension,
            extracted_text=extracted_text,
            verification_status=verification_status
        )
        db.session.add(new_prescription)
        db.session.commit()

        session['radiology_booking']['prescription_id'] = new_prescription.id
        session.modified = True

        if keywords_found:
            flash(f'Prescription uploaded and verified! Detected: {", ".join(keywords_found)}', 'success')
        else:
            flash('Prescription uploaded. It will be manually verified by our staff.', 'info')

        return redirect(url_for('radiology.payment'))

    return render_template('radiology/upload_prescription.html')


@radiology_bp.route('/payment', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def payment():
    if 'radiology_booking' not in session or 'prescription_id' not in session.get('radiology_booking', {}):
        flash('Please complete the previous steps first.', 'warning')
        return redirect(url_for('radiology.book_test'))

    booking_data = session['radiology_booking']
    test = DiagnosticTest.query.get(int(booking_data['test_id']))

    if request.method == 'POST':
        card_number = request.form.get('card_number')
        if not card_number or len(card_number.replace(' ', '')) < 12:
            flash('Please enter a valid card number.', 'danger')
            return render_template('radiology/payment.html', test=test)

        patient = get_current_patient()

        new_appointment = RadiologyAppointment(
            booking_id=generate_booking_id(),
            token_number=generate_token_number(),
            patient_id=patient.id,
            test_id=test.id,
            prescription_id=booking_data['prescription_id'],
            full_name=booking_data['full_name'],
            age=int(booking_data['age']),
            gender=booking_data['gender'],
            mobile_number=booking_data['mobile_number'],
            email=booking_data.get('email'),
            hospital_branch=booking_data['hospital_branch'],
            department=booking_data.get('department'),
            preferred_date=datetime.strptime(booking_data['preferred_date'], '%Y-%m-%d').date(),
            preferred_time_slot=booking_data['preferred_time_slot'],
            remarks=booking_data.get('remarks'),
            status='pending_approval'
        )
        db.session.add(new_appointment)
        db.session.commit()

        new_payment = Payment(
            radiology_appointment_id=new_appointment.id,
            amount=test.base_price,
            status='paid',
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            paid_at=datetime.utcnow()
        )
        db.session.add(new_payment)

        new_invoice = Invoice(
            invoice_number=generate_invoice_number(),
            radiology_appointment_id=new_appointment.id,
            amount=test.base_price
        )
        db.session.add(new_invoice)
        db.session.commit()

        session.pop('radiology_booking', None)

        flash('Payment successful! Your appointment request has been submitted for approval.', 'success')
        return redirect(url_for('radiology.confirmation', appointment_id=new_appointment.id))

    return render_template('radiology/payment.html', test=test)


@radiology_bp.route('/confirmation/<int:appointment_id>')
@login_required
@role_required('patient')
def confirmation(appointment_id):
    patient = get_current_patient()
    appointment = RadiologyAppointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('patient.dashboard'))

    return render_template('radiology/confirmation.html', appointment=appointment)


@radiology_bp.route('/appointment/<int:appointment_id>/qr-code')
@login_required
@role_required('patient')
def generate_qr_code(appointment_id):
    appointment = RadiologyAppointment.query.get_or_404(appointment_id)

    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(f"Booking ID: {appointment.booking_id} | Patient: {appointment.full_name}")
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return send_file(buffer, mimetype='image/png')


@radiology_bp.route('/appointment/<int:appointment_id>/receipt-pdf')
@login_required
@role_required('patient')
def download_receipt_pdf(appointment_id):
    patient = get_current_patient()
    appointment = RadiologyAppointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('patient.my_diagnostic_tests'))

    headers = ['Field', 'Details']
    rows = [
        ['Booking ID', appointment.booking_id],
        ['Token Number', appointment.token_number or '-'],
        ['Patient Name', appointment.full_name],
        ['Test', appointment.test.name],
        ['Preferred Date', appointment.preferred_date.strftime('%d %b %Y')],
        ['Status', appointment.status.replace('_', ' ').title()],
    ]

    if appointment.status == 'slot_assigned':
        rows += [
            ['Machine', appointment.machine.name],
            ['Radiologist', f"Dr. {appointment.radiologist.user.name}"],
            ['Scheduled Date', appointment.scheduled_date.strftime('%d %b %Y')],
            ['Scheduled Time', appointment.scheduled_time],
            ['Room Number', appointment.room_number],
        ]

    if appointment.payment:
        rows += [
            ['Amount Paid', f"₹{appointment.payment.amount}"],
            ['Transaction ID', appointment.payment.transaction_id],
        ]

    pdf_buffer = generate_pdf_report(
        title="Diagnostic Test Appointment Receipt",
        subtitle=f"Booking ID: {appointment.booking_id}",
        headers=headers,
        rows=rows
    )

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"receipt_{appointment.booking_id}.pdf",
        mimetype='application/pdf'
    )
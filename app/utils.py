from functools import wraps
from flask import abort
from flask_login import current_user
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime


def role_required(*roles):
    """
    Custom decorator to restrict access based on user role.
    Usage: @role_required('admin')  or  @role_required('admin', 'doctor')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_pdf_report(title, subtitle, headers, rows):
    """
    Generic PDF report generator.
    - title: main heading (e.g. "Medical Records Report")
    - subtitle: smaller text under title (e.g. patient name)
    - headers: list of column names for the table
    - rows: list of lists, each inner list is one table row
    Returns a BytesIO buffer containing the PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # ---- Header ----
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=20, textColor=colors.HexColor('#0d6efd'))
    elements.append(Paragraph("🏥 Patient Tracker", title_style))
    elements.append(Paragraph(title, styles['Heading2']))
    elements.append(Paragraph(subtitle, styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))

    # ---- Table ----
    table_data = [headers] + rows
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)

    # ---- Footer ----
    elements.append(Spacer(1, 0.4 * inch))
    footer_text = f"Generated on {datetime.now().strftime('%d %b %Y, %I:%M %p')} | Patient Tracker System"
    elements.append(Paragraph(footer_text, styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer
from app.models import Notification
from app.extensions import db


def create_notification(user_id, message):
    """Creates a notification for a specific user. Call this whenever a notify-worthy event happens."""
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()
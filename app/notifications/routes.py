from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
@login_required
def view_all():
    all_notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).all()

    # Mark all as read when the user views this page
    unread = [n for n in all_notifications if not n.is_read]
    for n in unread:
        n.is_read = True
    if unread:
        db.session.commit()

    return render_template('notifications/list.html', notifications=all_notifications)
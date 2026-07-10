from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models import User, Doctor, Patient
from app.auth.forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please login instead.', 'warning')
            return redirect(url_for('auth.login'))

        # Create new User
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()  # commit here to generate new_user.id

        # Create the linked role-specific profile
        if form.role.data == 'doctor':
            doctor_profile = Doctor(user_id=new_user.id)
            db.session.add(doctor_profile)
        elif form.role.data == 'patient':
            patient_profile = Patient(user_id=new_user.id)
            db.session.add(patient_profile)

        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')

            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor.dashboard'))
            elif user.role == 'patient':
                return redirect(url_for('patient.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Step 1: Verify current password is correct
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')

        # Step 2: Check new password meets minimum requirements
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'danger')
            return render_template('auth/change_password.html')

        # Step 3: Check new password and confirmation match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')

        # Step 4: Make sure new password is actually different
        if current_user.check_password(new_password):
            flash('New password must be different from your current password.', 'warning')
            return render_template('auth/change_password.html')

        # All checks passed — update the password
        current_user.set_password(new_password)
        db.session.commit()

        flash('Password changed successfully! Please log in again.', 'success')
        logout_user()
        return redirect(url_for('auth.login'))

    return render_template('auth/change_password.html')
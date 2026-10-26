from urllib.parse import urlsplit
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User
from forms.auth_forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)


def is_safe_url(target: str) -> bool:
    """Validate that target URL is a safe local redirect."""
    if not target:
        return False
    ref_url = urlsplit(request.host_url)
    test_url = urlsplit(target)
    return test_url.scheme in ('', 'http', 'https') and \
           (not test_url.netloc or ref_url.netloc == test_url.netloc)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User account registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created successfully! Please sign in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User authentication and session establishment."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter(User.email.ilike(email)).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.full_name}!', 'success')

            next_page = request.args.get('next')
            if not is_safe_url(next_page):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid email or password. Please verify your credentials.', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Terminate current user session securely."""
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))

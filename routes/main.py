from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, FileRecord
from forms.auth_forms import ChangePasswordForm
from forms.file_forms import FileUploadForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Application landing router."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main user dashboard presenting storage metrics, recent files, and quick actions."""
    # Storage calculations
    storage_used_bytes = current_user.get_storage_used_bytes()
    storage_quota_bytes = current_user.get_storage_quota_bytes()
    storage_percentage = current_user.get_storage_percentage()

    # File counts
    total_files = FileRecord.query.filter_by(user_id=current_user.id).count()

    # Recent files (last 5)
    recent_files = FileRecord.query.filter_by(user_id=current_user.id)\
        .order_by(FileRecord.uploaded_at.desc())\
        .limit(5)\
        .all()

    # Category breakdown
    category_query = db.session.query(
        FileRecord.category,
        func.count(FileRecord.id).label('count'),
        func.coalesce(func.sum(FileRecord.file_size), 0).label('size')
    ).filter(FileRecord.user_id == current_user.id)\
     .group_by(FileRecord.category)\
     .all()

    category_stats = {
        'document': {'count': 0, 'size': 0, 'formatted_size': '0 B'},
        'spreadsheet': {'count': 0, 'size': 0, 'formatted_size': '0 B'},
        'presentation': {'count': 0, 'size': 0, 'formatted_size': '0 B'},
        'image': {'count': 0, 'size': 0, 'formatted_size': '0 B'},
        'archive': {'count': 0, 'size': 0, 'formatted_size': '0 B'},
        'media': {'count': 0, 'size': 0, 'formatted_size': '0 B'},
        'other': {'count': 0, 'size': 0, 'formatted_size': '0 B'},
    }

    for cat, count, size in category_query:
        if cat in category_stats:
            category_stats[cat]['count'] = count
            category_stats[cat]['size'] = size
            category_stats[cat]['formatted_size'] = current_user._format_bytes(size)

    upload_form = FileUploadForm()

    return render_template(
        'dashboard.html',
        total_files=total_files,
        storage_used_bytes=storage_used_bytes,
        storage_quota_bytes=storage_quota_bytes,
        storage_used_formatted=current_user.get_formatted_storage_used(),
        storage_quota_formatted=current_user.get_formatted_storage_quota(),
        storage_percentage=storage_percentage,
        recent_files=recent_files,
        category_stats=category_stats,
        upload_form=upload_form
    )


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management and security settings."""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password entered is incorrect.', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            try:
                db.session.commit()
                flash('Your password has been updated successfully.', 'success')
                return redirect(url_for('main.profile'))
            except Exception:
                db.session.rollback()
                flash('An unexpected error occurred while updating your password.', 'danger')

    total_files = FileRecord.query.filter_by(user_id=current_user.id).count()

    return render_template(
        'profile.html',
        form=form,
        total_files=total_files,
        storage_used_formatted=current_user.get_formatted_storage_used(),
        storage_quota_formatted=current_user.get_formatted_storage_quota(),
        storage_percentage=current_user.get_storage_percentage()
    )


@main_bp.route('/about')
def about():
    """CloudVault project architecture, features, and Azure integration overview."""
    return render_template('about.html')

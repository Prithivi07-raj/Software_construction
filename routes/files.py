import os
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, send_file, current_app, jsonify, abort
)
from flask_login import login_required, current_user
from sqlalchemy import desc, asc
from werkzeug.utils import secure_filename

from models import db, FileRecord
from services.storage_service import get_storage_service, StorageFileNotFoundError
from forms.file_forms import FileUploadForm, DeleteFileForm

files_bp = Blueprint('files', __name__, url_prefix='/files')


def is_allowed_file(filename: str) -> bool:
    """Validate filename has an allowed extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', set())
    return ext in allowed


@files_bp.route('', methods=['GET'])
@files_bp.route('/', methods=['GET'])
@login_required
def list_files():
    """
    Search, filter, sort, and display authenticated user's files
    with support for Grid and List views.
    """
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', 'all').strip().lower()
    sort_by = request.args.get('sort_by', 'date').strip().lower()
    sort_order = request.args.get('order', 'desc').strip().lower()
    active_view = request.args.get('view', 'grid').strip().lower()

    if active_view not in ('grid', 'list'):
        active_view = 'grid'

    # Base query strictly filtered to current user
    query = FileRecord.query.filter_by(user_id=current_user.id)

    # Search filter
    if search_query:
        query = query.filter(FileRecord.original_filename.ilike(f"%{search_query}%"))

    # Category filter
    if category_filter and category_filter != 'all':
        query = query.filter_by(category=category_filter)

    # Sorting logic
    sort_column_map = {
        'name': FileRecord.original_filename,
        'date': FileRecord.uploaded_at,
        'size': FileRecord.file_size
    }
    sort_col = sort_column_map.get(sort_by, FileRecord.uploaded_at)
    if sort_order == 'asc':
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    files = query.all()

    upload_form = FileUploadForm()
    delete_form = DeleteFileForm()

    return render_template(
        'files.html',
        files=files,
        search_query=search_query,
        category_filter=category_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        active_view=active_view,
        total_count=len(files),
        upload_form=upload_form,
        delete_form=delete_form,
        storage_used_formatted=current_user.get_formatted_storage_used(),
        storage_quota_formatted=current_user.get_formatted_storage_quota(),
        storage_percentage=current_user.get_storage_percentage()
    )


@files_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """
    Handle single or multiple file uploads via standard POST or drag-and-drop AJAX.
    Enforces file extension whitelisting, quota checking, and path isolation.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              request.accept_mimetypes.best == 'application/json'

    # Check if a file was submitted
    if 'file' not in request.files:
        error_msg = "No file selected for upload."
        if is_ajax:
            return jsonify({'success': False, 'message': error_msg}), 400
        flash(error_msg, 'danger')
        return redirect(url_for('files.list_files'))

    uploaded_file = request.files['file']

    if not uploaded_file or uploaded_file.filename.strip() == '':
        error_msg = "No file selected for upload."
        if is_ajax:
            return jsonify({'success': False, 'message': error_msg}), 400
        flash(error_msg, 'danger')
        return redirect(url_for('files.list_files'))

    original_name = uploaded_file.filename.strip()

    # Sanitize and validate extension
    if not is_allowed_file(original_name):
        allowed_list = ", ".join(sorted(current_app.config.get('ALLOWED_EXTENSIONS', set())))
        error_msg = f"File type not allowed. Permitted formats: {allowed_list}"
        if is_ajax:
            return jsonify({'success': False, 'message': error_msg}), 400
        flash(error_msg, 'danger')
        return redirect(url_for('files.list_files'))

    # Calculate content length / file size
    uploaded_file.seek(0, os.SEEK_END)
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)

    # Max upload limit check
    max_limit = current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
    if file_size > max_limit:
        error_msg = f"File exceeds the maximum upload limit of {max_limit / (1024 * 1024):.0f} MB."
        if is_ajax:
            return jsonify({'success': False, 'message': error_msg}), 400
        flash(error_msg, 'danger')
        return redirect(url_for('files.list_files'))

    # User storage quota check
    storage_used = current_user.get_storage_used_bytes()
    storage_quota = current_user.get_storage_quota_bytes()
    if (storage_used + file_size) > storage_quota:
        error_msg = "Storage quota exceeded. Please delete some files before uploading new ones."
        if is_ajax:
            return jsonify({'success': False, 'message': error_msg}), 400
        flash(error_msg, 'danger')
        return redirect(url_for('files.list_files'))

    # Save to storage service
    storage_svc = get_storage_service(current_app)
    stored_filename, ext = storage_svc.generate_stored_filename(original_name)

    try:
        bytes_saved = storage_svc.save_file(
            user_id=current_user.id,
            file_stream=uploaded_file.stream,
            stored_filename=stored_filename
        )

        # Categorize
        category = FileRecord.categorize_extension(ext)
        mime_type = uploaded_file.content_type or 'application/octet-stream'

        # Record in database
        file_record = FileRecord(
            user_id=current_user.id,
            original_filename=secure_filename(original_name) or original_name,
            stored_filename=stored_filename,
            file_size=bytes_saved,
            file_extension=ext.lstrip('.'),
            mime_type=mime_type,
            category=category
        )
        db.session.add(file_record)
        db.session.commit()

        success_msg = f'"{file_record.original_filename}" uploaded successfully!'
        if is_ajax:
            return jsonify({
                'success': True,
                'message': success_msg,
                'file': file_record.to_dict()
            }), 201
        
        flash(success_msg, 'success')
        return redirect(url_for('files.list_files'))

    except Exception as e:
        db.session.rollback()
        # Clean up disk file if database commit failed
        storage_svc.delete_file(current_user.id, stored_filename)
        error_msg = "Failed to complete upload due to a server error."
        if is_ajax:
            return jsonify({'success': False, 'message': error_msg}), 500
        flash(error_msg, 'danger')
        return redirect(url_for('files.list_files'))


@files_bp.route('/<int:file_id>/download', methods=['GET'])
@login_required
def download_file(file_id: int):
    """
    Download a file securely.
    Verifies user ownership before serving from local storage.
    """
    file_record = FileRecord.query.filter_by(id=file_id, user_id=current_user.id).first()
    if not file_record:
        abort(404, description="File not found or access denied.")

    storage_svc = get_storage_service(current_app)
    try:
        file_stream = storage_svc.get_file_stream(
            current_user.id, file_record.stored_filename
        )
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=file_record.original_filename,
            mimetype=file_record.mime_type
        )
    except StorageFileNotFoundError:
        abort(404, description="File content not found in storage.")


@files_bp.route('/<int:file_id>/preview', methods=['GET'])
@login_required
def preview_file(file_id: int):
    """
    Inline preview for images, documents, and text files.
    Verifies user ownership before rendering.
    """
    file_record = FileRecord.query.filter_by(id=file_id, user_id=current_user.id).first()
    if not file_record:
        abort(404, description="File not found or access denied.")

    storage_svc = get_storage_service(current_app)
    try:
        file_stream = storage_svc.get_file_stream(
            current_user.id, file_record.stored_filename
        )
        return send_file(
            file_stream,
            as_attachment=False,
            download_name=file_record.original_filename,
            mimetype=file_record.mime_type
        )
    except StorageFileNotFoundError:
        abort(404, description="File content not found in storage.")


@files_bp.route('/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_file(file_id: int):
    """
    Delete a file permanently.
    Ensures user ownership before removing from disk and database.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              request.accept_mimetypes.best == 'application/json'

    file_record = FileRecord.query.filter_by(id=file_id, user_id=current_user.id).first()
    if not file_record:
        if is_ajax:
            return jsonify({'success': False, 'message': 'File not found or unauthorized.'}), 404
        flash('File not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('files.list_files'))

    filename = file_record.original_filename
    stored_name = file_record.stored_filename

    try:
        # Delete from disk
        storage_svc = get_storage_service(current_app)
        storage_svc.delete_file(current_user.id, stored_name)

        # Delete from database
        db.session.delete(file_record)
        db.session.commit()

        success_msg = f'"{filename}" has been permanently deleted.'
        if is_ajax:
            return jsonify({'success': True, 'message': success_msg}), 200

        flash(success_msg, 'success')
        return redirect(request.referrer or url_for('files.list_files'))

    except Exception:
        db.session.rollback()
        error_msg = "An error occurred while deleting the file."
        if is_ajax:
            return jsonify({'success': False, 'message': error_msg}), 500
        flash(error_msg, 'danger')
        return redirect(url_for('files.list_files'))


@files_bp.route('/stats', methods=['GET'])
@login_required
def stats_api():
    """Return JSON statistics for current user's storage usage."""
    return jsonify({
        'total_files': FileRecord.query.filter_by(user_id=current_user.id).count(),
        'used_bytes': current_user.get_storage_used_bytes(),
        'used_formatted': current_user.get_formatted_storage_used(),
        'quota_bytes': current_user.get_storage_quota_bytes(),
        'quota_formatted': current_user.get_formatted_storage_quota(),
        'percentage': current_user.get_storage_percentage()
    })

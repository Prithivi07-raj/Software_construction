import io
from models import db, FileRecord


def test_upload_file_success(auth_client, app, test_user):
    """Test file upload saves file to disk and creates FileRecord."""
    dummy_data = b"Hello, CloudVault Secure Storage!"
    data = {
        'file': (io.BytesIO(dummy_data), 'project_notes.txt')
    }

    response = auth_client.post('/files/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b"uploaded successfully" in response.data

    with app.app_context():
        record = FileRecord.query.filter_by(user_id=test_user.id).first()
        assert record is not None
        assert record.original_filename == 'project_notes.txt'
        assert record.file_size == len(dummy_data)
        assert record.category == 'document'


def test_upload_ajax(auth_client, app, test_user):
    """Test AJAX upload returns JSON payload with file metadata."""
    dummy_data = b"AJAX Upload test data"
    data = {
        'file': (io.BytesIO(dummy_data), 'document.pdf')
    }

    response = auth_client.post(
        '/files/upload',
        data=data,
        content_type='multipart/form-data',
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['success'] is True
    assert json_data['file']['original_filename'] == 'document.pdf'
    assert json_data['file']['category'] == 'document'


def test_upload_disallowed_extension(auth_client):
    """Test upload rejects unsafe executable or unauthorized extensions."""
    data = {
        'file': (io.BytesIO(b"malicious code"), 'exploit.exe')
    }

    response = auth_client.post(
        '/files/upload',
        data=data,
        content_type='multipart/form-data',
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['success'] is False
    assert "File type not allowed" in json_data['message']


def test_download_file(auth_client, app, test_user):
    """Test file download delivers original content and headers."""
    dummy_data = b"Confidential Report Content"
    data = {
        'file': (io.BytesIO(dummy_data), 'report.pdf')
    }
    auth_client.post('/files/upload', data=data, content_type='multipart/form-data')

    with app.app_context():
        file_rec = FileRecord.query.filter_by(user_id=test_user.id, original_filename='report.pdf').first()
        assert file_rec is not None
        file_id = file_rec.id

    download_resp = auth_client.get(f'/files/{file_id}/download')
    assert download_resp.status_code == 200
    assert download_resp.data == dummy_data
    assert 'attachment' in download_resp.headers.get('Content-Disposition', '')


def test_file_ownership_isolation(client, app, test_user, test_user2):
    """
    CRITICAL SECURITY TEST:
    Verify User Two (Bob) cannot access, download, or delete User One (Alice)'s file.
    """
    # 1. Login as Alice and upload file
    client.post('/login', data={'email': 'alice@example.com', 'password': 'SecurePass123!'}, follow_redirects=True)
    alice_data = b"Alice Secret Diary"
    client.post('/files/upload', data={'file': (io.BytesIO(alice_data), 'alice_secret.txt')}, content_type='multipart/form-data')

    with app.app_context():
        alice_file = FileRecord.query.filter_by(user_id=test_user.id).first()
        assert alice_file is not None
        alice_file_id = alice_file.id

    # 2. Logout Alice and Login as Bob
    client.get('/logout', follow_redirects=True)
    client.post('/login', data={'email': 'bob@example.com', 'password': 'SecurePass456!'}, follow_redirects=True)

    # 3. Bob attempts to download Alice's file -> MUST BE REJECTED (404 / access denied)
    unauthorized_download = client.get(f'/files/{alice_file_id}/download')
    assert unauthorized_download.status_code == 404

    # 4. Bob attempts to preview Alice's file -> MUST BE REJECTED (404)
    unauthorized_preview = client.get(f'/files/{alice_file_id}/preview')
    assert unauthorized_preview.status_code == 404

    # 5. Bob attempts to delete Alice's file -> MUST BE REJECTED (404)
    unauthorized_delete = client.post(
        f'/files/{alice_file_id}/delete',
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )
    assert unauthorized_delete.status_code == 404

    # Verify Alice's file is still safe in database
    with app.app_context():
        still_there = db.session.get(FileRecord, alice_file_id)
        assert still_there is not None
        assert still_there.original_filename == 'alice_secret.txt'


def test_delete_file_success(auth_client, app, test_user):
    """Test authorized user can delete their own file."""
    # Upload
    dummy_data = b"File to be deleted"
    auth_client.post('/files/upload', data={'file': (io.BytesIO(dummy_data), 'delete_me.txt')}, content_type='multipart/form-data')

    with app.app_context():
        record = FileRecord.query.filter_by(user_id=test_user.id, original_filename='delete_me.txt').first()
        assert record is not None
        file_id = record.id

    # Delete via AJAX
    response = auth_client.post(
        f'/files/{file_id}/delete',
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True

    # Confirm removed from database
    with app.app_context():
        deleted_record = db.session.get(FileRecord, file_id)
        assert deleted_record is None


def test_search_and_filter(auth_client, app, test_user):
    """Test search query and category filtering."""
    # Upload 2 files: one document, one image via AJAX to avoid session flash message pollution
    auth_client.post(
        '/files/upload',
        data={'file': (io.BytesIO(b"Doc content"), 'thesis.docx')},
        content_type='multipart/form-data',
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )
    auth_client.post(
        '/files/upload',
        data={'file': (io.BytesIO(b"Img content"), 'vacation.png')},
        content_type='multipart/form-data',
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )

    # Search for "thesis"
    search_resp = auth_client.get('/files/?q=thesis')
    assert search_resp.status_code == 200
    assert b"thesis.docx" in search_resp.data
    assert b"vacation.png" not in search_resp.data

    # Filter by category "image"
    filter_resp = auth_client.get('/files/?category=image')
    assert filter_resp.status_code == 200
    assert b"vacation.png" in filter_resp.data
    assert b"thesis.docx" not in filter_resp.data

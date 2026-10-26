import os
import shutil
import tempfile
import pytest
from app import create_app
from models import db, User, FileRecord


@pytest.fixture(scope='session')
def temp_storage():
    """Create a temporary storage folder for tests and clean up after."""
    temp_dir = tempfile.mkdtemp(prefix="cloudvault_test_storage_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def app(temp_storage):
    """Create application in testing mode with temporary storage."""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'UPLOAD_FOLDER': temp_storage,
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create primary test user."""
    with app.app_context():
        user = User(
            full_name="Alice Developer",
            email="alice@example.com"
        )
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()
        # Refresh from DB
        user_id = user.id
        user_obj = db.session.get(User, user_id)
        return user_obj


@pytest.fixture
def test_user2(app):
    """Create second test user to test user isolation and authorization."""
    with app.app_context():
        user = User(
            full_name="Bob Security",
            email="bob@example.com"
        )
        user.set_password("SecurePass456!")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return db.session.get(User, user_id)


@pytest.fixture
def auth_client(client, test_user):
    """Client authenticated as test_user."""
    client.post('/login', data={
        'email': 'alice@example.com',
        'password': 'SecurePass123!'
    }, follow_redirects=True)
    return client

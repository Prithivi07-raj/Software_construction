from models import User


def test_register_success(client, app):
    """Test standard user registration succeeds and creates database record."""
    response = client.post('/register', data={
        'full_name': 'Charlie Smith',
        'email': 'charlie@example.com',
        'password': 'StrongPassword123',
        'confirm_password': 'StrongPassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Your account has been created successfully" in response.data

    with app.app_context():
        user = User.query.filter_by(email='charlie@example.com').first()
        assert user is not None
        assert user.full_name == 'Charlie Smith'
        assert user.check_password('StrongPassword123') is True
        # Ensure password is not stored in plaintext
        assert user.password_hash != 'StrongPassword123'


def test_register_duplicate_email(client, test_user):
    """Test duplicate registration is prevented."""
    response = client.post('/register', data={
        'full_name': 'Another Alice',
        'email': 'alice@example.com',  # already exists from fixture
        'password': 'Password123',
        'confirm_password': 'Password123'
    })

    assert response.status_code == 200
    assert b"An account with this email address already exists" in response.data


def test_register_password_mismatch(client):
    """Test registration rejects mismatched password confirmation."""
    response = client.post('/register', data={
        'full_name': 'Mismatch Test',
        'email': 'mismatch@example.com',
        'password': 'Password123',
        'confirm_password': 'DifferentPassword123'
    })

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data


def test_login_success(client, test_user):
    """Test valid user login establishes session."""
    response = client.post('/login', data={
        'email': 'alice@example.com',
        'password': 'SecurePass123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back, Alice Developer" in response.data
    assert b"Sign Out" in response.data or b"Sign out" in response.data


def test_login_invalid_password(client, test_user):
    """Test login rejects invalid password."""
    response = client.post('/login', data={
        'email': 'alice@example.com',
        'password': 'WrongPassword999!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_logout(auth_client):
    """Test user logout terminates authenticated session."""
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out securely" in response.data

    # Attempting to access dashboard should now redirect to login
    dash_resp = auth_client.get('/dashboard')
    assert dash_resp.status_code == 302
    assert '/login' in dash_resp.headers['Location']


def test_protected_routes_require_login(client):
    """Test protected endpoints redirect anonymous visitors."""
    endpoints = ['/dashboard', '/files/', '/profile']
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

from app.models import User

def test_password_hashing(app):
    user = User(username='test_hash', email='hash@test.edu', role='student')
    user.set_password('mysecretpass')
    assert user.password_hash != 'mysecretpass'
    assert user.check_password('mysecretpass') is True
    assert user.check_password('wrongpass') is False

def test_user_roles(app):
    faculty = User(username='fac', email='fac@test.edu', role='faculty')
    student = User(username='stu', email='stu@test.edu', role='student')
    assert faculty.is_faculty() is True
    assert faculty.is_student() is False
    assert student.is_faculty() is False
    assert student.is_student() is True

def test_login_and_logout(client):
    # Valid login
    res = client.post('/login', data={'identifier': 'test_faculty', 'password': 'pass123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome back, test_faculty!" in res.data

    # Logout
    res = client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
    assert b"logged out" in res.data

    # Invalid login
    res = client.post('/login', data={'identifier': 'test_faculty', 'password': 'incorrect_password'}, follow_redirects=True)
    assert b"Invalid username/email or password." in res.data

def test_role_authorization_protection(client):
    # Log in as student
    client.post('/login', data={'identifier': 'test_student', 'password': 'pass123'}, follow_redirects=True)

    # Attempt to access faculty-only project creation
    res = client.get('/projects/create', follow_redirects=True)
    assert b"Access denied. This page is restricted to faculty members." in res.data

    # Attempt to access settings
    res = client.get('/settings', follow_redirects=True)
    assert b"Access denied." in res.data

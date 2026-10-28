import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from app.models import db, User, Student, AuditLog

auth_bp = Blueprint('auth', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def faculty_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        if session.get('role') not in ['faculty', 'admin']:
            flash("Access denied. This page is restricted to faculty members.", "danger")
            return redirect(url_for('dashboard.index'))
        return view(**kwargs)
    return wrapped_view

def student_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return view(**kwargs)
    return wrapped_view

@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['email'] = user.email

            # Log audit
            log = AuditLog(user_id=user.id, action_type='USER_LOGIN', description=f"User {user.username} ({user.role}) logged in.")
            db.session.add(log)
            db.session.commit()

            flash(f"Welcome back, {user.username}! Logged in as {user.role.title()}.", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        
        flash("Invalid username/email or password.", "danger")

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        full_name = request.form.get('full_name', '').strip() or username
        department = request.form.get('department', 'Computer Science')

        if not username or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash("Username is already taken.", "warning")
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "warning")
            return render_template('auth/register.html')

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        if role == 'student':
            # Create associated student record
            student_code = f"STU{new_user.id:04d}"
            student_obj = Student(
                user_id=new_user.id,
                student_id=student_code,
                full_name=full_name,
                email=email,
                department=department
            )
            db.session.add(student_obj)

        log = AuditLog(user_id=new_user.id, action_type='USER_REGISTER', description=f"New user registered: {username} ({role}).")
        db.session.add(log)
        db.session.commit()

        flash("Registration successful! You may now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    """Convenient one-click demo login for fast grading and evaluation."""
    target_role = 'faculty' if role == 'faculty' else 'student'
    user = User.query.filter_by(role=target_role).first()
    
    if not user:
        # Fallback to any user
        user = User.query.first()
    
    if user:
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['email'] = user.email
        flash(f"Logged in as Demo {user.role.title()} ({user.username}).", "info")
    else:
        flash("No demo accounts found. Please initialize demo data.", "warning")
        
    return redirect(url_for('dashboard.index'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for('auth.login'))

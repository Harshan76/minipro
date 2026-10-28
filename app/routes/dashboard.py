from flask import Blueprint, render_template, g, redirect, url_for
from app.models import db, Student, Project, Team, TeamGenerationRun, AuditLog
from app.routes.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def root():
    if not g.user:
        return redirect(url_for('auth.login'))
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # If logged in as student, display student personalized overview
    if g.user.is_student():
        student = g.user.student_profile
        comp_pct, missing_fields = student.calculate_completion_score() if student else (0, [])
        
        # Check if student is assigned to any teams
        assigned_memberships = student.team_memberships if student else []
        active_projects = Project.query.filter_by(status='Active').all()

        return render_template('dashboard/student_dashboard.html',
                               student=student,
                               comp_pct=comp_pct,
                               missing_fields=missing_fields,
                               assigned_memberships=assigned_memberships,
                               active_projects=active_projects)

    # Faculty / Admin Dashboard
    total_students = Student.query.count()
    total_projects = Project.query.count()
    total_teams = Team.query.count()
    
    # Calculate students awaiting assignment across active projects
    # For the default/latest project, count unassigned students
    latest_project = Project.query.order_by(Project.created_at.desc()).first()
    pending_students_count = 0
    if latest_project and total_students > 0:
        latest_run = latest_project.generation_runs[0] if latest_project.generation_runs else None
        if latest_run:
            assigned_ids = db.session.query(Team.id).filter_by(generation_run_id=latest_run.id).all()
            pending_students_count = latest_run.metrics.get('unassigned_count', 0)
        else:
            pending_students_count = total_students
    else:
        pending_students_count = total_students

    recent_runs = TeamGenerationRun.query.order_by(TeamGenerationRun.created_at.desc()).limit(5).all()
    recent_activities = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(8).all()
    projects = Project.query.order_by(Project.created_at.desc()).all()

    return render_template('dashboard/index.html',
                           total_students=total_students,
                           total_projects=total_projects,
                           total_teams=total_teams,
                           pending_students_count=pending_students_count,
                           recent_runs=recent_runs,
                           recent_activities=recent_activities,
                           projects=projects,
                           latest_project=latest_project)

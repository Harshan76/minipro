from flask import Blueprint, render_template, request, g, redirect, url_for, flash
from app.models import db, Project, Student, Team, TeamGenerationRun, AuditLog
from app.routes.auth import faculty_required

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit')
@faculty_required
def index():
    project = Project.query.order_by(Project.created_at.desc()).first()
    if not project:
        flash("Create a project to view the Allocation Audit.", "info")
        return redirect(url_for('projects.create'))
    return redirect(url_for('audit.project_audit', project_id=project.id))

@audit_bp.route('/projects/<int:project_id>/audit')
@faculty_required
def project_audit(project_id):
    project = Project.query.get_or_404(project_id)
    all_projects = Project.query.order_by(Project.title).all()
    all_students = Student.query.all()

    latest_run = TeamGenerationRun.query.filter_by(project_id=project.id).order_by(TeamGenerationRun.created_at.desc()).first()

    assigned_student_ids = set()
    teams = []
    unassigned_details = []
    size_compliance = []

    if latest_run:
        teams = Team.query.filter_by(generation_run_id=latest_run.id).all()
        for t in teams:
            sz = len(t.members)
            is_valid = (sz >= (project.min_team_size or 3) and sz <= (project.max_team_size or 5))
            size_compliance.append({
                'team_name': t.name,
                'size': sz,
                'min': project.min_team_size,
                'max': project.max_team_size,
                'status': 'Compliant' if is_valid else 'Non-compliant',
                'reason': 'Within bounds' if is_valid else f"Team size {sz} outside permitted range [{project.min_team_size}-{project.max_team_size}]"
            })
            for m in t.members:
                assigned_student_ids.add(m.student_id)

    # Detailed reason analysis for unassigned students
    for s in all_students:
        if s.id not in assigned_student_ids:
            reasons = []
            if s.experience_months < (project.min_experience_months or 0):
                reasons.append(f"Experience ({s.experience_months} mos) is below project minimum ({project.min_experience_months} mos).")
            if s.available_hours_per_week < (project.min_availability_hours or 0):
                reasons.append(f"Availability ({s.available_hours_per_week}h/week) is below project minimum ({project.min_availability_hours}h/week).")
            if not reasons:
                reasons.append(f"Cohort remainder: Total eligible students ({len(all_students)}) does not divide evenly by target team size ({project.preferred_team_size}).")

            unassigned_details.append({
                'student': s,
                'reasons': reasons
            })

    # Manual faculty changes history
    manual_edits = AuditLog.query.filter(AuditLog.action_type.in_(['MANUAL_STUDENT_MOVE', 'RUN_APPROVED', 'SIMULATION_APPLIED'])).order_by(AuditLog.timestamp.desc()).limit(20).all()

    # All generation runs history
    run_history = TeamGenerationRun.query.filter_by(project_id=project.id).order_by(TeamGenerationRun.created_at.desc()).all()

    return render_template('audit/index.html',
                           project=project,
                           all_projects=all_projects,
                           latest_run=latest_run,
                           unassigned_details=unassigned_details,
                           size_compliance=size_compliance,
                           manual_edits=manual_edits,
                           run_history=run_history)

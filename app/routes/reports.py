import csv
import io
from flask import Blueprint, render_template, make_response, redirect, url_for, flash, g
from app.models import db, Project, Team, TeamGenerationRun, TeamMember
from app.routes.auth import login_required, faculty_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    runs = TeamGenerationRun.query.order_by(TeamGenerationRun.created_at.desc()).all()
    return render_template('reports/index.html', projects=projects, runs=runs)

@reports_bp.route('/export/teams-csv/<int:run_id>')
@faculty_required
def export_teams_csv(run_id):
    gen_run = TeamGenerationRun.query.get_or_404(run_id)
    teams = Team.query.filter_by(generation_run_id=run_id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Project ID', 'Project Title', 'Formation Method', 'Run Status',
        'Team Name', 'Overall Score', 'Skill Coverage (%)', 'Role Coverage (%)',
        'Student ID', 'Student Name', 'Student Email', 'Department',
        'Assigned Role', 'Cluster Archetype', 'Experience (Months)', 'Available Hours/Week'
    ])

    for t in teams:
        for m in t.members:
            s = m.student
            writer.writerow([
                gen_run.project_id,
                gen_run.project.title,
                gen_run.method,
                gen_run.status,
                t.name,
                t.overall_score,
                t.skill_coverage_pct,
                t.role_coverage_pct,
                s.student_id,
                s.full_name,
                s.email,
                s.department,
                m.assigned_role,
                m.cluster_label,
                s.experience_months,
                s.available_hours_per_week
            ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f"attachment; filename=team_allocations_run_{run_id}.csv"
    response.headers['Content-type'] = 'text/csv; charset=utf-8'
    return response

@reports_bp.route('/export/summary-csv/<int:project_id>')
@faculty_required
def export_summary_csv(project_id):
    project = Project.query.get_or_404(project_id)
    runs = TeamGenerationRun.query.filter_by(project_id=project.id).order_by(TeamGenerationRun.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Run ID', 'Method', 'Status', 'Is Approved', 'Teams Formed',
        'Assigned Students', 'Unassigned Students', 'Skill Coverage (%)',
        'Role Coverage (%)', 'Runtime (ms)', 'Created At'
    ])

    for r in runs:
        m = r.metrics
        writer.writerow([
            r.id,
            r.method,
            r.status,
            'Yes' if r.is_approved else 'No',
            m.get('teams_count', 0),
            m.get('assigned_count', 0),
            m.get('unassigned_count', 0),
            m.get('avg_skill_coverage', 0.0),
            m.get('avg_role_coverage', 0.0),
            m.get('runtime_ms', 0.0),
            r.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f"attachment; filename=project_{project_id}_summary.csv"
    response.headers['Content-type'] = 'text/csv; charset=utf-8'
    return response

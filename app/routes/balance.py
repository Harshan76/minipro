from flask import Blueprint, render_template, request, g, redirect, url_for, flash
from app.models import db, Project, Team, TeamGenerationRun
from app.algorithms.explainer import TeamExplainer
from app.routes.auth import login_required

balance_bp = Blueprint('balance', __name__)

@balance_bp.route('/balance')
@login_required
def balance_default():
    project = Project.query.order_by(Project.created_at.desc()).first()
    if not project:
        flash("Create a project to analyze team balance.", "info")
        return redirect(url_for('projects.create'))
    return redirect(url_for('balance.balance_project', project_id=project.id))

@balance_bp.route('/projects/<int:project_id>/balance')
@login_required
def balance_project(project_id):
    project = Project.query.get_or_404(project_id)
    all_projects = Project.query.order_by(Project.title).all()

    # Determine which run to inspect (latest approved or latest proposed)
    run_id = request.args.get('run_id')
    if run_id:
        active_run = TeamGenerationRun.query.get(run_id)
    else:
        active_run = TeamGenerationRun.query.filter_by(project_id=project.id).order_by(TeamGenerationRun.is_approved.desc(), TeamGenerationRun.created_at.desc()).first()

    team_analyses = []
    if active_run:
        teams = Team.query.filter_by(generation_run_id=active_run.id).all()
        for t in teams:
            team_dict = {
                'name': t.name,
                'members': [m.student for m in t.members],
                'member_records': [
                    {'student': m.student, 'cluster_id': m.student_cluster, 'cluster_label': m.cluster_label, 'centroid_distance': 1.0}
                    for m in t.members
                ],
                'member_roles': {m.student_id: m.assigned_role for m in t.members},
                'skill_coverage_pct': t.skill_coverage_pct,
                'technical_details': t.technical_details
            }
            explanation = TeamExplainer.explain_team(team_dict, project)

            # Analyze skill concentrations (duplicates)
            all_member_skills = []
            for m in t.members:
                for ss in m.student.skills:
                    all_member_skills.append(ss.skill.name)
            
            skill_counts = {}
            for sk in all_member_skills:
                skill_counts[sk] = skill_counts.get(sk, 0) + 1
            duplicates = [f"{sk} ({cnt} students)" for sk, cnt in skill_counts.items() if cnt >= 3]

            # Role coverage checklist
            req_roles = [pr.role_name for pr in project.required_roles]
            filled_roles = [m.assigned_role for m in t.members]
            role_checklist = []
            for rr in req_roles:
                is_filled = any(rr.lower() in fr.lower() or fr.lower() in rr.lower() for fr in filled_roles)
                role_checklist.append({'role': rr, 'status': 'Covered' if is_filled else 'Missing'})

            # Experience distribution
            exp_list = [m.student.experience_months for m in t.members]
            avg_exp = round(sum(exp_list) / len(exp_list), 1) if exp_list else 0

            team_analyses.append({
                'team': t,
                'members_count': len(t.members),
                'target_size': project.preferred_team_size,
                'covered_skills': explanation['covered_skills'],
                'missing_skills': explanation['missing_skills'],
                'role_checklist': role_checklist,
                'avg_experience_months': avg_exp,
                'duplicates': duplicates,
                'conflicts': explanation['availability_conflicts'],
                'shared_days': explanation['shared_days'],
                'suggestions': explanation['suggestions'],
                'overall_score': t.overall_score
            })

    return render_template('balance/index.html',
                           project=project,
                           all_projects=all_projects,
                           active_run=active_run,
                           team_analyses=team_analyses)

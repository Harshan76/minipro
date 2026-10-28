import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, g
from app.models import db, Student, Project, Team, TeamMember, TeamGenerationRun, ModelTrainingRun, AuditLog
from app.algorithms.traditional import TraditionalTeamBuilder
from app.algorithms.ml_cluster import MLTeamBuilder
from app.algorithms.explainer import TeamExplainer
from app.routes.auth import login_required, faculty_required

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/projects/<int:project_id>/generate', methods=['GET', 'POST'])
@faculty_required
def generate(project_id):
    project = Project.query.get_or_404(project_id)
    students = Student.query.all()

    if request.method == 'POST':
        method = request.form.get('method', 'traditional')  # 'traditional' or 'ai_clustering'
        
        # Collect weights if traditional
        weights = {
            'skill': float(request.form.get('weight_skill', current_app.config['WEIGHT_SKILL'])),
            'interest': float(request.form.get('weight_interest', current_app.config['WEIGHT_INTEREST'])),
            'experience': float(request.form.get('weight_experience', current_app.config['WEIGHT_EXPERIENCE'])),
            'availability': float(request.form.get('weight_availability', current_app.config['WEIGHT_AVAILABILITY'])),
            'role': float(request.form.get('weight_role', current_app.config['WEIGHT_ROLE']))
        }

        # Filter eligible students
        eligible_students = [s for s in students if s.experience_months >= (project.min_experience_months or 0)]
        if not eligible_students:
            eligible_students = students

        if method == 'traditional':
            builder = TraditionalTeamBuilder(weights=weights)
            result = builder.form_teams(eligible_students, project)
        else:
            builder = MLTeamBuilder(model_dir=current_app.config['MODEL_DIR'])
            result = builder.recommend_teams(eligible_students, project)

            # Record model training run in DB if clusters were computed
            if 'clustering_summary' in result:
                meta = result['metrics'].get('clustering_metadata', {})
                mtr = ModelTrainingRun(
                    n_clusters=meta.get('k', 4),
                    n_students=len(eligible_students),
                    inertia=meta.get('inertia', 0.0),
                    silhouette_score=meta.get('silhouette_score', 0.0),
                    cluster_summaries_json=json.dumps(result.get('clustering_summary', {}))
                )
                db.session.add(mtr)

        # Save TeamGenerationRun in DB
        gen_run = TeamGenerationRun(
            project_id=project.id,
            method=method,
            status='Proposed',
            parameters_json=json.dumps({'weights': weights, 'eligible_count': len(eligible_students)}),
            evaluation_metrics_json=json.dumps(result['metrics'])
        )
        db.session.add(gen_run)
        db.session.flush()

        # Save Teams and Team Members
        for t_data in result['teams']:
            team = Team(
                generation_run_id=gen_run.id,
                project_id=project.id,
                name=t_data['name'],
                overall_score=t_data['overall_score'],
                skill_coverage_pct=t_data['skill_coverage_pct'],
                role_coverage_pct=t_data['role_coverage_pct'],
                experience_score=t_data['experience_score'],
                availability_score=t_data['availability_score'],
                interest_score=t_data['interest_score'],
                explanation_narrative=t_data['explanation'],
                technical_details_json=json.dumps(t_data.get('technical_details', {}))
            )
            db.session.add(team)
            db.session.flush()

            roles_map = t_data.get('member_roles', {})
            member_recs = {r['student'].id: r for r in t_data.get('member_records', [])}

            for s_obj in t_data['members']:
                c_id = -1
                c_lbl = 'Generalist'
                if s_obj.id in member_recs:
                    c_id = member_recs[s_obj.id].get('cluster_id', -1)
                    c_lbl = member_recs[s_obj.id].get('cluster_label', 'Generalist')

                tm = TeamMember(
                    team_id=team.id,
                    student_id=s_obj.id,
                    assigned_role=roles_map.get(s_obj.id, 'Developer'),
                    student_cluster=c_id,
                    cluster_label=c_lbl,
                    fit_score=team.overall_score
                )
                db.session.add(tm)

        # Audit log
        action = 'TEAMS_GENERATED_TRADITIONAL' if method == 'traditional' else 'TEAMS_GENERATED_AI'
        log = AuditLog(
            user_id=g.user.id,
            action_type=action,
            description=f"Generated {len(result['teams'])} proposed teams for '{project.title}' using {method.title()} method."
        )
        db.session.add(log)
        db.session.commit()

        flash(f"Successfully generated teams using {result['metrics']['method_label']}!", "success")
        return redirect(url_for('teams.view_run', project_id=project.id, run_id=gen_run.id))

    return render_template('teams/generate.html',
                           project=project,
                           students_count=len(students),
                           weights=current_app.config)

@teams_bp.route('/projects/<int:project_id>/runs/<int:run_id>')
@login_required
def view_run(project_id, run_id):
    project = Project.query.get_or_404(project_id)
    gen_run = TeamGenerationRun.query.get_or_404(run_id)
    teams = Team.query.filter_by(generation_run_id=run_id).all()
    all_students = Student.query.all()
    
    assigned_student_ids = {m.student_id for t in teams for m in t.members}
    unassigned_students = [s for s in all_students if s.id not in assigned_student_ids]

    return render_template('teams/view_run.html',
                           project=project,
                           run=gen_run,
                           teams=teams,
                           unassigned_students=unassigned_students)

@teams_bp.route('/teams/<int:team_id>/why')
@login_required
def why_team(team_id):
    team = Team.query.get_or_404(team_id)
    project = team.project
    
    # Construct team dict for Explainer
    team_dict = {
        'name': team.name,
        'members': [m.student for m in team.members],
        'member_records': [
            {
                'student': m.student,
                'cluster_id': m.student_cluster,
                'cluster_label': m.cluster_label,
                'centroid_distance': 1.0
            } for m in team.members
        ],
        'member_roles': {m.student_id: m.assigned_role for m in team.members},
        'skill_coverage_pct': team.skill_coverage_pct,
        'technical_details': team.technical_details
    }
    explanation = TeamExplainer.explain_team(team_dict, project)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('json') == '1':
        return jsonify(explanation)

    return render_template('teams/why_modal.html', team=team, explanation=explanation)

@teams_bp.route('/teams/move-student', methods=['POST'])
@faculty_required
def move_student():
    """Allows faculty to manually reassign a student between teams."""
    student_id = int(request.form.get('student_id'))
    from_team_id = int(request.form.get('from_team_id'))
    to_team_id = int(request.form.get('to_team_id'))

    student = Student.query.get_or_404(student_id)
    from_team = Team.query.get_or_404(from_team_id)
    to_team = Team.query.get_or_404(to_team_id)

    # Remove from from_team
    membership = TeamMember.query.filter_by(team_id=from_team_id, student_id=student_id).first()
    if membership:
        db.session.delete(membership)
        
        # Add to to_team
        new_mem = TeamMember(
            team_id=to_team_id,
            student_id=student_id,
            assigned_role=student.roles_list[0] if student.roles_list else 'Developer',
            student_cluster=membership.student_cluster,
            cluster_label=membership.cluster_label,
            fit_score=to_team.overall_score
        )
        db.session.add(new_mem)
        
        from_team.status = 'Modified'
        to_team.status = 'Modified'

        # Log audit
        log = AuditLog(
            user_id=g.user.id,
            action_type='MANUAL_STUDENT_MOVE',
            description=f"Faculty manually moved {student.full_name} from {from_team.name} to {to_team.name}."
        )
        db.session.add(log)
        db.session.commit()

        flash(f"Moved {student.full_name} to {to_team.name}.", "success")
    else:
        flash("Student was not in the specified source team.", "warning")

    return redirect(request.referrer or url_for('teams.view_run', project_id=from_team.project_id, run_id=from_team.generation_run_id))

@teams_bp.route('/projects/<int:project_id>/approve-run/<int:run_id>', methods=['POST'])
@faculty_required
def approve_run(project_id, run_id):
    """Faculty approves and finalizes team assignments."""
    gen_run = TeamGenerationRun.query.get_or_404(run_id)
    gen_run.is_approved = True
    gen_run.status = 'Approved'
    gen_run.approved_at = datetime.utcnow()

    for t in gen_run.teams:
        t.status = 'Approved'

    log = AuditLog(
        user_id=g.user.id,
        action_type='RUN_APPROVED',
        description=f"Faculty finalized and approved team allocation run #{run_id} ({gen_run.method}) for project #{project_id}."
    )
    db.session.add(log)
    db.session.commit()

    flash(f"Team assignments finalized and approved! Students can now view their team allocations.", "success")
    return redirect(url_for('teams.view_run', project_id=project_id, run_id=run_id))

@teams_bp.route('/ai-recommendations')
@login_required
def ai_recommendations():
    """Requirement 8: AI-Powered Team Recommendations Deep-Dive page."""
    latest_run = ModelTrainingRun.query.order_by(ModelTrainingRun.trained_at.desc()).first()
    latest_ai_team_run = TeamGenerationRun.query.filter_by(method='ai_clustering').order_by(TeamGenerationRun.created_at.desc()).first()
    
    return render_template('teams/ai_recommendations.html',
                           model_run=latest_run,
                           team_run=latest_ai_team_run)

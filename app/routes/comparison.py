import json
from flask import Blueprint, render_template, request, g, redirect, url_for, flash, current_app
from app.models import db, Project, Student, TeamGenerationRun, Team
from app.algorithms.traditional import TraditionalTeamBuilder
from app.algorithms.ml_cluster import MLTeamBuilder
from app.algorithms.evaluator import TeamEvaluator
from app.routes.auth import login_required

comparison_bp = Blueprint('comparison', __name__)

@comparison_bp.route('/compare')
@login_required
def compare_default():
    project = Project.query.order_by(Project.created_at.desc()).first()
    if not project:
        flash("Please create a project first to compare methods.", "info")
        return redirect(url_for('projects.create'))
    return redirect(url_for('comparison.compare_project', project_id=project.id))

@comparison_bp.route('/projects/<int:project_id>/compare', methods=['GET', 'POST'])
@login_required
def compare_project(project_id):
    project = Project.query.get_or_404(project_id)
    all_projects = Project.query.order_by(Project.title).all()
    students = Student.query.all()

    # Look for existing runs for this project
    trad_run = TeamGenerationRun.query.filter_by(project_id=project.id, method='traditional').order_by(TeamGenerationRun.created_at.desc()).first()
    ai_run = TeamGenerationRun.query.filter_by(project_id=project.id, method='ai_clustering').order_by(TeamGenerationRun.created_at.desc()).first()

    # If requested via POST or neither run exists yet, compute both simultaneously on identical cohort
    if request.method == 'POST' or request.args.get('rerun') == '1' or not (trad_run and ai_run):
        # 1. Run Traditional
        trad_builder = TraditionalTeamBuilder()
        trad_res = trad_builder.form_teams(students, project)

        # 2. Run AI
        ai_builder = MLTeamBuilder(model_dir=current_app.config['MODEL_DIR'])
        ai_res = ai_builder.recommend_teams(students, project)

        # Evaluate uniformly using TeamEvaluator
        trad_metrics = TeamEvaluator.evaluate(trad_res['teams'], trad_res['unassigned'], project, len(students), trad_res['metrics'].get('runtime_ms', 0))
        ai_metrics = TeamEvaluator.evaluate(ai_res['teams'], ai_res['unassigned'], project, len(students), ai_res['metrics'].get('runtime_ms', 0))

        # Save runs so they can be viewed
        if not trad_run:
            trad_run = TeamGenerationRun(
                project_id=project.id,
                method='traditional',
                status='Proposed',
                parameters_json=json.dumps({'weights': trad_builder.weights}),
                evaluation_metrics_json=json.dumps(trad_metrics)
            )
            db.session.add(trad_run)
            db.session.flush()
            for t in trad_res['teams']:
                team_obj = Team(
                    generation_run_id=trad_run.id,
                    project_id=project.id,
                    name=t['name'],
                    overall_score=t['overall_score'],
                    skill_coverage_pct=t['skill_coverage_pct'],
                    role_coverage_pct=t['role_coverage_pct'],
                    experience_score=t['experience_score'],
                    availability_score=t['availability_score'],
                    interest_score=t['interest_score'],
                    explanation_narrative=t['explanation'],
                    technical_details_json=json.dumps(t.get('technical_details', {}))
                )
                db.session.add(team_obj)

        if not ai_run:
            ai_run = TeamGenerationRun(
                project_id=project.id,
                method='ai_clustering',
                status='Proposed',
                parameters_json=json.dumps({'k': ai_res['metrics'].get('clustering_metadata', {}).get('k', 4)}),
                evaluation_metrics_json=json.dumps(ai_metrics)
            )
            db.session.add(ai_run)
            db.session.flush()
            for t in ai_res['teams']:
                team_obj = Team(
                    generation_run_id=ai_run.id,
                    project_id=project.id,
                    name=t['name'],
                    overall_score=t['overall_score'],
                    skill_coverage_pct=t['skill_coverage_pct'],
                    role_coverage_pct=t['role_coverage_pct'],
                    experience_score=t['experience_score'],
                    availability_score=t['availability_score'],
                    interest_score=t['interest_score'],
                    explanation_narrative=t['explanation'],
                    technical_details_json=json.dumps(t.get('technical_details', {}))
                )
                db.session.add(team_obj)

        db.session.commit()
    else:
        trad_metrics = trad_run.metrics
        ai_metrics = ai_run.metrics

    # Compare side by side
    comparison_rows = TeamEvaluator.compare(trad_metrics, ai_metrics)

    # Chart data for Chart.js
    radar_labels = ['Skill Coverage', 'Role Coverage', 'Availability', 'Experience', 'Student Fit']
    radar_trad_data = [
        trad_metrics.get('avg_skill_coverage', 0),
        trad_metrics.get('avg_role_coverage', 0),
        trad_metrics.get('avg_availability_compatibility', 0),
        trad_metrics.get('avg_experience_alignment', 0),
        trad_metrics.get('avg_student_fit', 0)
    ]
    radar_ai_data = [
        ai_metrics.get('avg_skill_coverage', 0),
        ai_metrics.get('avg_role_coverage', 0),
        ai_metrics.get('avg_availability_compatibility', 0),
        ai_metrics.get('avg_experience_alignment', 0),
        ai_metrics.get('avg_student_fit', 0)
    ]

    return render_template('comparison/index.html',
                           project=project,
                           all_projects=all_projects,
                           trad_run=trad_run,
                           ai_run=ai_run,
                           trad_metrics=trad_metrics,
                           ai_metrics=ai_metrics,
                           comparison_rows=comparison_rows,
                           radar_labels=json.dumps(radar_labels),
                           radar_trad_data=json.dumps(radar_trad_data),
                           radar_ai_data=json.dumps(radar_ai_data))

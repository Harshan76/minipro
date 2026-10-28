import json
from flask import Blueprint, render_template, request, g, redirect, url_for, flash, jsonify
from app.models import db, Project, Student, Team, TeamMember, TeamGenerationRun, SimulationRun, AuditLog
from app.algorithms.traditional import TraditionalTeamBuilder
from app.algorithms.evaluator import TeamEvaluator
from app.routes.auth import faculty_required

simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/simulation')
@faculty_required
def simulation_default():
    project = Project.query.order_by(Project.created_at.desc()).first()
    if not project:
        flash("Create a project to use the What-If Simulator.", "info")
        return redirect(url_for('projects.create'))
    return redirect(url_for('simulation.simulate_project', project_id=project.id))

@simulation_bp.route('/projects/<int:project_id>/simulation', methods=['GET', 'POST'])
@faculty_required
def simulate_project(project_id):
    project = Project.query.get_or_404(project_id)
    all_projects = Project.query.order_by(Project.title).all()
    students = Student.query.all()

    # Get baseline run
    baseline_run = TeamGenerationRun.query.filter_by(project_id=project.id).order_by(TeamGenerationRun.created_at.desc()).first()

    simulation_result = None
    diff_data = None

    if request.method == 'POST':
        # Simulated parameters
        sim_team_size = int(request.form.get('team_size', project.preferred_team_size))
        sim_min_hours = int(request.form.get('min_availability_hours', project.min_availability_hours))
        w_skill = float(request.form.get('weight_skill', 0.40))
        w_interest = float(request.form.get('weight_interest', 0.20))
        w_exp = float(request.form.get('weight_experience', 0.15))
        w_avail = float(request.form.get('weight_availability', 0.15))
        w_role = float(request.form.get('weight_role', 0.10))

        # Filter students by simulated availability
        sim_students = [s for s in students if s.available_hours_per_week >= sim_min_hours]
        if not sim_students:
            sim_students = students

        # Create temporary dummy project object with simulated parameters
        class SimulatedProjectProxy:
            def __init__(self, orig_p):
                self.id = orig_p.id
                self.title = orig_p.title
                self.description = orig_p.description
                self.domain = orig_p.domain
                self.preferred_team_size = sim_team_size
                self.min_team_size = max(sim_team_size - 1, 2)
                self.max_team_size = sim_team_size + 1
                self.min_experience_months = orig_p.min_experience_months
                self.min_availability_hours = sim_min_hours
                self.required_skills = orig_p.required_skills
                self.required_roles = orig_p.required_roles

        sim_project = SimulatedProjectProxy(project)

        weights = {
            'skill': w_skill,
            'interest': w_interest,
            'experience': w_exp,
            'availability': w_avail,
            'role': w_role
        }

        builder = TraditionalTeamBuilder(weights=weights)
        sim_res = builder.form_teams(sim_students, sim_project)
        sim_metrics = TeamEvaluator.evaluate(sim_res['teams'], sim_res['unassigned'], sim_project, len(students), sim_res['metrics'].get('runtime_ms', 0))

        # Save Simulation Run in DB (separate from finalized runs)
        sim_record = SimulationRun(
            project_id=project.id,
            simulation_name=f"Size {sim_team_size} | MinHours {sim_min_hours}h",
            parameters_json=json.dumps({
                'team_size': sim_team_size,
                'min_availability_hours': sim_min_hours,
                'weights': weights,
                'eligible_count': len(sim_students)
            }),
            results_json=json.dumps({
                'teams': [
                    {
                        'name': t['name'],
                        'member_names': [m.full_name for m in t['members']],
                        'member_ids': [m.id for m in t['members']],
                        'member_roles': t.get('member_roles', {}),
                        'overall_score': t['overall_score'],
                        'skill_coverage_pct': t['skill_coverage_pct'],
                        'role_coverage_pct': t['role_coverage_pct']
                    } for t in sim_res['teams']
                ],
                'metrics': sim_metrics,
                'unassigned_ids': [s.id for s in sim_res['unassigned']]
            })
        )
        db.session.add(sim_record)
        db.session.commit()

        # Compute Diff with baseline run
        baseline_metrics = baseline_run.metrics if baseline_run else {}
        baseline_teams = baseline_run.teams if baseline_run else []

        # Compare member movement
        # Student -> team in baseline vs student -> team in sim
        baseline_placement = {}
        for bt in baseline_teams:
            for bm in bt.members:
                baseline_placement[bm.student_id] = bt.name

        students_moved = []
        for st in sim_res['teams']:
            for sm in st['members']:
                old_team = baseline_placement.get(sm.id)
                new_team = st['name']
                if old_team and old_team != new_team:
                    students_moved.append({
                        'student_name': sm.full_name,
                        'from_team': old_team,
                        'to_team': new_team
                    })

        diff_data = {
            'sim_id': sim_record.id,
            'teams_count_before': len(baseline_teams),
            'teams_count_after': len(sim_res['teams']),
            'students_moved_count': len(students_moved),
            'students_moved': students_moved[:10],  # sample
            'skill_cov_before': baseline_metrics.get('avg_skill_coverage', 0.0),
            'skill_cov_after': sim_metrics.get('avg_skill_coverage', 0.0),
            'skill_cov_diff': round(sim_metrics.get('avg_skill_coverage', 0.0) - baseline_metrics.get('avg_skill_coverage', 0.0), 1),
            'role_cov_before': baseline_metrics.get('avg_role_coverage', 0.0),
            'role_cov_after': sim_metrics.get('avg_role_coverage', 0.0),
            'role_cov_diff': round(sim_metrics.get('avg_role_coverage', 0.0) - baseline_metrics.get('avg_role_coverage', 0.0), 1),
            'unassigned_before': baseline_metrics.get('unassigned_count', 0),
            'unassigned_after': sim_metrics.get('unassigned_count', 0),
            'violations_before': baseline_metrics.get('team_size_violations', 0),
            'violations_after': sim_metrics.get('team_size_violations', 0)
        }

        simulation_result = {
            'sim_record': sim_record,
            'teams': sim_res['teams'],
            'metrics': sim_metrics,
            'diff': diff_data
        }

    past_simulations = SimulationRun.query.filter_by(project_id=project.id).order_by(SimulationRun.created_at.desc()).limit(5).all()

    return render_template('simulation/index.html',
                           project=project,
                           all_projects=all_projects,
                           baseline_run=baseline_run,
                           students_count=len(students),
                           simulation_result=simulation_result,
                           past_simulations=past_simulations)

@simulation_bp.route('/projects/<int:project_id>/simulation/apply/<int:sim_id>', methods=['POST'])
@faculty_required
def apply_simulation(project_id, sim_id):
    """Applies simulated results to create a new Proposed TeamGenerationRun."""
    project = Project.query.get_or_404(project_id)
    sim_run = SimulationRun.query.get_or_404(sim_id)
    sim_data = sim_run.results

    if not sim_data or 'teams' not in sim_data:
        flash("Invalid simulation data to apply.", "danger")
        return redirect(url_for('simulation.simulate_project', project_id=project.id))

    # Create new Proposed TeamGenerationRun
    new_run = TeamGenerationRun(
        project_id=project.id,
        method='simulated_applied',
        status='Proposed',
        parameters_json=sim_run.parameters_json,
        evaluation_metrics_json=json.dumps(sim_data.get('metrics', {}))
    )
    db.session.add(new_run)
    db.session.flush()

    for t in sim_data['teams']:
        team_obj = Team(
            generation_run_id=new_run.id,
            project_id=project.id,
            name=t['name'],
            overall_score=t.get('overall_score', 80.0),
            skill_coverage_pct=t.get('skill_coverage_pct', 80.0),
            role_coverage_pct=t.get('role_coverage_pct', 80.0),
            explanation_narrative=f"Applied from What-If Simulation #{sim_id}."
        )
        db.session.add(team_obj)
        db.session.flush()

        roles = t.get('member_roles', {})
        for s_id in t.get('member_ids', []):
            tm = TeamMember(
                team_id=team_obj.id,
                student_id=s_id,
                assigned_role=roles.get(str(s_id), 'Developer'),
                fit_score=team_obj.overall_score
            )
            db.session.add(tm)

    log = AuditLog(
        user_id=g.user.id,
        action_type='SIMULATION_APPLIED',
        description=f"Applied What-If Simulation #{sim_id} as new proposed team generation run #{new_run.id}."
    )
    db.session.add(log)
    db.session.commit()

    flash(f"Simulation #{sim_id} results applied as proposed teams!", "success")
    return redirect(url_for('teams.view_run', project_id=project.id, run_id=new_run.id))

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.models import db, Project, Skill, ProjectSkill, ProjectRole, AuditLog
from app.routes.auth import login_required, faculty_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects')
@login_required
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects/index.html', projects=projects)

@projects_bp.route('/projects/<int:id>')
@login_required
def detail(id):
    project = Project.query.get_or_404(id)
    return render_template('projects/detail.html', project=project)

@projects_bp.route('/projects/create', methods=['GET', 'POST'])
@faculty_required
def create():
    all_skills = Skill.query.order_by(Skill.name).all()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        domain = request.form.get('domain', 'Web Development').strip()
        preferred_team_size = int(request.form.get('preferred_team_size', 4))
        min_team_size = int(request.form.get('min_team_size', 3))
        max_team_size = int(request.form.get('max_team_size', 5))
        min_experience_months = int(request.form.get('min_experience_months', 0))
        min_availability_hours = int(request.form.get('min_availability_hours', 8))

        if not title or not description:
            flash("Project title and description are required.", "danger")
            return render_template('projects/create.html', all_skills=all_skills)

        # Enforce size sanity
        if min_team_size > preferred_team_size:
            min_team_size = preferred_team_size
        if max_team_size < preferred_team_size:
            max_team_size = preferred_team_size

        new_project = Project(
            title=title,
            description=description,
            domain=domain,
            preferred_team_size=preferred_team_size,
            min_team_size=min_team_size,
            max_team_size=max_team_size,
            min_experience_months=min_experience_months,
            min_availability_hours=min_availability_hours,
            created_by_id=g.user.id
        )
        db.session.add(new_project)
        db.session.flush()

        # Add Required Skills
        selected_skills = request.form.getlist('skills[]')
        score_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        for sk_id in selected_skills:
            if not sk_id:
                continue
            min_prof = request.form.get(f'prof_{sk_id}', 'Intermediate')
            is_mandatory = (request.form.get(f'mandatory_{sk_id}', '1') == '1')
            ps = ProjectSkill(
                project_id=new_project.id,
                skill_id=int(sk_id),
                min_proficiency=min_prof,
                min_proficiency_score=score_map.get(min_prof, 2),
                is_mandatory=is_mandatory
            )
            db.session.add(ps)

        # Add Required Roles
        role_names = request.form.getlist('roles[]')
        for r_name in role_names:
            if r_name.strip():
                pr = ProjectRole(project_id=new_project.id, role_name=r_name.strip(), min_count=1)
                db.session.add(pr)

        log = AuditLog(user_id=g.user.id, action_type='PROJECT_CREATED', description=f"Created project: {title} (ID {new_project.id}).")
        db.session.add(log)
        db.session.commit()

        flash(f"Project '{title}' successfully created!", "success")
        return redirect(url_for('projects.detail', id=new_project.id))

    return render_template('projects/create.html', all_skills=all_skills)

@projects_bp.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
@faculty_required
def edit(id):
    project = Project.query.get_or_404(id)
    all_skills = Skill.query.order_by(Skill.name).all()

    if request.method == 'POST':
        project.title = request.form.get('title', '').strip()
        project.description = request.form.get('description', '').strip()
        project.domain = request.form.get('domain', '').strip()
        project.preferred_team_size = int(request.form.get('preferred_team_size', 4))
        project.min_team_size = int(request.form.get('min_team_size', 3))
        project.max_team_size = int(request.form.get('max_team_size', 5))
        project.min_experience_months = int(request.form.get('min_experience_months', 0))
        project.min_availability_hours = int(request.form.get('min_availability_hours', 8))
        project.status = request.form.get('status', 'Active')

        # Update Skills
        ProjectSkill.query.filter_by(project_id=project.id).delete()
        selected_skills = request.form.getlist('skills[]')
        score_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        for sk_id in selected_skills:
            if not sk_id:
                continue
            min_prof = request.form.get(f'prof_{sk_id}', 'Intermediate')
            is_mandatory = (request.form.get(f'mandatory_{sk_id}', '1') == '1')
            ps = ProjectSkill(
                project_id=project.id,
                skill_id=int(sk_id),
                min_proficiency=min_prof,
                min_proficiency_score=score_map.get(min_prof, 2),
                is_mandatory=is_mandatory
            )
            db.session.add(ps)

        # Update Roles
        ProjectRole.query.filter_by(project_id=project.id).delete()
        for r_name in request.form.getlist('roles[]'):
            if r_name.strip():
                pr = ProjectRole(project_id=project.id, role_name=r_name.strip(), min_count=1)
                db.session.add(pr)

        db.session.commit()
        flash("Project requirements updated.", "success")
        return redirect(url_for('projects.detail', id=project.id))

    current_skill_ids = {ps.skill_id: {'prof': ps.min_proficiency, 'mandatory': ps.is_mandatory} for ps in project.required_skills}
    current_roles = [pr.role_name for pr in project.required_roles]

    return render_template('projects/edit.html',
                           project=project,
                           all_skills=all_skills,
                           current_skill_ids=current_skill_ids,
                           current_roles=current_roles)

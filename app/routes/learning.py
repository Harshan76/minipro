from flask import Blueprint, render_template, request, g, redirect, url_for, flash
from app.models import db, Project, Team, TeamGenerationRun
from app.routes.auth import login_required

learning_bp = Blueprint('learning', __name__)

# Real, verified learning resource repository for common technical skills
SKILL_RESOURCES = {
    'python': {
        'resource_name': 'Python Official Tutorial & Docs',
        'resource_url': 'https://docs.python.org/3/tutorial/',
        'task': 'Complete Python core syntax, data structures (dicts, sets), and modular programming exercises.',
        'reason': 'Foundational for server-side APIs, scripting, and data processing.'
    },
    'flask': {
        'resource_name': 'Flask Official Quickstart & Application Patterns',
        'resource_url': 'https://flask.palletsprojects.com/en/stable/quickstart/',
        'task': 'Build a minimal CRUD endpoint with request handling, Jinja templates, and error handling.',
        'reason': 'Required for developing REST services and coordinating backend routing.'
    },
    'sql': {
        'resource_name': 'PostgreSQL / MySQL Interactive Tutorial & Exercises',
        'resource_url': 'https://www.mysqltutorial.org/',
        'task': 'Review relational schema design, primary/foreign keys, joins, and index optimizations.',
        'reason': 'Crucial for robust persistence and ensuring ACID transactions for project data.'
    },
    'javascript': {
        'resource_name': 'MDN Web Docs - JavaScript Guide',
        'resource_url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide',
        'task': 'Practice modern ES6+ features: Promises, async/await, DOM event listeners, and Fetch API.',
        'reason': 'Essential for interactive web applications and asynchronous frontend communication.'
    },
    'react': {
        'resource_name': 'React Official Documentation (Learn React)',
        'resource_url': 'https://react.dev/learn',
        'task': 'Complete the interactive tutorial on components, props, useState, and useEffect hooks.',
        'reason': 'Powers dynamic user interfaces and modular component-driven frontends.'
    },
    'machine learning': {
        'resource_name': 'Scikit-Learn User Guide & Getting Started',
        'resource_url': 'https://scikit-learn.org/stable/getting_started.html',
        'task': 'Walk through standard preprocessing pipelines, feature scaling, model fitting, and evaluation metrics.',
        'reason': 'Required for constructing reliable ML pipelines and interpreting model outcomes.'
    },
    'docker': {
        'resource_name': 'Docker Official Orientation and Setup',
        'resource_url': 'https://docs.docker.com/get-started/',
        'task': 'Write a multi-stage Dockerfile and docker-compose.yml file to containerize the web app and database.',
        'reason': 'Ensures reproducible development environments and simplifies deployment across team members.'
    },
    'git': {
        'resource_name': 'Git Book & GitHub Collaboration Guide',
        'resource_url': 'https://git-scm.com/book/en/v2',
        'task': 'Establish branch naming conventions, practice pull request reviews, and resolve merge conflicts.',
        'reason': 'Critical for effective multi-contributor team collaboration.'
    },
    'html': {
        'resource_name': 'MDN Web Docs - HTML Structure & Semantics',
        'resource_url': 'https://developer.mozilla.org/en-US/docs/Learn/HTML',
        'task': 'Implement semantic markup, accessible forms, and responsive mobile-first layouts.',
        'reason': 'Baseline for all web content structure and accessibility.'
    },
    'css': {
        'resource_name': 'MDN Web Docs - CSS Layouts & Flexbox/Grid',
        'resource_url': 'https://developer.mozilla.org/en-US/docs/Learn/CSS',
        'task': 'Master Flexbox and CSS Grid layout techniques for clean, responsive academic dashboards.',
        'reason': 'Ensures visually appealing and responsive user experiences.'
    }
}

@learning_bp.route('/learning-suggestions')
@login_required
def learning_default():
    project = Project.query.order_by(Project.created_at.desc()).first()
    if not project:
        flash("Please create a project to review learning suggestions.", "info")
        return redirect(url_for('projects.create'))
    return redirect(url_for('learning.project_learning', project_id=project.id))

@learning_bp.route('/projects/<int:project_id>/learning')
@login_required
def project_learning(project_id):
    project = Project.query.get_or_404(project_id)
    all_projects = Project.query.order_by(Project.title).all()

    # Get active or latest team generation run
    latest_run = TeamGenerationRun.query.filter_by(project_id=project.id).order_by(TeamGenerationRun.is_approved.desc(), TeamGenerationRun.created_at.desc()).first()
    
    gaps = []
    if latest_run:
        teams = Team.query.filter_by(generation_run_id=latest_run.id).all()
        for t in teams:
            team_skill_names = set(ss.skill.name.lower() for m in t.members for ss in m.student.skills)
            
            for ps in project.required_skills:
                req_sk_name = ps.skill.name.lower()
                if req_sk_name not in team_skill_names:
                    # Look up curated resource
                    matched_res = None
                    for key, res in SKILL_RESOURCES.items():
                        if key in req_sk_name or req_sk_name in key:
                            matched_res = res
                            break

                    if not matched_res:
                        matched_res = {
                            'resource_name': f"Official {ps.skill.name} Documentation & Reference",
                            'resource_url': f"https://en.wikipedia.org/wiki/{ps.skill.name.replace(' ', '_')}",
                            'task': f"Study core syntax, architecture patterns, and practical exercises for {ps.skill.name}.",
                            'reason': f"Required skill for {project.title} ({project.domain})."
                        }

                    gaps.append({
                        'team_name': t.name,
                        'team_id': t.id,
                        'skill_name': ps.skill.name,
                        'min_proficiency': ps.min_proficiency,
                        'is_mandatory': ps.is_mandatory,
                        'task': matched_res['task'],
                        'resource_name': matched_res['resource_name'],
                        'resource_url': matched_res['resource_url'],
                        'reason': matched_res['reason']
                    })

    return render_template('learning/index.html',
                           project=project,
                           all_projects=all_projects,
                           latest_run=latest_run,
                           gaps=gaps)

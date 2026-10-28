from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g
from app.models import db, Student, Project, User, Skill, Interest, Team, TeamGenerationRun, TeamMember, StudentFeedback, AuditLog
from app.routes.auth import faculty_required

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@faculty_required
def index():
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    # Obscure password for security in UI display
    safe_uri = db_uri
    if '@' in safe_uri and '://' in safe_uri:
        prefix = safe_uri.split('://')[0]
        host_part = safe_uri.split('@')[1]
        safe_uri = f"{prefix}://*****:*****@{host_part}"

    weights = {
        'skill': current_app.config['WEIGHT_SKILL'],
        'interest': current_app.config['WEIGHT_INTEREST'],
        'experience': current_app.config['WEIGHT_EXPERIENCE'],
        'availability': current_app.config['WEIGHT_AVAILABILITY'],
        'role': current_app.config['WEIGHT_ROLE']
    }

    counts = {
        'students': Student.query.count(),
        'projects': Project.query.count(),
        'teams': Team.query.count(),
        'skills': Skill.query.count(),
        'feedbacks': StudentFeedback.query.count()
    }

    return render_template('settings/index.html',
                           weights=weights,
                           db_uri=safe_uri,
                           counts=counts)

@settings_bp.route('/settings/update-weights', methods=['POST'])
@faculty_required
def update_weights():
    try:
        w_s = float(request.form.get('weight_skill', 0.40))
        w_i = float(request.form.get('weight_interest', 0.20))
        w_e = float(request.form.get('weight_experience', 0.15))
        w_a = float(request.form.get('weight_availability', 0.15))
        w_r = float(request.form.get('weight_role', 0.10))

        tot = w_s + w_i + w_e + w_a + w_r
        if tot <= 0:
            flash("Weights cannot sum to zero.", "danger")
            return redirect(url_for('settings.index'))

        # Normalize to 1.0
        current_app.config['WEIGHT_SKILL'] = round(w_s / tot, 3)
        current_app.config['WEIGHT_INTEREST'] = round(w_i / tot, 3)
        current_app.config['WEIGHT_EXPERIENCE'] = round(w_e / tot, 3)
        current_app.config['WEIGHT_AVAILABILITY'] = round(w_a / tot, 3)
        current_app.config['WEIGHT_ROLE'] = round(w_r / tot, 3)

        log = AuditLog(
            user_id=g.user.id,
            action_type='WEIGHTS_UPDATED',
            description=f"Updated baseline weights: Skill={current_app.config['WEIGHT_SKILL']}, Interest={current_app.config['WEIGHT_INTEREST']}, Exp={current_app.config['WEIGHT_EXPERIENCE']}, Avail={current_app.config['WEIGHT_AVAILABILITY']}, Role={current_app.config['WEIGHT_ROLE']}."
        )
        db.session.add(log)
        db.session.commit()

        flash("Traditional matching weights successfully updated and normalized to 100%!", "success")
    except Exception as e:
        flash(f"Error updating weights: {str(e)}", "danger")

    return redirect(url_for('settings.index'))

@settings_bp.route('/settings/reset-demo', methods=['POST'])
@faculty_required
def reset_demo():
    """Resets database and re-seeds synthetic student profiles & projects."""
    try:
        from seed_data import seed_database
        seed_database()
        flash("Demo data has been successfully reset! 30+ students and sample projects loaded.", "success")
    except Exception as e:
        flash(f"Error seeding demo data: {str(e)}", "danger")

    return redirect(url_for('settings.index'))

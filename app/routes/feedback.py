from flask import Blueprint, render_template, request, g, redirect, url_for, flash
from app.models import db, StudentFeedback, Project, Student, TeamMember, AuditLog
from app.routes.auth import login_required, faculty_required

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback/submit', methods=['GET', 'POST'])
@login_required
def submit():
    student = g.user.student_profile if g.user.is_student() else None
    if not student:
        flash("Only registered students can submit team experience feedback.", "warning")
        return redirect(url_for('dashboard.index'))

    # Check student's assigned team
    membership = TeamMember.query.filter_by(student_id=student.id).order_by(TeamMember.id.desc()).first()
    project = membership.team.project if membership else Project.query.order_by(Project.created_at.desc()).first()
    team = membership.team if membership else None

    # Check if student already submitted feedback for this project
    existing = StudentFeedback.query.filter_by(student_id=student.id, project_id=project.id).first() if project else None

    if request.method == 'POST':
        skill_fit = int(request.form.get('skill_fit_rating', 4))
        role_sat = int(request.form.get('role_satisfaction_rating', 4))
        avail_comp = int(request.form.get('availability_compatibility_rating', 4))
        collab_sat = int(request.form.get('collaboration_rating', 4))
        comments = request.form.get('comments', '').strip()

        if existing:
            existing.skill_fit_rating = skill_fit
            existing.role_satisfaction_rating = role_sat
            existing.availability_compatibility_rating = avail_comp
            existing.collaboration_rating = collab_sat
            existing.comments = comments
            flash("Your previous feedback has been updated.", "success")
        else:
            fb = StudentFeedback(
                student_id=student.id,
                project_id=project.id if project else 1,
                team_id=team.id if team else None,
                skill_fit_rating=skill_fit,
                role_satisfaction_rating=role_sat,
                availability_compatibility_rating=avail_comp,
                collaboration_rating=collab_sat,
                comments=comments
            )
            db.session.add(fb)
            flash("Thank you! Your feedback has been recorded.", "success")

        db.session.commit()
        return redirect(url_for('dashboard.index'))

    return render_template('feedback/submit.html',
                           student=student,
                           project=project,
                           team=team,
                           existing=existing)

@feedback_bp.route('/feedback/reviews')
@faculty_required
def reviews():
    all_feedbacks = StudentFeedback.query.order_by(StudentFeedback.submitted_at.desc()).all()
    
    total_count = len(all_feedbacks)
    avg_skill_fit = round(sum(f.skill_fit_rating for f in all_feedbacks) / total_count, 1) if total_count > 0 else 0.0
    avg_role_sat = round(sum(f.role_satisfaction_rating for f in all_feedbacks) / total_count, 1) if total_count > 0 else 0.0
    avg_avail_comp = round(sum(f.availability_compatibility_rating for f in all_feedbacks) / total_count, 1) if total_count > 0 else 0.0
    avg_collab = round(sum(f.collaboration_rating for f in all_feedbacks) / total_count, 1) if total_count > 0 else 0.0

    # Requirement 14: Clearly indicate whether sufficient labeled feedback exists
    # for future supervised outcome-prediction models (e.g. at least 50-100 real project reviews)
    min_required_samples = 50
    has_sufficient_ml_data = (total_count >= min_required_samples)

    return render_template('feedback/index.html',
                           feedbacks=all_feedbacks,
                           total_count=total_count,
                           avg_skill_fit=avg_skill_fit,
                           avg_role_sat=avg_role_sat,
                           avg_avail_comp=avg_avail_comp,
                           avg_collab=avg_collab,
                           min_required_samples=min_required_samples,
                           has_sufficient_ml_data=has_sufficient_ml_data)

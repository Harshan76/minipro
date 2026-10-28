from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.models import db, Student, Skill, StudentSkill, Interest, StudentInterest, AuditLog
from app.routes.auth import login_required, faculty_required

students_bp = Blueprint('students', __name__)

@students_bp.route('/students')
@login_required
def index():
    # Search and filtering
    query = request.args.get('q', '').strip()
    skill_filter = request.args.get('skill', '').strip()
    dept_filter = request.args.get('department', '').strip()

    students_query = Student.query

    if query:
        students_query = students_query.filter(
            (Student.full_name.ilike(f"%{query}%")) |
            (Student.student_id.ilike(f"%{query}%")) |
            (Student.email.ilike(f"%{query}%"))
        )

    if dept_filter:
        students_query = students_query.filter(Student.department == dept_filter)

    students = students_query.order_by(Student.student_id).all()

    if skill_filter:
        students = [s for s in students if any(skill_filter.lower() in ss.skill.name.lower() for ss in s.skills)]

    all_skills = Skill.query.order_by(Skill.name).all()
    all_departments = db.session.query(Student.department).distinct().all()
    departments = [d[0] for d in all_departments if d[0]]

    return render_template('students/index.html',
                           students=students,
                           all_skills=all_skills,
                           departments=departments,
                           search_query=query,
                           skill_filter=skill_filter,
                           dept_filter=dept_filter)

@students_bp.route('/students/<int:id>')
@login_required
def profile(id):
    student = Student.query.get_or_404(id)
    comp_pct, missing_fields = student.calculate_completion_score()
    return render_template('students/profile.html',
                           student=student,
                           comp_pct=comp_pct,
                           missing_fields=missing_fields)

@students_bp.route('/my-profile')
@login_required
def my_profile():
    if not g.user.is_student() or not g.user.student_profile:
        flash("You do not have an active student profile.", "warning")
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('students.edit_profile', id=g.user.student_profile.id))

@students_bp.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    student = Student.query.get_or_404(id)

    # Permission check: Faculty can edit anyone; Student can only edit themselves
    if g.user.is_student():
        if not g.user.student_profile or g.user.student_profile.id != student.id:
            flash("You can only edit your own profile.", "danger")
            return redirect(url_for('dashboard.index'))

    all_skills = Skill.query.order_by(Skill.name).all()
    all_interests = Interest.query.order_by(Interest.name).all()

    if request.method == 'POST':
        student.full_name = request.form.get('full_name', '').strip()
        student.email = request.form.get('email', '').strip()
        student.department = request.form.get('department', '').strip()
        student.year_of_study = int(request.form.get('year_of_study', 3))
        student.experience_months = int(request.form.get('experience_months', 0))
        student.experience_summary = request.form.get('experience_summary', '').strip()
        student.available_hours_per_week = int(request.form.get('available_hours_per_week', 10))

        # Preferred roles list to comma string
        roles = request.form.getlist('preferred_roles')
        student.preferred_roles = ', '.join(roles)

        # Days list
        days = request.form.getlist('availability_days')
        student.availability_days = ', '.join(days)

        # Slots
        slots = request.form.getlist('availability_slots')
        student.availability_slots = ', '.join(slots)

        # Manage Skills with proficiency
        # Clear existing and re-add selected
        StudentSkill.query.filter_by(student_id=student.id).delete()
        selected_skills = request.form.getlist('skills[]')
        for sk_id in selected_skills:
            if not sk_id:
                continue
            prof = request.form.get(f'prof_{sk_id}', 'Intermediate')
            score_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
            ss = StudentSkill(
                student_id=student.id,
                skill_id=int(sk_id),
                proficiency=prof,
                proficiency_score=score_map.get(prof, 2)
            )
            db.session.add(ss)

        # Handle custom new skill input
        custom_skill_name = request.form.get('custom_skill', '').strip()
        if custom_skill_name:
            skill_obj = Skill.query.filter(Skill.name.ilike(custom_skill_name)).first()
            if not skill_obj:
                skill_obj = Skill(name=custom_skill_name, category='Custom')
                db.session.add(skill_obj)
                db.session.flush()
            prof = request.form.get('custom_skill_prof', 'Intermediate')
            score_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
            ss = StudentSkill(student_id=student.id, skill_id=skill_obj.id, proficiency=prof, proficiency_score=score_map.get(prof, 2))
            db.session.add(ss)

        # Manage Interests
        StudentInterest.query.filter_by(student_id=student.id).delete()
        selected_interests = request.form.getlist('interests[]')
        for int_id in selected_interests:
            if not int_id:
                continue
            si = StudentInterest(student_id=student.id, interest_id=int_id)
            db.session.add(si)

        # Custom interest input
        custom_interest = request.form.get('custom_interest', '').strip()
        if custom_interest:
            int_obj = Interest.query.filter(Interest.name.ilike(custom_interest)).first()
            if not int_obj:
                int_obj = Interest(name=custom_interest, category='Custom')
                db.session.add(int_obj)
                db.session.flush()
            si = StudentInterest(student_id=student.id, interest_id=int_obj.id)
            db.session.add(si)

        # Recalculate completion score
        student.calculate_completion_score()

        # Audit
        log = AuditLog(user_id=g.user.id, action_type='STUDENT_UPDATED', description=f"Updated profile for student {student.student_id} ({student.full_name}).")
        db.session.add(log)
        db.session.commit()

        flash("Student profile successfully updated!", "success")
        return redirect(url_for('students.profile', id=student.id))

    comp_pct, missing_fields = student.calculate_completion_score()
    current_skill_ids = {ss.skill_id: ss.proficiency for ss in student.skills}
    current_interest_ids = {si.interest_id for si in student.interests}

    return render_template('students/edit.html',
                           student=student,
                           all_skills=all_skills,
                           all_interests=all_interests,
                           current_skill_ids=current_skill_ids,
                           current_interest_ids=current_interest_ids,
                           comp_pct=comp_pct,
                           missing_fields=missing_fields)

@students_bp.route('/students/create', methods=['GET', 'POST'])
@faculty_required
def create_student():
    all_skills = Skill.query.order_by(Skill.name).all()
    all_interests = Interest.query.order_by(Interest.name).all()

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', 'Computer Science')
        year_of_study = int(request.form.get('year_of_study', 3))
        experience_months = int(request.form.get('experience_months', 0))
        available_hours = int(request.form.get('available_hours_per_week', 10))

        if not student_id or not full_name or not email:
            flash("Student ID, Name, and Email are required.", "danger")
            return render_template('students/create.html', all_skills=all_skills, all_interests=all_interests)

        if Student.query.filter_by(student_id=student_id).first():
            flash(f"Student ID '{student_id}' already exists.", "warning")
            return render_template('students/create.html', all_skills=all_skills, all_interests=all_interests)

        student = Student(
            student_id=student_id,
            full_name=full_name,
            email=email,
            department=department,
            year_of_study=year_of_study,
            experience_months=experience_months,
            available_hours_per_week=available_hours,
            preferred_roles=', '.join(request.form.getlist('preferred_roles')),
            availability_days=', '.join(request.form.getlist('availability_days')),
            availability_slots=', '.join(request.form.getlist('availability_slots'))
        )
        db.session.add(student)
        db.session.flush()

        # Add Skills
        for sk_id in request.form.getlist('skills[]'):
            if sk_id:
                prof = request.form.get(f'prof_{sk_id}', 'Intermediate')
                score_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
                ss = StudentSkill(student_id=student.id, skill_id=int(sk_id), proficiency=prof, proficiency_score=score_map.get(prof, 2))
                db.session.add(ss)

        # Add Interests
        for int_id in request.form.getlist('interests[]'):
            if int_id:
                si = StudentInterest(student_id=student.id, interest_id=int(int_id))
                db.session.add(si)

        student.calculate_completion_score()
        db.session.commit()

        flash(f"Student {full_name} ({student_id}) successfully added!", "success")
        return redirect(url_for('students.index'))

    return render_template('students/create.html', all_skills=all_skills, all_interests=all_interests)

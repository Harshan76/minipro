from app.models import db, Student, Project, Skill, StudentSkill

def test_student_profile_completion_calculation(app):
    with app.app_context():
        student = Student.query.filter_by(student_id='STU-001').first()
        pct, missing = student.calculate_completion_score()
        assert pct >= 70
        assert isinstance(missing, list)

        # Incomplete student missing skills and interests
        new_stu = Student(student_id='STU-INC', full_name='Incomplete', email='inc@test.edu', preferred_roles='', experience_months=None)
        db.session.add(new_stu)
        db.session.flush()
        inc_pct, inc_missing = new_stu.calculate_completion_score()
        assert inc_pct < 60
        assert len(inc_missing) >= 3
        assert new_stu.profile_completed is False

def test_database_relationships_and_cascade(app):
    with app.app_context():
        student = Student.query.filter_by(student_id='STU-001').first()
        assert len(student.skills) >= 1
        assert len(student.interests) >= 1

        student_id = student.id
        db.session.delete(student)
        db.session.commit()

        # Associated skills should be deleted by cascade
        skills_left = StudentSkill.query.filter_by(student_id=student_id).all()
        assert len(skills_left) == 0

def test_project_attributes_and_defaults(app):
    with app.app_context():
        project = Project.query.first()
        assert project is not None
        assert project.preferred_team_size == 3
        assert len(project.required_skills) == 2
        assert len(project.required_roles) == 2

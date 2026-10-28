import pytest
import os
from app import create_app
from app.models import db, User, Student, Skill, StudentSkill, Interest, StudentInterest, Project, ProjectSkill, ProjectRole
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MODEL_DIR = os.path.join(os.path.dirname(__file__), 'test_models')

@pytest.fixture(scope='function')
def app():
    os.makedirs(TestConfig.MODEL_DIR, exist_ok=True)
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()

        # Seed minimal fixtures
        # 1. Users
        faculty = User(username='test_faculty', email='faculty@test.edu', role='faculty')
        faculty.set_password('pass123')
        db.session.add(faculty)

        student_user = User(username='test_student', email='student@test.edu', role='student')
        student_user.set_password('pass123')
        db.session.add(student_user)

        # 2. Skills
        sk_python = Skill(name='Python', category='Backend')
        sk_react = Skill(name='React', category='Frontend')
        sk_sql = Skill(name='SQL', category='Database')
        sk_ml = Skill(name='Machine Learning', category='AI/ML')
        db.session.add_all([sk_python, sk_react, sk_sql, sk_ml])

        # 3. Interests
        int_web = Interest(name='Web Development', category='Software')
        int_ai = Interest(name='Artificial Intelligence', category='Data')
        db.session.add_all([int_web, int_ai])
        db.session.flush()

        # 4. Project
        project = Project(
            title="Test Capstone Project",
            description="A comprehensive testing project",
            domain="Web Development & AI",
            preferred_team_size=3,
            min_team_size=2,
            max_team_size=4,
            min_experience_months=0,
            min_availability_hours=8,
            created_by_id=faculty.id
        )
        db.session.add(project)
        db.session.flush()

        # Required skills & roles
        db.session.add(ProjectSkill(project_id=project.id, skill_id=sk_python.id, min_proficiency='Intermediate', min_proficiency_score=2, is_mandatory=True))
        db.session.add(ProjectSkill(project_id=project.id, skill_id=sk_react.id, min_proficiency='Intermediate', min_proficiency_score=2, is_mandatory=True))
        db.session.add(ProjectRole(project_id=project.id, role_name='Frontend Developer', min_count=1))
        db.session.add(ProjectRole(project_id=project.id, role_name='Backend Developer', min_count=1))

        # 5. Create 6 distinct students
        students_data = [
            ("Alice", "alice@test.edu", ["Python"], ["Web Development"], 12, 14, ["Backend Developer"]),
            ("Bob", "bob@test.edu", ["React"], ["Web Development"], 10, 12, ["Frontend Developer"]),
            ("Charlie", "charlie@test.edu", ["SQL", "Python"], ["Web Development"], 8, 10, ["Backend Developer"]),
            ("Diana", "diana@test.edu", ["React", "Python"], ["Artificial Intelligence"], 14, 16, ["Fullstack Engineer"]),
            ("Ethan", "ethan@test.edu", ["Machine Learning", "Python"], ["Artificial Intelligence"], 18, 12, ["Data / ML Specialist"]),
            ("Fiona", "fiona@test.edu", ["React"], ["Web Development"], 6, 8, ["Frontend Developer"])
        ]

        for idx, (name, email, s_skills, s_interests, exp, hrs, roles) in enumerate(students_data):
            stu = Student(
                student_id=f"STU-00{idx+1}",
                full_name=name,
                email=email,
                department="Computer Science",
                year_of_study=3,
                experience_months=exp,
                available_hours_per_week=hrs,
                preferred_roles=', '.join(roles),
                availability_days="Mon,Wed,Fri",
                availability_slots="Evening"
            )
            db.session.add(stu)
            db.session.flush()

            for sk_n in s_skills:
                sk_obj = Skill.query.filter_by(name=sk_n).first()
                if sk_obj:
                    db.session.add(StudentSkill(student_id=stu.id, skill_id=sk_obj.id, proficiency='Intermediate', proficiency_score=2))

            for it_n in s_interests:
                it_obj = Interest.query.filter_by(name=it_n).first()
                if it_obj:
                    db.session.add(StudentInterest(student_id=stu.id, interest_id=it_obj.id))

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'faculty', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_faculty(self):
        return self.role in ['faculty', 'admin']

    def is_student(self):
        return self.role == 'student'

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, unique=True)
    student_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), default='Computer Science')
    year_of_study = db.Column(db.Integer, default=3)
    experience_months = db.Column(db.Integer, default=0)
    experience_summary = db.Column(db.Text, default='')
    preferred_roles = db.Column(db.String(255), default='')  # comma-separated
    available_hours_per_week = db.Column(db.Integer, default=10)
    availability_days = db.Column(db.String(255), default='Mon,Wed,Fri')  # comma-separated
    availability_slots = db.Column(db.String(255), default='Evening,Weekend')  # comma-separated
    profile_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    skills = db.relationship('StudentSkill', backref='student', cascade='all, delete-orphan')
    interests = db.relationship('StudentInterest', backref='student', cascade='all, delete-orphan')
    team_memberships = db.relationship('TeamMember', backref='student', cascade='all, delete-orphan')
    feedbacks = db.relationship('StudentFeedback', backref='student', cascade='all, delete-orphan')

    @property
    def roles_list(self):
        if not self.preferred_roles:
            return []
        return [r.strip() for r in self.preferred_roles.split(',') if r.strip()]

    @property
    def days_list(self):
        if not self.availability_days:
            return []
        return [d.strip() for d in self.availability_days.split(',') if d.strip()]

    @property
    def slots_list(self):
        if not self.availability_slots:
            return []
        return [s.strip() for s in self.availability_slots.split(',') if s.strip()]

    def calculate_completion_score(self):
        """Calculates profile completion percentage and missing items."""
        total_checks = 7
        completed_checks = 0
        missing = []

        if self.full_name and self.email:
            completed_checks += 1
        else:
            missing.append("Basic contact info (Name, Email)")

        if self.department and self.year_of_study:
            completed_checks += 1
        else:
            missing.append("Academic department and year")

        if len(self.skills) > 0:
            completed_checks += 1
        else:
            missing.append("At least 1 technical skill")

        if len(self.interests) > 0:
            completed_checks += 1
        else:
            missing.append("At least 1 interest topic")

        if self.preferred_roles:
            completed_checks += 1
        else:
            missing.append("Preferred team roles")

        if self.available_hours_per_week and self.availability_days:
            completed_checks += 1
        else:
            missing.append("Availability schedule")

        if self.experience_months is not None:
            completed_checks += 1
        else:
            missing.append("Project experience details")

        pct = int((completed_checks / total_checks) * 100)
        self.profile_completed = (pct >= 85)
        return pct, missing

    def __repr__(self):
        return f"<Student {self.student_id} - {self.full_name}>"


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), default='General')  # Frontend, Backend, AI/ML, Database, DevOps, etc.

    def __repr__(self):
        return f"<Skill {self.name}>"


class StudentSkill(db.Model):
    __tablename__ = 'student_skills'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    proficiency = db.Column(db.String(20), default='Intermediate')  # Beginner, Intermediate, Advanced
    proficiency_score = db.Column(db.Integer, default=2)  # 1: Beginner, 2: Intermediate, 3: Advanced

    skill = db.relationship('Skill')

    def __repr__(self):
        return f"<StudentSkill {self.student_id}-{self.skill_id} ({self.proficiency})>"


class Interest(db.Model):
    __tablename__ = 'interests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), default='General')

    def __repr__(self):
        return f"<Interest {self.name}>"


class StudentInterest(db.Model):
    __tablename__ = 'student_interests'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    interest_id = db.Column(db.Integer, db.ForeignKey('interests.id', ondelete='CASCADE'), nullable=False)

    interest = db.relationship('Interest')

    def __repr__(self):
        return f"<StudentInterest {self.student_id}-{self.interest_id}>"


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(100), default='Web Development')
    preferred_team_size = db.Column(db.Integer, default=4)
    min_team_size = db.Column(db.Integer, default=3)
    max_team_size = db.Column(db.Integer, default=5)
    min_experience_months = db.Column(db.Integer, default=0)
    min_availability_hours = db.Column(db.Integer, default=8)
    status = db.Column(db.String(30), default='Active')  # Draft, Active, Completed
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    required_skills = db.relationship('ProjectSkill', backref='project', cascade='all, delete-orphan')
    required_roles = db.relationship('ProjectRole', backref='project', cascade='all, delete-orphan')
    generation_runs = db.relationship('TeamGenerationRun', backref='project', cascade='all, delete-orphan', order_by='desc(TeamGenerationRun.created_at)')
    teams = db.relationship('Team', backref='project', cascade='all, delete-orphan')
    simulations = db.relationship('SimulationRun', backref='project', cascade='all, delete-orphan')

    @property
    def latest_traditional_run(self):
        for run in self.generation_runs:
            if run.method == 'traditional':
                return run
        return None

    @property
    def latest_ai_run(self):
        for run in self.generation_runs:
            if run.method == 'ai_clustering':
                return run
        return None

    def __repr__(self):
        return f"<Project {self.title}>"


class ProjectSkill(db.Model):
    __tablename__ = 'project_skills'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    min_proficiency = db.Column(db.String(20), default='Intermediate')
    min_proficiency_score = db.Column(db.Integer, default=2)
    is_mandatory = db.Column(db.Boolean, default=True)

    skill = db.relationship('Skill')

    def __repr__(self):
        return f"<ProjectSkill {self.project_id}-{self.skill_id}>"


class ProjectRole(db.Model):
    __tablename__ = 'project_roles'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    role_name = db.Column(db.String(60), nullable=False)  # e.g., 'Frontend Developer'
    min_count = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<ProjectRole {self.project_id} - {self.role_name}>"


class TeamGenerationRun(db.Model):
    __tablename__ = 'team_generation_runs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    method = db.Column(db.String(30), nullable=False)  # 'traditional' or 'ai_clustering'
    status = db.Column(db.String(30), default='Proposed')  # 'Proposed', 'Approved', 'Archived'
    parameters_json = db.Column(db.Text, default='{}')
    evaluation_metrics_json = db.Column(db.Text, default='{}')
    is_approved = db.Column(db.Boolean, default=False)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teams = db.relationship('Team', backref='generation_run', cascade='all, delete-orphan')

    @property
    def metrics(self):
        try:
            return json.loads(self.evaluation_metrics_json or '{}')
        except Exception:
            return {}

    @property
    def parameters(self):
        try:
            return json.loads(self.parameters_json or '{}')
        except Exception:
            return {}

    def __repr__(self):
        return f"<TeamGenerationRun {self.id} ({self.method}) - Project {self.project_id}>"


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    generation_run_id = db.Column(db.Integer, db.ForeignKey('team_generation_runs.id', ondelete='CASCADE'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(80), nullable=False)  # "Team Alpha", "Team Beta", etc.
    overall_score = db.Column(db.Float, default=0.0)
    skill_coverage_pct = db.Column(db.Float, default=0.0)
    role_coverage_pct = db.Column(db.Float, default=0.0)
    experience_score = db.Column(db.Float, default=0.0)
    availability_score = db.Column(db.Float, default=0.0)
    interest_score = db.Column(db.Float, default=0.0)
    explanation_narrative = db.Column(db.Text, default='')  # Plain English "Why This Team?"
    technical_details_json = db.Column(db.Text, default='{}')  # Centroid distances, cluster distributions
    status = db.Column(db.String(30), default='Proposed')  # 'Proposed', 'Approved', 'Modified'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('TeamMember', backref='team', cascade='all, delete-orphan')

    @property
    def technical_details(self):
        try:
            return json.loads(self.technical_details_json or '{}')
        except Exception:
            return {}

    def __repr__(self):
        return f"<Team {self.name} (Project {self.project_id})>"


class TeamMember(db.Model):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    assigned_role = db.Column(db.String(60), default='Developer')
    student_cluster = db.Column(db.Integer, default=-1)
    cluster_label = db.Column(db.String(100), default='Generalist')
    fit_score = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<TeamMember Team {self.team_id} - Student {self.student_id}>"


class ModelTrainingRun(db.Model):
    __tablename__ = 'model_training_runs'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(80), default='KMeans-StudentArchetypes')
    n_clusters = db.Column(db.Integer, default=4)
    n_students = db.Column(db.Integer, default=0)
    inertia = db.Column(db.Float, default=0.0)
    silhouette_score = db.Column(db.Float, default=0.0)
    features_list_json = db.Column(db.Text, default='[]')
    cluster_summaries_json = db.Column(db.Text, default='{}')
    model_path = db.Column(db.String(255), default='')
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def cluster_summaries(self):
        try:
            return json.loads(self.cluster_summaries_json or '{}')
        except Exception:
            return {}

    @property
    def features_list(self):
        try:
            return json.loads(self.features_list_json or '[]')
        except Exception:
            return []

    def __repr__(self):
        return f"<ModelTrainingRun k={self.n_clusters} n={self.n_students}>"


class SimulationRun(db.Model):
    __tablename__ = 'simulation_runs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    simulation_name = db.Column(db.String(100), default='What-If Simulation')
    parameters_json = db.Column(db.Text, default='{}')
    results_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def results(self):
        try:
            return json.loads(self.results_json or '{}')
        except Exception:
            return {}

    @property
    def parameters(self):
        try:
            return json.loads(self.parameters_json or '{}')
        except Exception:
            return {}


class StudentFeedback(db.Model):
    __tablename__ = 'student_feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='SET NULL'), nullable=True)
    skill_fit_rating = db.Column(db.Integer, default=4)  # 1-5
    role_satisfaction_rating = db.Column(db.Integer, default=4)  # 1-5
    availability_compatibility_rating = db.Column(db.Integer, default=4)  # 1-5
    collaboration_rating = db.Column(db.Integer, default=4)  # 1-5
    comments = db.Column(db.Text, default='')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    team = db.relationship('Team')
    project = db.relationship('Project')


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action_type = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action_type} at {self.timestamp}>"

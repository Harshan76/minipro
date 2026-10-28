from app.models import Student, Project
from app.algorithms.traditional import TraditionalTeamBuilder

def test_traditional_weights_normalization():
    builder = TraditionalTeamBuilder(weights={'skill': 4, 'interest': 2, 'experience': 1.5, 'availability': 1.5, 'role': 1})
    assert round(sum(builder.weights.values()), 3) == 1.000
    assert builder.weights['skill'] == 0.40

def test_traditional_team_formation_constraints(app):
    with app.app_context():
        students = Student.query.all()
        project = Project.query.first()

        builder = TraditionalTeamBuilder()
        result = builder.form_teams(students, project)

        teams = result['teams']
        unassigned = result['unassigned']
        metrics = result['metrics']

        assert len(teams) > 0
        assert metrics['assigned_count'] + len(unassigned) == len(students)

        # Requirement 19: No student assigned more than once
        assigned_ids = []
        for t in teams:
            for m in t['members']:
                assigned_ids.append(m.id)

        assert len(assigned_ids) == len(set(assigned_ids)), "Duplicate student assignments detected across teams!"

        # Check team size compliance
        for t in teams:
            assert len(t['members']) >= project.min_team_size
            assert len(t['members']) <= project.max_team_size

def test_individual_fit_score_calculation(app):
    with app.app_context():
        student = Student.query.filter_by(student_id='STU-001').first()
        project = Project.query.first()

        builder = TraditionalTeamBuilder()
        fit = builder.calculate_student_project_fit(student, project)

        assert 0.0 <= fit['total_fit'] <= 100.0
        assert 'skill_score' in fit
        assert 'interest_score' in fit
        assert 'experience_score' in fit

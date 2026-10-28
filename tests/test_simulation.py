from app.models import Student, Project, TeamGenerationRun, SimulationRun
from app.algorithms.traditional import TraditionalTeamBuilder
from app.algorithms.evaluator import TeamEvaluator

def test_what_if_simulation_execution(app):
    with app.app_context():
        students = Student.query.all()
        project = Project.query.first()

        # Simulate smaller team size = 2
        class SimProxy:
            id = project.id
            title = project.title
            domain = project.domain
            preferred_team_size = 2
            min_team_size = 2
            max_team_size = 3
            min_experience_months = 0
            min_availability_hours = 8
            required_skills = project.required_skills
            required_roles = project.required_roles

        builder = TraditionalTeamBuilder()
        res = builder.form_teams(students, SimProxy())

        assert len(res['teams']) == 3  # 6 students / 2 = 3 teams
        for t in res['teams']:
            assert len(t['members']) == 2

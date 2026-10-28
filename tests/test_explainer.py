from app.models import Student, Project
from app.algorithms.traditional import TraditionalTeamBuilder
from app.algorithms.explainer import TeamExplainer

def test_team_explainer_narrative_and_breakdown(app):
    with app.app_context():
        students = Student.query.all()
        project = Project.query.first()

        builder = TraditionalTeamBuilder()
        res = builder.form_teams(students, project)

        first_team = res['teams'][0]
        explanation = TeamExplainer.explain_team(first_team, project)

        assert 'summary_narrative' in explanation
        assert len(explanation['summary_narrative']) > 20
        assert 'covered_skills' in explanation
        assert 'missing_skills' in explanation
        assert 'suggestions' in explanation
        assert isinstance(explanation['suggestions'], list)

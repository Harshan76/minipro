from app.models import Student, Project
from app.algorithms.traditional import TraditionalTeamBuilder
from app.algorithms.ml_cluster import MLTeamBuilder
from app.algorithms.evaluator import TeamEvaluator

def test_evaluator_metrics_calculation(app):
    with app.app_context():
        students = Student.query.all()
        project = Project.query.first()

        builder = TraditionalTeamBuilder()
        res = builder.form_teams(students, project)

        metrics = TeamEvaluator.evaluate(res['teams'], res['unassigned'], project, len(students), runtime_ms=12.5)

        assert 'avg_skill_coverage' in metrics
        assert 'avg_role_coverage' in metrics
        assert 'avg_student_fit' in metrics
        assert 'pct_assigned' in metrics
        assert metrics['pct_assigned'] > 0
        assert metrics['runtime_ms'] == 12.5

def test_comparison_between_traditional_and_ai(app):
    with app.app_context():
        students = Student.query.all()
        project = Project.query.first()

        trad_res = TraditionalTeamBuilder().form_teams(students, project)
        ai_res = MLTeamBuilder(model_dir=app.config['MODEL_DIR']).recommend_teams(students, project)

        trad_metrics = TeamEvaluator.evaluate(trad_res['teams'], trad_res['unassigned'], project, len(students), 10.0)
        ai_metrics = TeamEvaluator.evaluate(ai_res['teams'], ai_res['unassigned'], project, len(students), 25.0)

        rows = TeamEvaluator.compare(trad_metrics, ai_metrics)
        assert len(rows) >= 8

        for row in rows:
            assert 'label' in row
            assert 'winner' in row
            assert row['winner'] in ['traditional', 'ai', 'tie']

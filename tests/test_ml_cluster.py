import os
import joblib
from app.models import Student, Project
from app.algorithms.ml_cluster import MLTeamBuilder

def test_feature_extraction(app):
    with app.app_context():
        students = Student.query.all()
        builder = MLTeamBuilder(model_dir=app.config['MODEL_DIR'])
        df, feature_cols = builder.extract_features(students)

        assert len(df) == len(students)
        assert len(feature_cols) > 0
        assert 'exp_months' in feature_cols
        assert 'avail_hours' in feature_cols

def test_kmeans_training_and_archetypes(app):
    with app.app_context():
        students = Student.query.all()
        builder = MLTeamBuilder(model_dir=app.config['MODEL_DIR'])
        res = builder.train_clustering_model(students, n_clusters=2)

        assert res['success'] is True
        assert res['n_clusters'] == 2
        assert 'cluster_summaries' in res
        assert os.path.exists(res['model_path'])

        # Test model reloadability using Joblib
        pipeline = joblib.load(res['model_path'])
        assert 'scaler' in pipeline
        assert 'kmeans' in pipeline
        assert pipeline['kmeans'].n_clusters == 2

def test_insufficient_data_handling(app):
    with app.app_context():
        # Only 2 students: below threshold of 4
        students = Student.query.limit(2).all()
        builder = MLTeamBuilder(model_dir=app.config['MODEL_DIR'])
        res = builder.train_clustering_model(students, n_clusters=3)

        assert res['success'] is False
        assert "Meaningful clustering requires at least 4 student profiles" in res['warning']

def test_ai_team_recommendations(app):
    with app.app_context():
        students = Student.query.all()
        project = Project.query.first()

        builder = MLTeamBuilder(model_dir=app.config['MODEL_DIR'])
        result = builder.recommend_teams(students, project)

        assert 'teams' in result
        assert 'metrics' in result
        assert len(result['teams']) > 0

        # Check no duplicate students in AI assignment
        assigned_ids = [m.id for t in result['teams'] for m in t['members']]
        assert len(assigned_ids) == len(set(assigned_ids))

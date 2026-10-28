import json
from app.models import Project, TeamGenerationRun, Team

def test_routes_workflow(client):
    # 1. Login as Faculty
    res = client.post('/login', data={'identifier': 'test_faculty', 'password': 'pass123'}, follow_redirects=True)
    assert res.status_code == 200

    # 2. View Overview Dashboard
    res = client.get('/dashboard')
    assert res.status_code == 200
    assert b"Academic Overview Dashboard" in res.data

    # 3. View Student Directory
    res = client.get('/students')
    assert res.status_code == 200
    assert b"Student Directory" in res.data

    # 4. Form Teams (Traditional)
    project = Project.query.first()
    res = client.post(f'/projects/{project.id}/generate', data={'method': 'traditional'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Successfully generated teams using Traditional Rule-Based Method!" in res.data

    # 5. Form Teams (AI Clustering)
    res = client.post(f'/projects/{project.id}/generate', data={'method': 'ai_clustering'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"AI-Powered" in res.data

    # 6. Check "Why This Team?" JSON endpoint
    team = Team.query.first()
    res = client.get(f'/teams/{team.id}/why?json=1')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert 'summary_narrative' in data
    assert 'covered_skills' in data
    assert 'suggestions' in data

    # 7. Compare Results
    res = client.get(f'/projects/{project.id}/compare')
    assert res.status_code == 200
    assert b"Baseline vs AI Comparison Dashboard" in res.data

    # 8. Team Balance
    res = client.get(f'/projects/{project.id}/balance')
    assert res.status_code == 200
    assert b"Smart Team Balance Analyzer" in res.data

    # 9. Learning Suggestions
    res = client.get(f'/projects/{project.id}/learning')
    assert res.status_code == 200
    assert b"Learning Suggestions" in res.data

    # 10. Fairness and Allocation Audit
    res = client.get(f'/projects/{project.id}/audit')
    assert res.status_code == 200
    assert b"Fairness &amp; Allocation Audit" in res.data or b"Fairness & Allocation Audit" in res.data

    # 11. Network Endpoint
    res = client.get('/api/network-data')
    assert res.status_code == 200
    net_data = json.loads(res.data)
    assert 'nodes' in net_data
    assert 'edges' in net_data

    # 12. CSV Export
    run = TeamGenerationRun.query.first()
    res = client.get(f'/export/teams-csv/{run.id}')
    assert res.status_code == 200
    assert res.content_type.startswith('text/csv')
    assert b"Student ID,Student Name" in res.data

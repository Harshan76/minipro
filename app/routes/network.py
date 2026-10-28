from flask import Blueprint, render_template, jsonify, request, g
from app.models import db, Student, Skill, Interest, TeamMember
from app.routes.auth import login_required

network_bp = Blueprint('network', __name__)

@network_bp.route('/network')
@login_required
def index():
    all_skills = Skill.query.order_by(Skill.name).all()
    all_interests = Interest.query.order_by(Interest.name).all()
    students = Student.query.all()
    return render_template('network/index.html',
                           skills=all_skills,
                           interests=all_interests,
                           students=students)

@network_bp.route('/api/network-data')
@login_required
def get_network_data():
    skill_filter = request.args.get('skill', '').strip()
    interest_filter = request.args.get('interest', '').strip()

    students = Student.query.all()
    nodes = []
    edges = []

    # Map team colors
    palette = [
        '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899',
        '#06b6d4', '#84cc16', '#f97316', '#6366f1', '#14b8a6'
    ]

    # Pre-fetch recent team memberships
    team_memberships = {tm.student_id: tm for tm in TeamMember.query.all()}

    student_skills_map = {}
    student_interests_map = {}

    for s in students:
        s_skills = {ss.skill.name.lower() for ss in s.skills}
        s_interests = {si.interest.name.lower() for si in s.interests}
        student_skills_map[s.id] = s_skills
        student_interests_map[s.id] = s_interests

        # Determine node color based on assigned team or default
        tm = team_memberships.get(s.id)
        team_name = tm.team.name if tm else "Unassigned"
        color = palette[tm.team_id % len(palette)] if tm else "#94a3b8"

        nodes.append({
            'id': s.id,
            'label': s.full_name,
            'title': f"<b>{s.full_name}</b><br>ID: {s.student_id}<br>Team: {team_name}<br>Skills: {', '.join([ss.skill.name for ss in s.skills[:3]])}<br>Exp: {s.experience_months} mos",
            'department': s.department,
            'team': team_name,
            'color': color,
            'skills': [ss.skill.name for ss in s.skills],
            'interests': [si.interest.name for si in s.interests],
            'experience': s.experience_months,
            'roles': s.roles_list
        })

    # Build edges based on shared skills or complementary interests
    edge_id = 0
    for i in range(len(students)):
        for j in range(i + 1, len(students)):
            s1 = students[i]
            s2 = students[j]
            shared_sk = student_skills_map[s1.id] & student_skills_map[s2.id]
            shared_int = student_interests_map[s1.id] & student_interests_map[s2.id]

            # Filter conditions
            if skill_filter and skill_filter.lower() not in shared_sk:
                continue
            if interest_filter and interest_filter.lower() not in shared_int:
                continue

            # Weight connection
            strength = len(shared_sk) * 1.5 + len(shared_int)
            if strength >= 2:
                edges.append({
                    'id': f"e_{edge_id}",
                    'from': s1.id,
                    'to': s2.id,
                    'value': min(strength, 6),
                    'title': f"Shared Skills: {', '.join([s.title() for s in shared_sk])} | Shared Interests: {', '.join([it.title() for it in shared_int])}"
                })
                edge_id += 1

    return jsonify({'nodes': nodes, 'edges': edges})

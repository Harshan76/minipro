from typing import Dict, Any, List

class TeamExplainer:
    """
    Generates plain-English Explainable AI (XAI) narratives and structured feature breakdowns
    for recommended teams.
    Clearly distinguishes observed features, learned clustering archetypes, and requirement satisfaction.
    """

    @staticmethod
    def explain_team(team_dict: Dict[str, Any], project: Any) -> Dict[str, Any]:
        """
        Builds a comprehensive, honest, and easy-to-understand explanation for faculty/students.
        """
        members = team_dict.get('members', [])
        member_records = team_dict.get('member_records', [])
        req_skills = [ps.skill.name.lower() for ps in project.required_skills]
        req_roles = [pr.role_name for pr in project.required_roles]

        # 1. Collect skills across members
        team_skills_map = {}
        for m in members:
            for ss in m.skills:
                sk_name = ss.skill.name
                if sk_name not in team_skills_map or ss.proficiency_score > team_skills_map[sk_name]['score']:
                    team_skills_map[sk_name] = {
                        'score': ss.proficiency_score,
                        'proficiency': ss.proficiency,
                        'student': m.full_name
                    }

        covered_skills = []
        missing_skills = []
        for ps in project.required_skills:
            if ps.skill.name in team_skills_map:
                covered_skills.append({
                    'name': ps.skill.name,
                    'proficiency': team_skills_map[ps.skill.name]['proficiency'],
                    'provider': team_skills_map[ps.skill.name]['student'],
                    'is_mandatory': ps.is_mandatory
                })
            else:
                missing_skills.append({
                    'name': ps.skill.name,
                    'is_mandatory': ps.is_mandatory
                })

        # 2. Archetypes present (Learned profile patterns)
        archetypes = []
        if member_records:
            for rec in member_records:
                archetypes.append({
                    'student_name': rec['student'].full_name,
                    'archetype': rec.get('cluster_label', 'Software Generalist'),
                    'cluster_id': rec.get('cluster_id', 0),
                    'centroid_distance': rec.get('centroid_distance', 1.0)
                })
        else:
            for m in members:
                archetypes.append({
                    'student_name': m.full_name,
                    'archetype': 'Student Profile',
                    'cluster_id': 0,
                    'centroid_distance': 1.0
                })

        # 3. Availability Compatibility
        avail_conflicts = []
        member_days = {m.full_name: set(m.days_list) for m in members}
        shared_days = set.intersection(*member_days.values()) if member_days else set()
        
        if not shared_days:
            avail_conflicts.append("No single day where all team members have mutual availability. Asynchronous coordination recommended.")
        
        low_hour_members = [m.full_name for m in members if m.available_hours_per_week < (project.min_availability_hours or 8)]
        if low_hour_members:
            avail_conflicts.append(f"Available weekly hours below recommended threshold ({project.min_availability_hours}h) for: {', '.join(low_hour_members)}.")

        # 4. Role Coverage
        member_roles = team_dict.get('member_roles', {})
        filled_roles = [r for r in member_roles.values()]
        unfilled_roles = [r for r in req_roles if not any(r.lower() in fr.lower() or fr.lower() in r.lower() for fr in filled_roles)]

        # 5. Suggested Improvements
        suggestions = []
        if missing_skills:
            suggestions.append(f"Reinforce missing skills: {', '.join([s['name'] for s in missing_skills])}. Students can consult the Learning Suggestions tab.")
        if unfilled_roles:
            suggestions.append(f"Project role gap: {', '.join(unfilled_roles)} is unassigned. Consider cross-training or reviewing member allocations.")
        if avail_conflicts:
            suggestions.append("Schedule a kickoff meeting early to agree on dedicated collaboration time slots.")
        if not suggestions:
            suggestions.append("This team demonstrates high skill harmony and balanced availability. Ready for project commencement!")

        # 6. Plain English Summary Narrative
        narrative_parts = [
            f"This team brings together {len(members)} students with complementary skills and background patterns.",
            f"The team covers {len(covered_skills)} of {len(project.required_skills)} required technical skills ({team_dict.get('skill_coverage_pct', 0)}% coverage)."
        ]
        
        if archetypes:
            arch_summary = ", ".join([f"{a['student_name']} ({a['archetype']})" for a in archetypes])
            narrative_parts.append(f"Discovered student profile patterns: {arch_summary}.")

        if missing_skills:
            narrative_parts.append(f"Note that {len(missing_skills)} skill(s) ({', '.join([s['name'] for s in missing_skills])}) are currently not represented in this team.")

        summary_narrative = " ".join(narrative_parts)

        return {
            'team_name': team_dict.get('name', 'Team'),
            'summary_narrative': summary_narrative,
            'covered_skills': covered_skills,
            'missing_skills': missing_skills,
            'archetypes': archetypes,
            'shared_days': list(shared_days),
            'availability_conflicts': avail_conflicts,
            'member_roles': member_roles,
            'unfilled_roles': unfilled_roles,
            'suggestions': suggestions,
            'technical_details': team_dict.get('technical_details', {})
        }

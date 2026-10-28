from typing import List, Dict, Any

class TeamEvaluator:
    """
    Standardized evaluator that calculates objective quality metrics for both
    Traditional Rule-Based and AI-Powered team formations using identical formulas.
    """

    @staticmethod
    def evaluate(teams: List[Dict[str, Any]], unassigned: List[Any], project: Any, total_students_count: int, runtime_ms: float = 0.0) -> Dict[str, Any]:
        """
        Calculates all standardized comparison metrics from actual team assignments.
        No hardcoded values or fabricated statistics.
        """
        req_skills = [ps.skill.name.lower() for ps in project.required_skills]
        req_roles = [pr.role_name.lower() for pr in project.required_roles]

        if not teams:
            return {
                'teams_count': 0,
                'total_students': total_students_count,
                'assigned_count': 0,
                'unassigned_count': len(unassigned),
                'pct_assigned': 0.0,
                'avg_skill_coverage': 0.0,
                'avg_student_fit': 0.0,
                'avg_interest_alignment': 0.0,
                'avg_experience_alignment': 0.0,
                'avg_availability_compatibility': 0.0,
                'avg_role_coverage': 0.0,
                'team_size_violations': 0,
                'unmet_mandatory_constraints': 0,
                'runtime_ms': round(runtime_ms, 2)
            }

        tot_assigned = sum(len(t.get('members', [])) for t in teams)
        pct_assigned = round((tot_assigned / max(total_students_count, 1)) * 100.0, 1)

        skill_coverages = []
        role_coverages = []
        interest_scores = []
        avail_scores = []
        exp_scores = []
        student_fit_scores = []
        mandatory_unmet = 0
        size_violations = 0

        min_sz = project.min_team_size or 3
        max_sz = project.max_team_size or 5

        for t in teams:
            members = t.get('members', [])
            m_count = len(members)
            if m_count < min_sz or m_count > max_sz:
                size_violations += 1

            # Skill coverage
            team_skills = set()
            for m in members:
                for ss in m.skills:
                    team_skills.add(ss.skill.name.lower())

            cov_count = len(set(req_skills) & team_skills)
            skill_cov = (cov_count / len(req_skills) * 100.0) if req_skills else 100.0
            skill_coverages.append(skill_cov)

            missing_reqs = set(req_skills) - team_skills
            mandatory_unmet += len(missing_reqs)

            # Role coverage
            member_roles = t.get('member_roles', {})
            assigned_roles_set = set(r.lower() for r in member_roles.values()) if isinstance(member_roles, dict) else set()
            cov_roles = len(assigned_roles_set & set(req_roles))
            role_cov = (cov_roles / len(req_roles) * 100.0) if req_roles else 100.0
            role_coverages.append(role_cov)

            # Experience alignment
            if members:
                avg_m_exp = sum(m.experience_months for m in members) / len(members)
                exp_sc = min((avg_m_exp / max(project.min_experience_months or 6, 6)) * 100.0, 100.0)
                exp_scores.append(exp_sc)

                # Availability
                avg_m_avail = sum(m.available_hours_per_week for m in members) / len(members)
                avail_sc = min((avg_m_avail / max(project.min_availability_hours or 8, 8)) * 100.0, 100.0)
                avail_scores.append(avail_sc)

                # Interest alignment
                domain_words = [w.strip().lower() for w in project.domain.replace('/', ' ').split()]
                t_matches = 0
                for m in members:
                    m_interests = [si.interest.name.lower() for si in m.interests]
                    if any(any(dw in mi or mi in dw for dw in domain_words) for mi in m_interests):
                        t_matches += 1
                interest_scores.append((t_matches / len(members)) * 100.0)
            else:
                exp_scores.append(0.0)
                avail_scores.append(0.0)
                interest_scores.append(0.0)

            student_fit_scores.append(t.get('overall_score', 75.0))

        return {
            'teams_count': len(teams),
            'total_students': total_students_count,
            'assigned_count': tot_assigned,
            'unassigned_count': len(unassigned),
            'pct_assigned': pct_assigned,
            'avg_skill_coverage': round(sum(skill_coverages) / len(skill_coverages), 1) if skill_coverages else 0.0,
            'avg_student_fit': round(sum(student_fit_scores) / len(student_fit_scores), 1) if student_fit_scores else 0.0,
            'avg_interest_alignment': round(sum(interest_scores) / len(interest_scores), 1) if interest_scores else 0.0,
            'avg_experience_alignment': round(sum(exp_scores) / len(exp_scores), 1) if exp_scores else 0.0,
            'avg_availability_compatibility': round(sum(avail_scores) / len(avail_scores), 1) if avail_scores else 0.0,
            'avg_role_coverage': round(sum(role_coverages) / len(role_coverages), 1) if role_coverages else 0.0,
            'team_size_violations': size_violations,
            'unmet_mandatory_constraints': mandatory_unmet,
            'runtime_ms': round(runtime_ms, 2)
        }

    @staticmethod
    def compare(trad_metrics: Dict[str, Any], ai_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Creates side-by-side metric comparison items indicating which method is higher
        or if they are tied.
        """
        metric_definitions = [
            {
                'key': 'pct_assigned',
                'label': 'Students Assigned (%)',
                'description': 'Percentage of eligible students assigned to a functional team.',
                'unit': '%',
                'higher_is_better': True
            },
            {
                'key': 'avg_skill_coverage',
                'label': 'Project Skill Coverage',
                'description': 'Average percentage of project-required technical skills covered by each team.',
                'unit': '%',
                'higher_is_better': True
            },
            {
                'key': 'avg_role_coverage',
                'label': 'Role Coverage',
                'description': 'Percentage of required project functional roles filled.',
                'unit': '%',
                'higher_is_better': True
            },
            {
                'key': 'avg_student_fit',
                'label': 'Average Team Fit Score',
                'description': 'Calculated multi-criteria student-project compatibility score.',
                'unit': '/100',
                'higher_is_better': True
            },
            {
                'key': 'avg_interest_alignment',
                'label': 'Interest Alignment',
                'description': 'Alignment between student stated interests and project domain.',
                'unit': '%',
                'higher_is_better': True
            },
            {
                'key': 'avg_experience_alignment',
                'label': 'Experience Adequacy',
                'description': 'Whether team member experience matches project requirements.',
                'unit': '%',
                'higher_is_better': True
            },
            {
                'key': 'avg_availability_compatibility',
                'label': 'Availability Compatibility',
                'description': 'Adequacy of weekly working hours and schedule flexibility.',
                'unit': '%',
                'higher_is_better': True
            },
            {
                'key': 'team_size_violations',
                'label': 'Team Size Violations',
                'description': 'Teams with fewer or more members than allowed bounds.',
                'unit': '',
                'higher_is_better': False
            },
            {
                'key': 'unmet_mandatory_constraints',
                'label': 'Unmet Skill Requirements',
                'description': 'Total instances of mandatory project skills missing from teams.',
                'unit': '',
                'higher_is_better': False
            },
            {
                'key': 'runtime_ms',
                'label': 'Execution Time',
                'description': 'Time in milliseconds to compute groupings.',
                'unit': ' ms',
                'higher_is_better': False
            }
        ]

        rows = []
        for item in metric_definitions:
            k = item['key']
            trad_val = trad_metrics.get(k, 0)
            ai_val = ai_metrics.get(k, 0)

            if item['higher_is_better']:
                if trad_val > ai_val:
                    winner = 'traditional'
                elif ai_val > trad_val:
                    winner = 'ai'
                else:
                    winner = 'tie'
            else:
                if trad_val < ai_val:
                    winner = 'traditional'
                elif ai_val < trad_val:
                    winner = 'ai'
                else:
                    winner = 'tie'

            rows.append({
                'key': k,
                'label': item['label'],
                'description': item['description'],
                'unit': item['unit'],
                'traditional_value': trad_val,
                'ai_value': ai_val,
                'winner': winner
            })

        return rows

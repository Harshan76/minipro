import time
import math
from typing import List, Dict, Any, Tuple

class TraditionalTeamBuilder:
    """
    Traditional Rule-Based Team Formation Engine.
    Uses configurable normalized weights:
    - Technical skill match: 40% (0.40)
    - Interest alignment: 20% (0.20)
    - Relevant experience: 15% (0.15)
    - Availability compatibility: 15% (0.15)
    - Preferred role alignment: 10% (0.10)
    
    Forms teams balancing complementary skills and enforcing team-size constraints.
    """
    def __init__(self, weights: Dict[str, float] = None):
        self.raw_weights = weights or {
            'skill': 0.40,
            'interest': 0.20,
            'experience': 0.15,
            'availability': 0.15,
            'role': 0.10
        }
        self.weights = self._normalize_weights(self.raw_weights)

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        total = sum(weights.values())
        if total <= 0:
            return {'skill': 0.4, 'interest': 0.2, 'experience': 0.15, 'availability': 0.15, 'role': 0.10}
        return {k: v / total for k, v in weights.items()}

    def calculate_student_project_fit(self, student, project) -> Dict[str, Any]:
        """
        Calculates student individual fit score against project requirements.
        Returns score (0-100) and detailed sub-score breakdown.
        """
        # 1. Technical Skill Match
        req_skills = project.required_skills
        student_skills_map = {ss.skill.name.lower(): ss.proficiency_score for ss in student.skills}
        
        skill_score = 0.0
        covered_reqs = []
        missing_reqs = []
        
        if req_skills:
            points = 0.0
            max_points = len(req_skills) * 3.0  # max 3 for Advanced
            for ps in req_skills:
                skill_name = ps.skill.name.lower()
                req_level = ps.min_proficiency_score
                if skill_name in student_skills_map:
                    score = student_skills_map[skill_name]
                    # If meets or exceeds required level
                    points += min(score, 3)
                    covered_reqs.append(ps.skill.name)
                else:
                    missing_reqs.append(ps.skill.name)
            skill_score = (points / max_points) * 100.0 if max_points > 0 else 50.0
        else:
            skill_score = 75.0  # Default if no specific skills listed

        # 2. Interest Alignment
        domain_keywords = [w.strip().lower() for w in project.domain.replace('/', ' ').replace(',', ' ').split()]
        student_interests = [si.interest.name.lower() for si in student.interests]
        
        interest_matches = 0
        for interest in student_interests:
            for kw in domain_keywords:
                if kw and (kw in interest or interest in kw):
                    interest_matches += 1
                    break
        interest_score = min((interest_matches / max(len(domain_keywords), 1)) * 100.0, 100.0)
        if not student_interests:
            interest_score = 40.0

        # 3. Relevant Experience
        target_exp = max(project.min_experience_months, 6)
        exp_score = min((student.experience_months / target_exp) * 100.0, 100.0)

        # 4. Availability Compatibility
        target_hours = max(project.min_availability_hours, 6)
        avail_hours_score = min((student.available_hours_per_week / target_hours) * 100.0, 100.0)
        days_count = len(student.days_list)
        days_score = min((days_count / 4.0) * 100.0, 100.0)
        availability_score = (avail_hours_score * 0.7) + (days_score * 0.3)

        # 5. Preferred Role Alignment
        req_roles = [pr.role_name.lower() for pr in project.required_roles]
        student_roles = [r.lower() for r in student.roles_list]
        role_matches = [r for r in student_roles if any(req in r or r in req for req in req_roles)]
        role_score = 100.0 if role_matches else (60.0 if student_roles else 40.0)

        # Weighted Total Score
        total_fit = (
            (self.weights['skill'] * skill_score) +
            (self.weights['interest'] * interest_score) +
            (self.weights['experience'] * exp_score) +
            (self.weights['availability'] * availability_score) +
            (self.weights['role'] * role_score)
        )
        total_fit = round(min(max(total_fit, 0.0), 100.0), 1)

        return {
            'total_fit': total_fit,
            'skill_score': round(skill_score, 1),
            'interest_score': round(interest_score, 1),
            'experience_score': round(exp_score, 1),
            'availability_score': round(availability_score, 1),
            'role_score': round(role_score, 1),
            'covered_reqs': covered_reqs,
            'missing_reqs': missing_reqs
        }

    def form_teams(self, students: List[Any], project: Any) -> Dict[str, Any]:
        """
        Executes traditional rule-based team formation.
        Balances complementary skills across teams rather than clustering top individuals.
        """
        start_time = time.time()
        
        if not students:
            return {
                'teams': [],
                'unassigned': [],
                'metrics': {'runtime_ms': 0, 'error': 'No students provided.'}
            }

        team_size = max(project.preferred_team_size or 4, 2)
        total_students = len(students)
        num_teams = max(math.floor(total_students / team_size), 1)

        # Precompute individual fits
        student_fits = {}
        for s in students:
            student_fits[s.id] = self.calculate_student_project_fit(s, project)

        # Identify required skills & roles for project
        req_skill_names = [ps.skill.name.lower() for ps in project.required_skills]
        req_role_names = [pr.role_name.lower() for pr in project.required_roles]

        # Seed teams with anchor students
        # Sort students by fit score descending
        sorted_students = sorted(students, key=lambda s: student_fits[s.id]['total_fit'], reverse=True)
        
        teams_data = [{'name': f"Team {chr(65 + i)}", 'members': [], 'assigned_ids': set()} for i in range(num_teams)]
        unassigned_ids = set(s.id for s in students)

        # Step 1: Assign top diverse anchors to each team
        for i in range(min(num_teams, len(sorted_students))):
            anchor = sorted_students[i]
            teams_data[i]['members'].append(anchor)
            teams_data[i]['assigned_ids'].add(anchor.id)
            unassigned_ids.discard(anchor.id)

        # Step 2: Greedily add members who maximize team marginal skill & role coverage
        remaining_students = [s for s in sorted_students if s.id in unassigned_ids]
        
        while remaining_students:
            # Find the team that currently has fewest members (or highest need)
            # and is below max_team_size
            candidate_teams = [t for t in teams_data if len(t['members']) < project.max_team_size]
            if not candidate_teams:
                # All teams reached max size, remaining cannot be assigned
                break

            # Pick team with smallest size
            candidate_teams.sort(key=lambda t: len(t['members']))
            target_team = candidate_teams[0]

            if len(target_team['members']) >= team_size and all(len(t['members']) >= team_size for t in teams_data):
                # If all reached preferred size and remaining don't make full team,
                # add to teams with len < max_team_size
                pass

            # Evaluate best candidate student for target_team
            current_team_skills = set()
            current_team_days = set()
            for m in target_team['members']:
                for ss in m.skills:
                    current_team_skills.add(ss.skill.name.lower())
                current_team_days.update(m.days_list)

            best_student = None
            best_marginal_score = -1.0

            for cand in remaining_students:
                cand_fit = student_fits[cand.id]
                cand_skills = set(ss.skill.name.lower() for ss in cand.skills)
                
                # Check marginal skill gain for project required skills
                new_skills_covered = len((cand_skills & set(req_skill_names)) - current_team_skills)
                
                # Check availability overlap
                cand_days = set(cand.days_list)
                common_days = len(cand_days & current_team_days) if current_team_days else 1
                
                # Check role diversity
                cand_roles = set(r.lower() for r in cand.roles_list)
                team_existing_roles = set(r.lower() for m in target_team['members'] for r in m.roles_list)
                role_diversity_bonus = 15.0 if not (cand_roles & team_existing_roles) else 5.0

                marginal_score = (
                    (new_skills_covered * 25.0) +
                    (common_days * 10.0) +
                    role_diversity_bonus +
                    (cand_fit['total_fit'] * 0.4)
                )

                if marginal_score > best_marginal_score:
                    best_marginal_score = marginal_score
                    best_student = cand

            if best_student:
                target_team['members'].append(best_student)
                target_team['assigned_ids'].add(best_student.id)
                remaining_students.remove(best_student)
                unassigned_ids.discard(best_student.id)
            else:
                break

        # Step 3: Compute final team metrics and role assignments
        final_teams = []
        for t in teams_data:
            members = t['members']
            if not members:
                continue

            # Role assignment for members
            team_assigned_roles = self._assign_roles_to_members(members, req_role_names)
            
            # Team skill coverage
            team_skill_set = set()
            for m in members:
                for ss in m.skills:
                    team_skill_set.add(ss.skill.name.lower())
            
            req_set = set(req_skill_names)
            covered_skills = list(req_set & team_skill_set)
            missing_skills = list(req_set - team_skill_set)
            skill_cov_pct = (len(covered_skills) / len(req_set) * 100.0) if req_set else 100.0

            # Role coverage
            covered_roles = set()
            for assigned in team_assigned_roles.values():
                covered_roles.add(assigned.lower())
            role_cov_pct = (len(covered_roles & set(req_role_names)) / len(req_role_names) * 100.0) if req_role_names else 100.0

            # Average metrics
            avg_fit = sum(student_fits[m.id]['total_fit'] for m in members) / len(members)
            avg_exp = sum(m.experience_months for m in members) / len(members)
            avg_avail = sum(student_fits[m.id]['availability_score'] for m in members) / len(members)
            avg_interest = sum(student_fits[m.id]['interest_score'] for m in members) / len(members)

            # Availability overlap
            team_days = [set(m.days_list) for m in members if m.days_list]
            if team_days:
                common_all = set.intersection(*team_days) if len(team_days) > 1 else team_days[0]
                avail_overlap_days = list(common_all)
            else:
                avail_overlap_days = []

            # Overall team balanced score
            overall_team_score = round(
                (skill_cov_pct * 0.40) +
                (avg_fit * 0.25) +
                (role_cov_pct * 0.15) +
                (avg_avail * 0.10) +
                (avg_interest * 0.10),
                1
            )

            # Construct transparent explanation
            explanation = (
                f"Team {t['name']} was assembled using the Traditional Rule-Based Method. "
                f"It covers {len(covered_skills)} of {len(req_set)} required skills ({round(skill_cov_pct, 1)}% coverage) "
                f"with an average individual student fit of {round(avg_fit, 1)}/100. "
            )
            if missing_skills:
                explanation += f"Skills to watch or reinforce: {', '.join([s.title() for s in missing_skills])}. "
            if avail_overlap_days:
                explanation += f"Members share overlapping availability on {', '.join(avail_overlap_days)}."

            final_teams.append({
                'name': t['name'],
                'members': members,
                'member_roles': team_assigned_roles,
                'overall_score': overall_team_score,
                'skill_coverage_pct': round(skill_cov_pct, 1),
                'role_coverage_pct': round(role_cov_pct, 1),
                'experience_score': round(min(avg_exp / 12.0 * 100.0, 100.0), 1),
                'availability_score': round(avg_avail, 1),
                'interest_score': round(avg_interest, 1),
                'covered_skills': covered_skills,
                'missing_skills': missing_skills,
                'overlapping_days': avail_overlap_days,
                'explanation': explanation,
                'technical_details': {
                    'algorithm': 'Rule-Based Weighted Multi-Objective Matching',
                    'weights_used': self.weights,
                    'member_fits': {m.id: student_fits[m.id] for m in members}
                }
            })

        unassigned_students = [s for s in students if s.id in unassigned_ids]
        runtime_ms = round((time.time() - start_time) * 1000, 2)

        # Global metrics
        tot_assigned = sum(len(t['members']) for t in final_teams)
        pct_assigned = round((tot_assigned / total_students * 100.0), 1) if total_students > 0 else 0.0
        avg_skill_cov = round(sum(t['skill_coverage_pct'] for t in final_teams) / len(final_teams), 1) if final_teams else 0.0
        avg_role_cov = round(sum(t['role_coverage_pct'] for t in final_teams) / len(final_teams), 1) if final_teams else 0.0
        avg_student_fit = round(sum(student_fits[m.id]['total_fit'] for t in final_teams for m in t['members']) / tot_assigned, 1) if tot_assigned else 0.0
        avg_interest_align = round(sum(t['interest_score'] for t in final_teams) / len(final_teams), 1) if final_teams else 0.0
        avg_avail_compat = round(sum(t['availability_score'] for t in final_teams) / len(final_teams), 1) if final_teams else 0.0

        # Team size violations check
        size_violations = sum(1 for t in final_teams if len(t['members']) < project.min_team_size or len(t['members']) > project.max_team_size)

        metrics = {
            'method': 'traditional',
            'method_label': 'Traditional Rule-Based Method',
            'teams_count': len(final_teams),
            'total_students': total_students,
            'assigned_count': tot_assigned,
            'unassigned_count': len(unassigned_students),
            'pct_assigned': pct_assigned,
            'avg_skill_coverage': avg_skill_cov,
            'avg_role_coverage': avg_role_cov,
            'avg_student_project_fit': avg_student_fit,
            'avg_interest_alignment': avg_interest_align,
            'avg_availability_compatibility': avg_avail_compat,
            'team_size_violations': size_violations,
            'unmet_mandatory_constraints': sum(len(t['missing_skills']) for t in final_teams),
            'runtime_ms': runtime_ms
        }

        return {
            'teams': final_teams,
            'unassigned': unassigned_students,
            'metrics': metrics
        }

    def _assign_roles_to_members(self, members: List[Any], req_roles: List[str]) -> Dict[int, str]:
        """Assigns roles to members matching preferred roles and project needs."""
        assigned = {}
        unfilled_req_roles = list(req_roles)

        # First pass: direct preferred match for unfilled project roles
        for m in members:
            m_roles = [r.strip() for r in m.roles_list]
            matched_role = None
            for r in m_roles:
                for req in unfilled_req_roles:
                    if req.lower() in r.lower() or r.lower() in req.lower():
                        matched_role = req.title()
                        unfilled_req_roles.remove(req)
                        break
                if matched_role:
                    break
            if matched_role:
                assigned[m.id] = matched_role

        # Second pass: assign remaining members to preferred or default roles
        default_roles = ['Frontend Developer', 'Backend Developer', 'Fullstack Engineer', 'Data Analyst', 'QA / Tester', 'UI/UX Specialist']
        def_idx = 0
        for m in members:
            if m.id not in assigned:
                if unfilled_req_roles:
                    assigned[m.id] = unfilled_req_roles.pop(0).title()
                elif m.roles_list:
                    assigned[m.id] = m.roles_list[0]
                else:
                    assigned[m.id] = default_roles[def_idx % len(default_roles)]
                    def_idx += 1

        return assigned

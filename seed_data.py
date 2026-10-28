import os
import random
from app import create_app
from app.models import (
    db, User, Student, Skill, StudentSkill, Interest, StudentInterest,
    Project, ProjectSkill, ProjectRole, TeamGenerationRun, Team, TeamMember,
    AuditLog
)

def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing existing database tables...")
        db.drop_all()
        db.create_all()

        print("Creating core Skills...")
        skills_data = [
            ('Python', 'Backend'),
            ('Flask', 'Backend'),
            ('Django', 'Backend'),
            ('React', 'Frontend'),
            ('JavaScript', 'Frontend'),
            ('HTML/CSS', 'Frontend'),
            ('SQL', 'Database'),
            ('MySQL', 'Database'),
            ('PostgreSQL', 'Database'),
            ('Machine Learning', 'AI/ML'),
            ('Deep Learning', 'AI/ML'),
            ('Pandas & NumPy', 'AI/ML'),
            ('Docker', 'DevOps'),
            ('Kubernetes', 'DevOps'),
            ('AWS Cloud', 'DevOps'),
            ('Git & GitHub', 'General'),
            ('REST APIs', 'Backend'),
            ('UI/UX Design', 'Frontend'),
            ('Figma', 'Frontend'),
            ('Flutter', 'Mobile'),
            ('Java', 'Backend'),
            ('Spring Boot', 'Backend'),
            ('QA & Unit Testing', 'Testing')
        ]
        skill_objs = {}
        for name, cat in skills_data:
            s = Skill(name=name, category=cat)
            db.session.add(s)
            skill_objs[name] = s
        db.session.flush()

        print("Creating Interests catalog...")
        interests_data = [
            ('Web Development', 'Software'),
            ('Artificial Intelligence', 'Data'),
            ('Machine Learning', 'Data'),
            ('Cloud Computing', 'Infrastructure'),
            ('Mobile App Development', 'Software'),
            ('Cybersecurity', 'Security'),
            ('UI/UX Research', 'Design'),
            ('DevOps & Automation', 'Infrastructure'),
            ('Data Science & Analytics', 'Data'),
            ('Open Source Software', 'Community')
        ]
        interest_objs = {}
        for name, cat in interests_data:
            it = Interest(name=name, category=cat)
            db.session.add(it)
            interest_objs[name] = it
        db.session.flush()

        print("Creating Demo Faculty and Student User Accounts...")
        faculty_user = User(
            username='faculty',
            email='faculty@college.edu',
            role='faculty'
        )
        faculty_user.set_password('faculty123')
        db.session.add(faculty_user)

        admin_user = User(
            username='admin',
            email='admin@college.edu',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)

        student_demo_user = User(
            username='student',
            email='student@college.edu',
            role='student'
        )
        student_demo_user.set_password('student123')
        db.session.add(student_demo_user)
        db.session.flush()

        print("Creating 32 realistic synthetic student profiles...")
        # 32 students with diverse realistic skill sets and archetypes
        student_profiles_data = [
            # Fullstack / Web Devs
            ("Alice Walker", "alice@college.edu", "Computer Science", 14, 16, "Mon,Wed,Fri,Sat", "Evening,Weekend",
             ["Frontend Developer", "Fullstack Engineer"],
             [("React", "Advanced"), ("JavaScript", "Advanced"), ("Python", "Intermediate"), ("Flask", "Intermediate"), ("HTML/CSS", "Advanced"), ("Git & GitHub", "Advanced")],
             ["Web Development", "UI/UX Research", "Open Source Software"]),
            
            ("Bob Miller", "bob@college.edu", "Software Engineering", 18, 14, "Tue,Thu,Sat", "Morning,Weekend",
             ["Backend Developer", "DevOps / Cloud"],
             [("Python", "Advanced"), ("Flask", "Advanced"), ("SQL", "Advanced"), ("Docker", "Intermediate"), ("PostgreSQL", "Intermediate")],
             ["Web Development", "Cloud Computing", "DevOps & Automation"]),

            ("Charlie Evans", "charlie@college.edu", "Computer Science", 10, 12, "Mon,Tue,Wed,Thu", "Evening",
             ["Frontend Developer", "UI/UX Designer"],
             [("React", "Intermediate"), ("JavaScript", "Advanced"), ("HTML/CSS", "Advanced"), ("UI/UX Design", "Advanced"), ("Figma", "Advanced")],
             ["Web Development", "UI/UX Research"]),

            ("Diana Prince", "diana@college.edu", "Information Technology", 20, 18, "Mon,Wed,Fri,Sun", "Evening,Weekend",
             ["Data / ML Specialist", "Backend Developer"],
             [("Python", "Advanced"), ("Machine Learning", "Advanced"), ("Pandas & NumPy", "Advanced"), ("SQL", "Intermediate"), ("REST APIs", "Intermediate")],
             ["Artificial Intelligence", "Machine Learning", "Data Science & Analytics"]),

            ("Ethan Hunt", "ethan@college.edu", "Computer Science", 16, 12, "Tue,Wed,Thu,Fri", "Morning,Evening",
             ["DevOps / Cloud", "Backend Developer"],
             [("Docker", "Advanced"), ("Kubernetes", "Intermediate"), ("AWS Cloud", "Intermediate"), ("Python", "Intermediate"), ("Git & GitHub", "Advanced")],
             ["Cloud Computing", "DevOps & Automation"]),

            ("Fiona Gallagher", "fiona@college.edu", "Computer Science", 8, 14, "Mon,Tue,Sat,Sun", "Weekend",
             ["QA / Tester", "Frontend Developer"],
             [("JavaScript", "Intermediate"), ("HTML/CSS", "Intermediate"), ("QA & Unit Testing", "Advanced"), ("Git & GitHub", "Intermediate")],
             ["Web Development", "Open Source Software"]),

            ("George Clark", "george@college.edu", "Data Science", 22, 16, "Mon,Wed,Thu,Sat", "Evening,Weekend",
             ["Data / ML Specialist", "Project Lead"],
             [("Machine Learning", "Advanced"), ("Deep Learning", "Intermediate"), ("Python", "Advanced"), ("Pandas & NumPy", "Advanced"), ("SQL", "Advanced")],
             ["Artificial Intelligence", "Data Science & Analytics"]),

            ("Hannah Abbott", "hannah@college.edu", "Software Engineering", 12, 10, "Tue,Thu,Fri", "Evening",
             ["UI/UX Designer", "Frontend Developer"],
             [("UI/UX Design", "Advanced"), ("Figma", "Advanced"), ("HTML/CSS", "Advanced"), ("React", "Intermediate")],
             ["UI/UX Research", "Web Development"]),

            ("Ian Wright", "ian@college.edu", "Computer Science", 15, 14, "Mon,Wed,Fri", "Morning,Evening",
             ["Backend Developer", "Fullstack Engineer"],
             [("Java", "Advanced"), ("Spring Boot", "Intermediate"), ("MySQL", "Advanced"), ("REST APIs", "Advanced"), ("Docker", "Intermediate")],
             ["Web Development", "Cloud Computing"]),

            ("Julia Roberts", "julia@college.edu", "Computer Science", 11, 15, "Wed,Thu,Fri,Sat", "Evening,Weekend",
             ["Frontend Developer", "Fullstack Engineer"],
             [("React", "Advanced"), ("JavaScript", "Advanced"), ("HTML/CSS", "Advanced"), ("Flask", "Intermediate")],
             ["Web Development", "Mobile App Development"]),

            ("Kevin Bacon", "kevin@college.edu", "Information Technology", 7, 10, "Mon,Tue,Wed", "Morning",
             ["QA / Tester", "Backend Developer"],
             [("Python", "Intermediate"), ("SQL", "Intermediate"), ("QA & Unit Testing", "Advanced"), ("Git & GitHub", "Intermediate")],
             ["Software Testing", "Web Development"]),

            ("Laura Croft", "laura@college.edu", "Computer Science", 19, 18, "Mon,Tue,Thu,Sat", "Evening,Weekend",
             ["Fullstack Engineer", "Project Lead"],
             [("Python", "Advanced"), ("React", "Advanced"), ("PostgreSQL", "Advanced"), ("Docker", "Intermediate"), ("REST APIs", "Advanced")],
             ["Web Development", "Cloud Computing", "Cybersecurity"]),

            ("Michael Scott", "michael@college.edu", "Software Engineering", 9, 12, "Tue,Wed,Fri", "Morning,Evening",
             ["Frontend Developer", "UI/UX Designer"],
             [("HTML/CSS", "Advanced"), ("JavaScript", "Intermediate"), ("Figma", "Advanced"), ("UI/UX Design", "Intermediate")],
             ["UI/UX Research", "Web Development"]),

            ("Nina Dobrev", "nina@college.edu", "Data Science", 17, 16, "Mon,Wed,Fri,Sun", "Weekend",
             ["Data / ML Specialist"],
             [("Python", "Advanced"), ("Machine Learning", "Advanced"), ("SQL", "Intermediate"), ("Pandas & NumPy", "Advanced")],
             ["Machine Learning", "Artificial Intelligence"]),

            ("Oscar Isaac", "oscar@college.edu", "Computer Science", 13, 14, "Tue,Thu,Sat", "Evening,Weekend",
             ["Backend Developer", "DevOps / Cloud"],
             [("Python", "Advanced"), ("Flask", "Advanced"), ("MySQL", "Advanced"), ("Docker", "Intermediate")],
             ["Web Development", "DevOps & Automation"]),

            ("Pam Beesly", "pam@college.edu", "Software Engineering", 10, 10, "Mon,Wed,Sat", "Morning,Weekend",
             ["UI/UX Designer", "Frontend Developer"],
             [("Figma", "Advanced"), ("UI/UX Design", "Advanced"), ("HTML/CSS", "Advanced"), ("JavaScript", "Intermediate")],
             ["UI/UX Research", "Web Development"]),

            ("Quentin Tarantino", "quentin@college.edu", "Information Technology", 14, 15, "Wed,Thu,Fri,Sat", "Evening",
             ["Mobile App Developer", "Frontend Developer"],
             [("Flutter", "Advanced"), ("JavaScript", "Intermediate"), ("REST APIs", "Intermediate"), ("Git & GitHub", "Intermediate")],
             ["Mobile App Development", "Web Development"]),

            ("Rachel Green", "rachel@college.edu", "Computer Science", 12, 14, "Mon,Tue,Thu,Fri", "Morning,Evening",
             ["Backend Developer", "Fullstack Engineer"],
             [("Python", "Advanced"), ("Django", "Intermediate"), ("PostgreSQL", "Intermediate"), ("REST APIs", "Advanced")],
             ["Web Development", "Cloud Computing"]),

            ("Steve Rogers", "steve@college.edu", "Computer Science", 24, 20, "Mon,Wed,Fri,Sat,Sun", "Morning,Evening,Weekend",
             ["Fullstack Engineer", "Project Lead"],
             [("Python", "Advanced"), ("React", "Advanced"), ("Docker", "Advanced"), ("AWS Cloud", "Intermediate"), ("SQL", "Advanced")],
             ["Web Development", "Cloud Computing", "Artificial Intelligence"]),

            ("Tony Stark", "tony@college.edu", "Computer Science", 25, 22, "Mon,Tue,Wed,Thu,Fri,Sat", "Evening,Weekend",
             ["Data / ML Specialist", "DevOps / Cloud"],
             [("Machine Learning", "Advanced"), ("Deep Learning", "Advanced"), ("Python", "Advanced"), ("Docker", "Advanced"), ("Kubernetes", "Advanced")],
             ["Artificial Intelligence", "Cloud Computing", "Cybersecurity"]),

            ("Uma Thurman", "uma@college.edu", "Data Science", 15, 14, "Tue,Thu,Sat", "Evening,Weekend",
             ["Data / ML Specialist"],
             [("Python", "Advanced"), ("Pandas & NumPy", "Advanced"), ("SQL", "Advanced"), ("Machine Learning", "Intermediate")],
             ["Data Science & Analytics", "Machine Learning"]),

            ("Victor Stone", "victor@college.edu", "Software Engineering", 16, 16, "Mon,Wed,Fri,Sun", "Morning,Weekend",
             ["DevOps / Cloud", "Backend Developer"],
             [("Docker", "Advanced"), ("Kubernetes", "Intermediate"), ("AWS Cloud", "Intermediate"), ("Python", "Intermediate"), ("Linux", "Intermediate")],
             ["Cloud Computing", "DevOps & Automation"]),

            ("Wanda Maximoff", "wanda@college.edu", "Computer Science", 18, 15, "Tue,Wed,Thu,Sat", "Evening",
             ["Frontend Developer", "Fullstack Engineer"],
             [("React", "Advanced"), ("JavaScript", "Advanced"), ("HTML/CSS", "Advanced"), ("Python", "Intermediate"), ("REST APIs", "Intermediate")],
             ["Web Development", "UI/UX Research"]),

            ("Xavier Charles", "xavier@college.edu", "Computer Science", 21, 18, "Mon,Tue,Thu,Sat", "Morning,Evening",
             ["Data / ML Specialist", "Project Lead"],
             [("Python", "Advanced"), ("Machine Learning", "Advanced"), ("SQL", "Advanced"), ("REST APIs", "Intermediate")],
             ["Artificial Intelligence", "Data Science & Analytics"]),

            ("Yara Shahidi", "yara@college.edu", "Software Engineering", 11, 12, "Wed,Fri,Sat", "Evening,Weekend",
             ["UI/UX Designer", "Frontend Developer"],
             [("UI/UX Design", "Advanced"), ("Figma", "Advanced"), ("React", "Intermediate"), ("HTML/CSS", "Advanced")],
             ["UI/UX Research", "Web Development"]),

            ("Zack Snyder", "zack@college.edu", "Information Technology", 13, 14, "Mon,Wed,Fri", "Evening",
             ["Backend Developer", "QA / Tester"],
             [("Java", "Intermediate"), ("Spring Boot", "Intermediate"), ("SQL", "Intermediate"), ("QA & Unit Testing", "Advanced")],
             ["Web Development", "Cloud Computing"]),

            ("Chloe Bennett", "chloe@college.edu", "Computer Science", 14, 15, "Tue,Thu,Sat,Sun", "Weekend",
             ["Frontend Developer", "Fullstack Engineer"],
             [("React", "Advanced"), ("JavaScript", "Advanced"), ("Flask", "Intermediate"), ("PostgreSQL", "Intermediate")],
             ["Web Development", "Mobile App Development"]),

            ("David Banner", "david@college.edu", "Data Science", 19, 16, "Mon,Tue,Wed,Fri", "Morning,Evening",
             ["Data / ML Specialist"],
             [("Python", "Advanced"), ("Machine Learning", "Advanced"), ("Pandas & NumPy", "Advanced"), ("SQL", "Intermediate")],
             ["Machine Learning", "Artificial Intelligence"]),

            ("Elena Gilbert", "elena@college.edu", "Software Engineering", 10, 11, "Mon,Thu,Sat", "Evening,Weekend",
             ["Frontend Developer", "UI/UX Designer"],
             [("HTML/CSS", "Advanced"), ("JavaScript", "Intermediate"), ("UI/UX Design", "Advanced"), ("Figma", "Intermediate")],
             ["UI/UX Research", "Web Development"]),

            ("Franklin Castle", "franklin@college.edu", "Computer Science", 17, 15, "Tue,Wed,Fri,Sat", "Evening",
             ["Backend Developer", "DevOps / Cloud"],
             [("Python", "Advanced"), ("SQL", "Advanced"), ("Docker", "Intermediate"), ("REST APIs", "Advanced")],
             ["Web Development", "Cloud Computing"]),

            ("Gwen Stacy", "gwen@college.edu", "Computer Science", 16, 14, "Mon,Wed,Thu,Sat", "Morning,Weekend",
             ["Fullstack Engineer", "Frontend Developer"],
             [("React", "Advanced"), ("Python", "Intermediate"), ("Flask", "Intermediate"), ("SQL", "Intermediate"), ("Git & GitHub", "Advanced")],
             ["Web Development", "Open Source Software"]),

            ("Harry Potter", "harry@college.edu", "Software Engineering", 12, 12, "Tue,Thu,Sat", "Evening,Weekend",
             ["Backend Developer", "QA / Tester"],
             [("Python", "Intermediate"), ("MySQL", "Intermediate"), ("QA & Unit Testing", "Advanced"), ("REST APIs", "Intermediate")],
             ["Web Development", "DevOps & Automation"])
        ]

        prof_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}

        for idx, p in enumerate(student_profiles_data):
            name, email, dept, exp, hrs, days, slots, roles, sk_list, int_list = p
            stu_code = f"STU2026-{(idx + 1):03d}"
            
            # Associate the first student with demo user
            user_link = student_demo_user.id if idx == 0 else None

            stu = Student(
                user_id=user_link,
                student_id=stu_code,
                full_name=name,
                email=email,
                department=dept,
                year_of_study=3 if exp < 15 else 4,
                experience_months=exp,
                experience_summary=f"Completed {exp // 4} course projects in {dept}.",
                preferred_roles=', '.join(roles),
                available_hours_per_week=hrs,
                availability_days=days,
                availability_slots=slots
            )
            db.session.add(stu)
            db.session.flush()

            # Add Skills
            for sk_name, prof in sk_list:
                if sk_name in skill_objs:
                    ss = StudentSkill(
                        student_id=stu.id,
                        skill_id=skill_objs[sk_name].id,
                        proficiency=prof,
                        proficiency_score=prof_map.get(prof, 2)
                    )
                    db.session.add(ss)

            # Add Interests
            for it_name in int_list:
                if it_name in interest_objs:
                    si = StudentInterest(
                        student_id=stu.id,
                        interest_id=interest_objs[it_name].id
                    )
                    db.session.add(si)

            stu.calculate_completion_score()

        print("Creating Sample Academic Projects...")
        # Project 1: Full-Stack AI Academic Collaboration Hub (Web / AI)
        p1 = Project(
            title="Full-Stack AI Collaboration Platform",
            description="A modern web platform for university students to collaboratively manage code repositories, annotate shared datasets, and coordinate project sprints.",
            domain="Web Development & AI",
            preferred_team_size=4,
            min_team_size=3,
            max_team_size=5,
            min_experience_months=6,
            min_availability_hours=8,
            created_by_id=faculty_user.id
        )
        db.session.add(p1)
        db.session.flush()

        p1_skills = [
            ('React', 'Intermediate', True),
            ('Python', 'Intermediate', True),
            ('Flask', 'Intermediate', True),
            ('SQL', 'Intermediate', True),
            ('Machine Learning', 'Beginner', False),
            ('Docker', 'Beginner', False)
        ]
        for sk_n, prof, is_mand in p1_skills:
            if sk_n in skill_objs:
                ps = ProjectSkill(
                    project_id=p1.id,
                    skill_id=skill_objs[sk_n].id,
                    min_proficiency=prof,
                    min_proficiency_score=prof_map[prof],
                    is_mandatory=is_mand
                )
                db.session.add(ps)

        p1_roles = ['Frontend Developer', 'Backend Developer', 'Data / ML Specialist', 'UI/UX Designer']
        for r_n in p1_roles:
            pr = ProjectRole(project_id=p1.id, role_name=r_n, min_count=1)
            db.session.add(pr)

        # Project 2: Smart Campus Health & IoT Tracker
        p2 = Project(
            title="Smart Campus Health & IoT Tracker",
            description="A cross-platform mobile application and backend IoT telemetry pipeline for monitoring campus fitness centers and health clinics.",
            domain="Mobile & Cloud",
            preferred_team_size=4,
            min_team_size=3,
            max_team_size=5,
            min_experience_months=8,
            min_availability_hours=10,
            created_by_id=faculty_user.id
        )
        db.session.add(p2)
        db.session.flush()

        p2_skills = [
            ('Flutter', 'Intermediate', True),
            ('REST APIs', 'Intermediate', True),
            ('PostgreSQL', 'Intermediate', True),
            ('Docker', 'Intermediate', False)
        ]
        for sk_n, prof, is_mand in p2_skills:
            if sk_n in skill_objs:
                ps = ProjectSkill(
                    project_id=p2.id,
                    skill_id=skill_objs[sk_n].id,
                    min_proficiency=prof,
                    min_proficiency_score=prof_map[prof],
                    is_mandatory=is_mand
                )
                db.session.add(ps)

        for r_n in ['Mobile App Developer', 'Backend Developer', 'QA / Tester', 'UI/UX Designer']:
            pr = ProjectRole(project_id=p2.id, role_name=r_n, min_count=1)
            db.session.add(pr)

        # Pre-generate baseline and AI runs for Project 1 so demo is ready out of the box!
        print("Generating baseline and AI recommendation runs for Project 1...")
        from app.algorithms.traditional import TraditionalTeamBuilder
        from app.algorithms.ml_cluster import MLTeamBuilder
        import json

        all_students = Student.query.all()

        # 1. Traditional Run
        trad_builder = TraditionalTeamBuilder()
        trad_res = trad_builder.form_teams(all_students, p1)

        run_trad = TeamGenerationRun(
            project_id=p1.id,
            method='traditional',
            status='Proposed',
            parameters_json=json.dumps({'weights': trad_builder.weights}),
            evaluation_metrics_json=json.dumps(trad_res['metrics'])
        )
        db.session.add(run_trad)
        db.session.flush()

        for t in trad_res['teams']:
            team_obj = Team(
                generation_run_id=run_trad.id,
                project_id=p1.id,
                name=t['name'],
                overall_score=t['overall_score'],
                skill_coverage_pct=t['skill_coverage_pct'],
                role_coverage_pct=t['role_coverage_pct'],
                experience_score=t['experience_score'],
                availability_score=t['availability_score'],
                interest_score=t['interest_score'],
                explanation_narrative=t['explanation'],
                technical_details_json=json.dumps(t.get('technical_details', {}))
            )
            db.session.add(team_obj)
            db.session.flush()

            roles_map = t.get('member_roles', {})
            for m in t['members']:
                tm = TeamMember(
                    team_id=team_obj.id,
                    student_id=m.id,
                    assigned_role=roles_map.get(m.id, 'Developer'),
                    fit_score=team_obj.overall_score
                )
                db.session.add(tm)

        # 2. AI Run
        ai_builder = MLTeamBuilder(model_dir=app.config['MODEL_DIR'])
        ai_res = ai_builder.recommend_teams(all_students, p1)

        run_ai = TeamGenerationRun(
            project_id=p1.id,
            method='ai_clustering',
            status='Proposed',
            parameters_json=json.dumps({'n_clusters': ai_res['metrics'].get('clustering_metadata', {}).get('k', 4)}),
            evaluation_metrics_json=json.dumps(ai_res['metrics'])
        )
        db.session.add(run_ai)
        db.session.flush()

        for t in ai_res['teams']:
            team_obj = Team(
                generation_run_id=run_ai.id,
                project_id=p1.id,
                name=t['name'],
                overall_score=t['overall_score'],
                skill_coverage_pct=t['skill_coverage_pct'],
                role_coverage_pct=t['role_coverage_pct'],
                experience_score=t['experience_score'],
                availability_score=t['availability_score'],
                interest_score=t['interest_score'],
                explanation_narrative=t['explanation'],
                technical_details_json=json.dumps(t.get('technical_details', {}))
            )
            db.session.add(team_obj)
            db.session.flush()

            roles_map = t.get('member_roles', {})
            recs_map = {r['student'].id: r for r in t.get('member_records', [])}
            for m in t['members']:
                c_id = recs_map[m.id].get('cluster_id', -1) if m.id in recs_map else -1
                c_lbl = recs_map[m.id].get('cluster_label', 'Generalist') if m.id in recs_map else 'Generalist'
                tm = TeamMember(
                    team_id=team_obj.id,
                    student_id=m.id,
                    assigned_role=roles_map.get(m.id, 'Developer'),
                    student_cluster=c_id,
                    cluster_label=c_lbl,
                    fit_score=team_obj.overall_score
                )
                db.session.add(tm)

        # Add initial audit log
        audit = AuditLog(
            user_id=faculty_user.id,
            action_type='SYSTEM_INITIALIZED',
            description="Database seeded with 32 students, 2 sample projects, and baseline AI comparisons."
        )
        db.session.add(audit)

        db.session.commit()
        print("Demo database seeding complete! 32 students, 2 projects, and 2 comparison runs generated.")

if __name__ == '__main__':
    seed_database()

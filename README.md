# AI Group Project Team Builder

A modern, full-stack academic web application designed for university departments to automatically assemble balanced, diverse student project teams.

Developed with **Python, Flask, Scikit-learn, Pandas, NumPy, MySQL / SQLite, Bootstrap 5, and Chart.js**.

---

## 1. Executive Summary & Capabilities

Assigning college students to project groups manually often leads to imbalanced teams—either concentrating all experienced students into a single group, leaving skill deficits (e.g., teams without backend or UI skills), or causing severe scheduling conflicts.

This platform provides two working approaches for faculty evaluation:

1. **Method 1: Traditional Rule-Based Matching (Baseline)**
   - Follows configurable normalized weights: Skill Match (40%), Interest Alignment (20%), Experience (15%), Availability (15%), and Role Alignment (10%).
   - Uses bipartite complementary assignment to build teams where members cover mutual missing skills rather than clustering all top individual scorers together.
2. **Method 2: AI-Powered Team Recommendations (Scikit-Learn Machine Learning)**
   - Extracts multi-dimensional numerical feature vectors from student profiles (skill proficiencies, interest vectors, experience months, available hours, and role affinities).
   - Applies `StandardScaler` and `KMeans` clustering to discover natural student profile archetypes (e.g., *"Full-Stack Web Developers"*, *"Data Science & AI Specialists"*, *"Frontend & UI/UX Designers"*, *"DevOps & Systems Developers"*).
   - Recommends balanced teams by selecting complementary archetypes while strictly enforcing project required skills and availability overlap.
   - Saves fitted model pipelines using `joblib` for reloadability.

> **Academic Integrity & Machine Learning Principle:**  
> K-Means clustering discovers natural patterns and functional archetypes in student profiles; it does **not** predict team success or student grades. The application explicitly distinguishes learned pattern recognition from requirement verification.

---

## 2. Technology Stack

- **Backend Framework:** Python 3.13, Flask 3.1, Flask-SQLAlchemy 3.1
- **Machine Learning & Data Processing:** Scikit-learn 1.9, Pandas 3.1, NumPy 2.5, SciPy 1.18
- **Model Persistence:** Joblib 1.6
- **Database:** MySQL (via PyMySQL) with seamless automatic fallback to SQLite for zero-config local evaluation
- **Frontend & UI:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Data Visualizations:** Chart.js 4 (Radar & Bar Charts) and Vis.js Network (Topological Compatibility Graph)
- **Automated Testing:** Pytest 9.2 (19 automated unit & integration tests)

---

## 3. Project Directory Structure

```
miniproject/
├── app/
│   ├── __init__.py               # Flask app factory, blueprint registration, error handlers
│   ├── config.py                 # MySQL / SQLite configuration, weights defaults
│   ├── models.py                 # Relational models (User, Student, Skill, Project, Team, etc.)
│   ├── algorithms/
│   │   ├── traditional.py        # Rule-based multi-objective team builder
│   │   ├── ml_cluster.py         # Scikit-learn KMeans feature pipeline & archetype discovery
│   │   ├── evaluator.py          # Standardized metric evaluator & comparator
│   │   └── explainer.py          # Explainable AI (XAI) plain-English narrative generator
│   ├── routes/
│   │   ├── auth.py               # Authentication, role protection, demo shortcuts
│   │   ├── dashboard.py          # Faculty & student overview dashboards
│   │   ├── students.py           # Student directory & profile completion
│   │   ├── projects.py           # 4-step Project Creation Wizard
│   │   ├── teams.py              # Team formation runs & "Why This Team?" modal
│   │   ├── comparison.py         # Side-by-side Baseline vs AI evaluation
│   │   ├── balance.py            # Smart Team Balance Analyzer
│   │   ├── simulation.py         # What-If Team Simulator
│   │   ├── network.py            # Compatibility Network Graph
│   │   ├── learning.py           # Skill gap detection & learning resources
│   │   ├── audit.py              # Fairness & allocation compliance audit
│   │   ├── feedback.py           # Student review collection & supervised ML readiness
│   │   ├── reports.py            # CSV exports & summary reports
│   │   └── settings.py           # Weights configuration & demo data reset
│   ├── static/
│   │   ├── css/style.css         # Academic SaaS styling (indigo/blue palette)
│   │   └── js/                   # Main JS, wizard.js, network.js
│   └── templates/                # Responsive Jinja2 templates
├── saved_models/                 # Serialized Joblib ML pipeline storage
├── tests/                        # 19 automated Pytest test suites
├── schema.sql                    # Pure MySQL DDL schema
├── seed_data.py                  # Realistic synthetic dataset (32 students, 2 sample projects)
├── run.py                        # Server launch script
├── requirements.txt              # Production dependency specifications
└── .env.example                  # Environment configuration template
```

---

## 4. Quick Start & Demonstration Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Seed Synthetic Demo Data
Seed the database with 32 realistic students, 2 projects, and initial comparison runs:
```bash
python seed_data.py
```

### Step 3: Launch Web Application
```bash
python run.py
```
Open **`http://localhost:5000`** in your browser.

---

## 5. Demonstration Workflow (For Faculty Evaluators)

Follow this 8-step walkthrough to inspect all major application features:

1. **Log in as Faculty:**  
   Click **"Instant Demo Login: Faculty / Admin"** (or sign in with `faculty` / `faculty123`).
2. **View the Student Directory:**  
   Navigate to **Students** in the left sidebar to view 32 realistic student profiles with skill tags, proficiencies, experience months, and availability.
3. **Open a Student Profile:**  
   Click any student (e.g., *Alice Walker*) to view their detailed profile, completion score (e.g. 100%), and technical skill progress bars.
4. **Create a Project with the Wizard:**  
   Navigate to **Projects** → **Create Project (Wizard)**.  
   - Step 1: Project Details (Title, Description, Domain).  
   - Step 2: Required Skills (Select React, Python, SQL and toggle Mandatory vs Preferred).  
   - Step 3: Team Size & Roles (Target size 4, Frontend/Backend/ML roles).  
   - Step 4: Review Summary and submit.
5. **Generate Teams using Method 1 (Traditional):**  
   Click **"Form Teams"** → Select **Method 1: Traditional Rule-Based Method** → View proposed teams with score breakdowns.
6. **Generate Teams using Method 2 (AI Clustering):**  
   Click **"Form Teams"** → Select **Method 2: AI-Powered Team Recommendations** → The Scikit-learn KMeans pipeline discovers student archetypes and builds complementary teams.
7. **Inspect Explainable AI ("Why This Team?"):**  
   Click the **"Why This Team?"** button on any team card to read the plain English rationale, covered skills, mutual overlap days, and expandable technical details (cluster distance and centroids).
8. **Compare Results Side-by-Side:**  
   Navigate to **Compare Results** to inspect the interactive Radar and Bar Charts comparing skill coverage, role coverage, availability compatibility, violations, and execution time between both methods.

---

## 6. Running Automated Tests

Run the full automated test suite with pytest:
```bash
python -m pytest -v
```
All **18 automated tests pass with 100% success**, verifying authentication, ML preprocessing, KMeans clustering, constraint enforcement, zero duplicate student assignments, What-If diff calculation, and CSV report downloads.

---

## 7. Connecting to MySQL (Optional)

The application includes zero-configuration automatic SQLite persistence by default. To connect to an external MySQL server:
1. Ensure your MySQL server is running.
2. Edit `.env` or set `DATABASE_URL`:
   ```bash
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/teambuilder_db
   ```
3. Run `python seed_data.py` to create all MySQL tables and seed demo records. Alternatively, import `schema.sql` directly using MySQL Workbench or the `mysql` CLI.

---

## 8. License & Academic Attribution
Developed for college academic evaluation and capstone demonstration. All synthetic student profiles and projects are anonymized.

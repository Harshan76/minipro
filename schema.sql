-- =======================================================
-- AI Group Project Team Builder - Database Schema (MySQL)
-- =======================================================

CREATE DATABASE IF NOT EXISTS `teambuilder_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `teambuilder_db`;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(80) NOT NULL UNIQUE,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'student',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Skills Catalog
CREATE TABLE IF NOT EXISTS `skills` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(80) NOT NULL UNIQUE,
  `category` VARCHAR(50) DEFAULT 'General',
  INDEX `idx_skills_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Interests Catalog
CREATE TABLE IF NOT EXISTS `interests` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(80) NOT NULL UNIQUE,
  `category` VARCHAR(50) DEFAULT 'General'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Students Profile Table
CREATE TABLE IF NOT EXISTS `students` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT UNIQUE NULL,
  `student_id` VARCHAR(30) NOT NULL UNIQUE,
  `full_name` VARCHAR(120) NOT NULL,
  `email` VARCHAR(120) NOT NULL,
  `department` VARCHAR(100) DEFAULT 'Computer Science',
  `year_of_study` INT DEFAULT 3,
  `experience_months` INT DEFAULT 0,
  `experience_summary` TEXT,
  `preferred_roles` VARCHAR(255) DEFAULT '',
  `available_hours_per_week` INT DEFAULT 10,
  `availability_days` VARCHAR(255) DEFAULT 'Mon,Wed,Fri',
  `availability_slots` VARCHAR(255) DEFAULT 'Evening,Weekend',
  `profile_completed` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Student Skills Table
CREATE TABLE IF NOT EXISTS `student_skills` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `student_id` INT NOT NULL,
  `skill_id` INT NOT NULL,
  `proficiency` VARCHAR(20) DEFAULT 'Intermediate',
  `proficiency_score` INT DEFAULT 2,
  FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`skill_id`) REFERENCES `skills`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uniq_student_skill` (`student_id`, `skill_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Student Interests Table
CREATE TABLE IF NOT EXISTS `student_interests` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `student_id` INT NOT NULL,
  `interest_id` INT NOT NULL,
  FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`interest_id`) REFERENCES `interests`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uniq_student_interest` (`student_id`, `interest_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Projects Table
CREATE TABLE IF NOT EXISTS `projects` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(150) NOT NULL,
  `description` TEXT NOT NULL,
  `domain` VARCHAR(100) DEFAULT 'Web Development',
  `preferred_team_size` INT DEFAULT 4,
  `min_team_size` INT DEFAULT 3,
  `max_team_size` INT DEFAULT 5,
  `min_experience_months` INT DEFAULT 0,
  `min_availability_hours` INT DEFAULT 8,
  `status` VARCHAR(30) DEFAULT 'Active',
  `created_by_id` INT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`created_by_id`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Project Required Skills
CREATE TABLE IF NOT EXISTS `project_skills` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `project_id` INT NOT NULL,
  `skill_id` INT NOT NULL,
  `min_proficiency` VARCHAR(20) DEFAULT 'Intermediate',
  `min_proficiency_score` INT DEFAULT 2,
  `is_mandatory` BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`skill_id`) REFERENCES `skills`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Project Required Roles
CREATE TABLE IF NOT EXISTS `project_roles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `project_id` INT NOT NULL,
  `role_name` VARCHAR(60) NOT NULL,
  `min_count` INT DEFAULT 1,
  FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Team Generation Runs (Tracks executions of Traditional and AI algorithms)
CREATE TABLE IF NOT EXISTS `team_generation_runs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `project_id` INT NOT NULL,
  `method` VARCHAR(30) NOT NULL,
  `status` VARCHAR(30) DEFAULT 'Proposed',
  `parameters_json` TEXT,
  `evaluation_metrics_json` TEXT,
  `is_approved` BOOLEAN DEFAULT FALSE,
  `approved_at` DATETIME NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Teams Table
CREATE TABLE IF NOT EXISTS `teams` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `generation_run_id` INT NOT NULL,
  `project_id` INT NOT NULL,
  `name` VARCHAR(80) NOT NULL,
  `overall_score` FLOAT DEFAULT 0.0,
  `skill_coverage_pct` FLOAT DEFAULT 0.0,
  `role_coverage_pct` FLOAT DEFAULT 0.0,
  `experience_score` FLOAT DEFAULT 0.0,
  `availability_score` FLOAT DEFAULT 0.0,
  `interest_score` FLOAT DEFAULT 0.0,
  `explanation_narrative` TEXT,
  `technical_details_json` TEXT,
  `status` VARCHAR(30) DEFAULT 'Proposed',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`generation_run_id`) REFERENCES `team_generation_runs`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. Team Members Table
CREATE TABLE IF NOT EXISTS `team_members` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT NOT NULL,
  `student_id` INT NOT NULL,
  `assigned_role` VARCHAR(60) DEFAULT 'Developer',
  `student_cluster` INT DEFAULT -1,
  `cluster_label` VARCHAR(100) DEFAULT 'Generalist',
  `fit_score` FLOAT DEFAULT 0.0,
  FOREIGN KEY (`team_id`) REFERENCES `teams`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uniq_team_student` (`team_id`, `student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. ML Model Training Runs
CREATE TABLE IF NOT EXISTS `model_training_runs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `model_name` VARCHAR(80) DEFAULT 'KMeans-StudentArchetypes',
  `n_clusters` INT DEFAULT 4,
  `n_students` INT DEFAULT 0,
  `inertia` FLOAT DEFAULT 0.0,
  `silhouette_score` FLOAT DEFAULT 0.0,
  `features_list_json` TEXT,
  `cluster_summaries_json` TEXT,
  `model_path` VARCHAR(255) DEFAULT '',
  `trained_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. What-If Simulation Runs
CREATE TABLE IF NOT EXISTS `simulation_runs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `project_id` INT NOT NULL,
  `simulation_name` VARCHAR(100) DEFAULT 'What-If Simulation',
  `parameters_json` TEXT,
  `results_json` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. Student Feedback
CREATE TABLE IF NOT EXISTS `student_feedbacks` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `student_id` INT NOT NULL,
  `project_id` INT NOT NULL,
  `team_id` INT NULL,
  `skill_fit_rating` INT DEFAULT 4,
  `role_satisfaction_rating` INT DEFAULT 4,
  `availability_compatibility_rating` INT DEFAULT 4,
  `collaboration_rating` INT DEFAULT 4,
  `comments` TEXT,
  `submitted_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`team_id`) REFERENCES `teams`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 16. Audit Log
CREATE TABLE IF NOT EXISTS `audit_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `action_type` VARCHAR(60) NOT NULL,
  `description` TEXT NOT NULL,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

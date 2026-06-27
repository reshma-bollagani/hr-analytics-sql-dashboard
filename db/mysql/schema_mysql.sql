-- =====================================================================
-- HR ANALYTICS DATABASE SCHEMA -- MySQL VERSION
-- =====================================================================
-- This is the MySQL port of db/schema.sql (originally SQLite).
-- DIFFERENCES FROM THE SQLITE VERSION (everything else is identical):
--   1. AUTOINCREMENT -> AUTO_INCREMENT, and it must sit on the column
--      itself, not as a separate keyword after PRIMARY KEY.
--   2. SQLite's dynamic typing doesn't enforce VARCHAR lengths; MySQL
--      needs explicit lengths, e.g. VARCHAR(50) instead of bare TEXT.
--   3. PRAGMA foreign_keys = ON is SQLite-only; MySQL's InnoDB engine
--      enforces foreign keys by default, so it's simply removed here.
--   4. Engine is explicitly set to InnoDB (MySQL's default in modern
--      versions, but stated explicitly since InnoDB is required for
--      foreign key constraints to actually be enforced).
--
-- HOW TO RUN THIS IN MYSQL WORKBENCH:
--   1. Open MySQL Workbench, connect to your local server.
--   2. File -> Open SQL Script -> select this file.
--   3. Click the lightning bolt ("Execute") to run the whole script.
--      This creates a new schema/database called hr_analytics and
--      all 4 tables inside it.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS hr_analytics
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hr_analytics;

DROP TABLE IF EXISTS performance;
DROP TABLE IF EXISTS compensation;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS managers;

-- ---------------------------------------------------------------------
-- MANAGERS: lookup/dimension table
-- ---------------------------------------------------------------------
CREATE TABLE managers (
    manager_id     INT PRIMARY KEY,
    manager_name   VARCHAR(50) NOT NULL,
    department     VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- EMPLOYEES: core record, one row per employee
-- ---------------------------------------------------------------------
CREATE TABLE employees (
    employee_id              INT PRIMARY KEY,
    age                      INT NOT NULL,
    gender                   VARCHAR(10),
    marital_status           VARCHAR(20),
    department               VARCHAR(50) NOT NULL,
    job_role                 VARCHAR(50) NOT NULL,
    education_field          VARCHAR(50),
    education_level          INT,        -- 1=Below College ... 4=Doctor
    business_travel          VARCHAR(30),
    distance_from_home       INT,
    job_level                INT,
    total_working_years      INT,
    years_at_company         INT,
    years_in_current_role    INT,
    years_since_last_promo   INT,
    years_with_curr_manager  INT,
    manager_id               INT,
    attrition                VARCHAR(3) NOT NULL,   -- 'Yes' / 'No'
    CONSTRAINT fk_employees_manager
        FOREIGN KEY (manager_id) REFERENCES managers(manager_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- COMPENSATION: pay-related fields, one row per employee
-- ---------------------------------------------------------------------
CREATE TABLE compensation (
    employee_id          INT PRIMARY KEY,
    monthly_income       INT NOT NULL,
    percent_salary_hike  INT,
    stock_option_level   INT,
    overtime             VARCHAR(3),   -- 'Yes' / 'No'
    CONSTRAINT fk_compensation_employee
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- PERFORMANCE: review/satisfaction fields, one row per employee
-- ---------------------------------------------------------------------
CREATE TABLE performance (
    employee_id                INT PRIMARY KEY,
    job_satisfaction           INT,   -- 1-4 scale
    environment_satisfaction   INT,
    work_life_balance          INT,
    job_involvement            INT,
    relationship_satisfaction  INT,
    performance_rating         INT,   -- 1-4 scale
    training_times_last_year   INT,
    num_companies_worked       INT,
    CONSTRAINT fk_performance_employee
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
) ENGINE=InnoDB;

-- Indexes on columns we filter/join/group by most often.
CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_manager ON employees(manager_id);
CREATE INDEX idx_employees_attrition ON employees(attrition);
CREATE INDEX idx_compensation_overtime ON compensation(overtime);

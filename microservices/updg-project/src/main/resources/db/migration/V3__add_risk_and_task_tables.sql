-- Project Risk Register (F-306 风险识别与预警)
CREATE TABLE IF NOT EXISTS pm_project_risk (
    risk_id VARCHAR(32) PRIMARY KEY,
    project_id VARCHAR(32) NOT NULL,
    risk_code VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    category VARCHAR(30),
    probability DECIMAL(4,2),
    impact INT,
    risk_score DECIMAL(5,2),
    owner VARCHAR(32),
    status VARCHAR(20) DEFAULT 'IDENTIFIED',
    mitigation_plan VARCHAR(1000),
    contingency_plan VARCHAR(1000),
    identified_by VARCHAR(32),
    identified_date TIMESTAMP,
    closed_date TIMESTAMP,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project Task Management (F-307 任务管理)
CREATE TABLE IF NOT EXISTS pm_project_task (
    task_id VARCHAR(32) PRIMARY KEY,
    project_id VARCHAR(32) NOT NULL,
    parent_task_id VARCHAR(32),
    task_name VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    wbs_node VARCHAR(50),
    assignee VARCHAR(32),
    status VARCHAR(20) DEFAULT 'NOT_STARTED',
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    estimated_hours INT,
    actual_hours INT,
    progress INT DEFAULT 0,
    start_date DATE,
    end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    predecessor_ids VARCHAR(500),
    deliverable VARCHAR(500),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_risk_project ON pm_project_risk(project_id);
CREATE INDEX IF NOT EXISTS idx_risk_severity ON pm_project_risk(severity);
CREATE INDEX IF NOT EXISTS idx_risk_score ON pm_project_risk(risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_task_project ON pm_project_task(project_id);
CREATE INDEX IF NOT EXISTS idx_task_assignee ON pm_project_task(assignee);
CREATE INDEX IF NOT EXISTS idx_task_status ON pm_project_task(status);

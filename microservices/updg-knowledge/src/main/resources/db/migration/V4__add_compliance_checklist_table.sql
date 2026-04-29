CREATE TABLE pm_compliance_checklist (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    category VARCHAR(100),
    items TEXT,
    completed_items TEXT,
    completion_rate DECIMAL(5,2),
    checked_by VARCHAR(36),
    checked_at TIMESTAMP
);

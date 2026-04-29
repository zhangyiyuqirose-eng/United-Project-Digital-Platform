CREATE TABLE pm_project_dependency (
    id VARCHAR(36) PRIMARY KEY,
    source_project_id VARCHAR(36) NOT NULL,
    target_project_id VARCHAR(36) NOT NULL,
    type VARCHAR(32) NOT NULL,
    description TEXT,
    created_at TIMESTAMP
);

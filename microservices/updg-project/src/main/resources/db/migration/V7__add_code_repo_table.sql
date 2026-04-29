CREATE TABLE pm_code_repo (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    repo_url VARCHAR(500) NOT NULL,
    branch VARCHAR(100),
    type VARCHAR(16) NOT NULL,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP
);

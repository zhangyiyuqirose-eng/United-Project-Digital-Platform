CREATE TABLE pm_build_record (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    repo_id VARCHAR(36),
    build_number VARCHAR(64) NOT NULL,
    status VARCHAR(16) NOT NULL,
    duration BIGINT,
    triggered_by VARCHAR(100),
    commit_hash VARCHAR(64),
    created_at TIMESTAMP
);

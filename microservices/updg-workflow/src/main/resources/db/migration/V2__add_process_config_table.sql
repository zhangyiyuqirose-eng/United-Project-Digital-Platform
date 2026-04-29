CREATE TABLE pm_process_config (
    id VARCHAR(36) PRIMARY KEY,
    process_key VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    nodes TEXT,
    transitions TEXT,
    version INT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

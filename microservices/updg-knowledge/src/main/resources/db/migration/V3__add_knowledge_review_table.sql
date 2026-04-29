CREATE TABLE pm_knowledge_review (
    id VARCHAR(36) PRIMARY KEY,
    doc_id VARCHAR(36) NOT NULL,
    reviewer_id VARCHAR(36) NOT NULL,
    status VARCHAR(16) NOT NULL,
    comment TEXT,
    reviewed_at TIMESTAMP
);

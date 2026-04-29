CREATE TABLE pm_expense_reimbursement (
    id VARCHAR(36) PRIMARY KEY,
    staff_id VARCHAR(36) NOT NULL,
    project_id VARCHAR(36),
    type VARCHAR(32) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    receipt_count INT,
    description TEXT,
    status VARCHAR(16) NOT NULL,
    submitted_at TIMESTAMP,
    approved_at TIMESTAMP,
    paid_at TIMESTAMP
);

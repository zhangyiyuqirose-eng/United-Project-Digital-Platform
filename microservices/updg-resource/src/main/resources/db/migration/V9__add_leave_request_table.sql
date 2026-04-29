CREATE TABLE pm_leave_request (
    id VARCHAR(36) PRIMARY KEY,
    staff_id VARCHAR(36) NOT NULL,
    type VARCHAR(16) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days INT,
    reason TEXT,
    status VARCHAR(16) NOT NULL,
    approved_by VARCHAR(36),
    approved_at TIMESTAMP
);

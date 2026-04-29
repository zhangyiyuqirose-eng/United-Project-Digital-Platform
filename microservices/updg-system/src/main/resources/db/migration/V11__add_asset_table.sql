CREATE TABLE pm_asset (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(32) NOT NULL,
    serial_number VARCHAR(100),
    assigned_to VARCHAR(36),
    project_id VARCHAR(36),
    purchase_date DATE,
    cost DECIMAL(12,2),
    status VARCHAR(16) NOT NULL,
    created_at TIMESTAMP
);

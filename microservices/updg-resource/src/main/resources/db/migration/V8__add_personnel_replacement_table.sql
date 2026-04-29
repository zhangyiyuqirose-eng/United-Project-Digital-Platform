-- V8__add_personnel_replacement_table.sql
-- Personnel replacement management table

CREATE TABLE IF NOT EXISTS pm_personnel_replacement (
    replacement_id    VARCHAR(64)    NOT NULL COMMENT 'Replacement ID',
    project_id        VARCHAR(64)    NOT NULL COMMENT 'Project ID',
    outgoing_staff_id VARCHAR(64)    COMMENT 'Outgoing staff ID',
    incoming_staff_id VARCHAR(64)    COMMENT 'Incoming staff ID',
    reason            VARCHAR(1000)  COMMENT 'Replacement reason',
    status            VARCHAR(32)    DEFAULT 'REQUESTED' COMMENT 'Status: REQUESTED/APPROVED/COMPLETED/REJECTED',
    handover_notes    TEXT           COMMENT 'Handover notes',
    requested_by      VARCHAR(64)    COMMENT 'Requested by user ID',
    requested_at      VARCHAR(32)    COMMENT 'Request time',
    completed_at      VARCHAR(32)    COMMENT 'Completion time',
    PRIMARY KEY (replacement_id),
    INDEX idx_project_id (project_id),
    INDEX idx_status (status)
) COMMENT 'Personnel replacement table';

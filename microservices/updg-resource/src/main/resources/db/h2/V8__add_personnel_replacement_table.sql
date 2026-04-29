-- V8__add_personnel_replacement_table.sql
-- Personnel replacement management table (H2)

CREATE TABLE IF NOT EXISTS pm_personnel_replacement (
    replacement_id    VARCHAR(64)    NOT NULL,
    project_id        VARCHAR(64)    NOT NULL,
    outgoing_staff_id VARCHAR(64),
    incoming_staff_id VARCHAR(64),
    reason            VARCHAR(1000),
    status            VARCHAR(32)    DEFAULT 'REQUESTED',
    handover_notes    TEXT,
    requested_by      VARCHAR(64),
    requested_at      VARCHAR(32),
    completed_at      VARCHAR(32),
    PRIMARY KEY (replacement_id)
);

CREATE INDEX IF NOT EXISTS idx_repl_proj_id ON pm_personnel_replacement(project_id);
CREATE INDEX IF NOT EXISTS idx_repl_status ON pm_personnel_replacement(status);

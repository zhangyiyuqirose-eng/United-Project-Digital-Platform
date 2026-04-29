-- V4__add_progress_alert_table.sql (H2 compatible)
-- Progress Alert table (F-304 Progress Deviation Alert)
CREATE TABLE IF NOT EXISTS pm_progress_alert (
    alert_id        VARCHAR(64)  NOT NULL,
    project_id      VARCHAR(64)  NOT NULL,
    alert_type      VARCHAR(30)  DEFAULT 'PROGRESS_DEVIATION',
    message         VARCHAR(1000),
    actual_progress DECIMAL(5,2),
    expected_progress DECIMAL(5,2),
    deviation       DECIMAL(5,2),
    severity        VARCHAR(20)  DEFAULT 'WARNING',
    status          VARCHAR(20)  DEFAULT 'ACTIVE',
    created_by      VARCHAR(64),
    create_time     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    ack_time        TIMESTAMP,
    resolve_time    TIMESTAMP,
    PRIMARY KEY (alert_id)
);

CREATE INDEX IF NOT EXISTS idx_alert_project ON pm_progress_alert(project_id);
CREATE INDEX IF NOT EXISTS idx_alert_status ON pm_progress_alert(status);

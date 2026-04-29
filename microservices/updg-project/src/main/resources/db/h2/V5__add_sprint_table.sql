-- V5__add_sprint_table.sql (H2 compatible)
-- Sprint Management (F-309)
CREATE TABLE IF NOT EXISTS pm_sprint (
    sprint_id       VARCHAR(64)  NOT NULL,
    project_id      VARCHAR(64)  NOT NULL,
    name            VARCHAR(128) NOT NULL,
    goal            VARCHAR(1000),
    start_date      DATE,
    end_date        DATE,
    status          VARCHAR(20)  DEFAULT 'PLANNED',
    velocity        DECIMAL(8,2),
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (sprint_id)
);

CREATE INDEX IF NOT EXISTS idx_sprint_project ON pm_sprint(project_id);
CREATE INDEX IF NOT EXISTS idx_sprint_status ON pm_sprint(status);

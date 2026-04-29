-- V6__add_budget_and_alert_tables.sql
-- Budget management and cost variance alert tables (H2)

CREATE TABLE IF NOT EXISTS pm_budget (
    budget_id          VARCHAR(64)    NOT NULL,
    project_id         VARCHAR(64)    NOT NULL,
    budget_year        INT,
    total_budget       DECIMAL(15,2),
    labor_budget       DECIMAL(15,2),
    outsource_budget   DECIMAL(15,2),
    procurement_budget DECIMAL(15,2),
    other_budget       DECIMAL(15,2),
    approved_by        VARCHAR(64),
    approved_date      TIMESTAMP,
    status             VARCHAR(32)    DEFAULT 'DRAFT',
    create_time        TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    update_time        TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (budget_id)
);

CREATE INDEX IF NOT EXISTS idx_pm_budget_project ON pm_budget(project_id);
CREATE INDEX IF NOT EXISTS idx_pm_budget_year ON pm_budget(budget_year);
CREATE INDEX IF NOT EXISTS idx_pm_budget_status ON pm_budget(status);

CREATE TABLE IF NOT EXISTS pm_cost_alert (
    alert_id          VARCHAR(64)     NOT NULL,
    project_id        VARCHAR(64)     NOT NULL,
    alert_type        VARCHAR(32),
    severity          VARCHAR(16),
    message           VARCHAR(500),
    current_value     DECIMAL(15,2),
    threshold         DECIMAL(15,2),
    status            VARCHAR(32)     DEFAULT 'ACTIVE',
    created_by        VARCHAR(64),
    create_time       TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    ack_time          TIMESTAMP,
    resolve_time      TIMESTAMP,
    PRIMARY KEY (alert_id)
);

CREATE INDEX IF NOT EXISTS idx_pm_alert_project ON pm_cost_alert(project_id);
CREATE INDEX IF NOT EXISTS idx_pm_alert_type ON pm_cost_alert(alert_type);
CREATE INDEX IF NOT EXISTS idx_pm_alert_status ON pm_cost_alert(status);
CREATE INDEX IF NOT EXISTS idx_pm_alert_severity ON pm_cost_alert(severity);

-- V6__add_budget_and_alert_tables.sql
-- Budget management and cost variance alert tables

CREATE TABLE IF NOT EXISTS pm_budget (
    budget_id          VARCHAR(64)    NOT NULL COMMENT 'Budget ID',
    project_id         VARCHAR(64)    NOT NULL COMMENT 'Project ID',
    budget_year        INT            COMMENT 'Budget year',
    total_budget       DECIMAL(15,2)  COMMENT 'Total budget',
    labor_budget       DECIMAL(15,2)  COMMENT 'Labor budget',
    outsource_budget   DECIMAL(15,2)  COMMENT 'Outsource budget',
    procurement_budget DECIMAL(15,2)  COMMENT 'Procurement budget',
    other_budget       DECIMAL(15,2)  COMMENT 'Other budget',
    approved_by        VARCHAR(64)    COMMENT 'Approved by user ID',
    approved_date      DATETIME       COMMENT 'Approval date',
    status             VARCHAR(32)    DEFAULT 'DRAFT' COMMENT 'DRAFT, APPROVED, ADJUSTED',
    create_time        DATETIME       DEFAULT CURRENT_TIMESTAMP,
    update_time        DATETIME       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (budget_id),
    INDEX idx_project_id (project_id),
    INDEX idx_budget_year (budget_year),
    INDEX idx_status (status)
) COMMENT 'Budget management table';

CREATE TABLE IF NOT EXISTS pm_cost_alert (
    alert_id          VARCHAR(64)     NOT NULL COMMENT 'Alert ID',
    project_id        VARCHAR(64)     NOT NULL COMMENT 'Project ID',
    alert_type        VARCHAR(32)     COMMENT 'BUDGET_OVER_RUN, CPI_LOW, SPI_LOW, VARIANCE_HIGH',
    severity          VARCHAR(16)     COMMENT 'WARNING, CRITICAL',
    message           VARCHAR(500)    COMMENT 'Alert message',
    current_value     DECIMAL(15,2)   COMMENT 'Current metric value',
    threshold         DECIMAL(15,2)   COMMENT 'Threshold value',
    status            VARCHAR(32)     DEFAULT 'ACTIVE' COMMENT 'ACTIVE, ACKNOWLEDGED, RESOLVED',
    created_by        VARCHAR(64)     COMMENT 'Created by',
    create_time       DATETIME        DEFAULT CURRENT_TIMESTAMP,
    ack_time          DATETIME        COMMENT 'Acknowledged time',
    resolve_time      DATETIME        COMMENT 'Resolved time',
    PRIMARY KEY (alert_id),
    INDEX idx_project_id (project_id),
    INDEX idx_alert_type (alert_type),
    INDEX idx_status (status),
    INDEX idx_severity (severity)
) COMMENT 'Cost variance alert table';

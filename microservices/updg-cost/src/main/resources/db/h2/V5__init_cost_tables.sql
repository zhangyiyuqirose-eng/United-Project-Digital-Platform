-- V5__init_cost_tables.sql (H2 compatible)

CREATE TABLE IF NOT EXISTS pm_cost (
    cost_id         VARCHAR(64)   NOT NULL,
    project_id      VARCHAR(64)   NOT NULL,
    cost_type       VARCHAR(32),
    amount          DECIMAL(15,2),
    calculate_time  TIMESTAMP,
    evm_pv          DECIMAL(15,2) DEFAULT 0,
    evm_ev          DECIMAL(15,2) DEFAULT 0,
    evm_ac          DECIMAL(15,2) DEFAULT 0,
    create_time     TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cost_id)
);

CREATE TABLE IF NOT EXISTS pm_cost_outsource (
    outsource_cost_id VARCHAR(64)  NOT NULL,
    cost_id           VARCHAR(64)  NOT NULL,
    staff_id          VARCHAR(64)  NOT NULL,
    timesheet_id      VARCHAR(64)  NOT NULL,
    amount            DECIMAL(10,2),
    create_time       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (outsource_cost_id)
);

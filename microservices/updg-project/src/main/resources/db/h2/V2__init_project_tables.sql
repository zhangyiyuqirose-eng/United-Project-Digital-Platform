-- V2__init_project_tables.sql (H2 compatible)

CREATE TABLE IF NOT EXISTS pm_project (
    project_id      VARCHAR(64)   NOT NULL,
    project_name    VARCHAR(128)  NOT NULL,
    project_type    VARCHAR(32),
    status          VARCHAR(32)   DEFAULT 'DRAFT',
    manager_id      VARCHAR(64),
    budget          DECIMAL(15,2),
    wbs_json        CLOB,
    milestone_json  CLOB,
    evm_pv          DECIMAL(15,2) DEFAULT 0,
    evm_ev          DECIMAL(15,2) DEFAULT 0,
    evm_ac          DECIMAL(15,2) DEFAULT 0,
    evm_cpi         DECIMAL(10,4) DEFAULT 0,
    evm_spi         DECIMAL(10,4) DEFAULT 0,
    health_score    DECIMAL(5,2)  DEFAULT 0,
    init_time       TIMESTAMP,
    start_time      TIMESTAMP,
    end_time        TIMESTAMP,
    actual_end_time TIMESTAMP,
    create_user     VARCHAR(64),
    create_time     TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id)
);

CREATE TABLE IF NOT EXISTS pm_project_milestone (
    milestone_id    VARCHAR(64)  NOT NULL,
    project_id      VARCHAR(64)  NOT NULL,
    milestone_name  VARCHAR(128) NOT NULL,
    plan_time       TIMESTAMP,
    actual_time     TIMESTAMP,
    status          VARCHAR(32)  DEFAULT 'PENDING',
    sort            INT          DEFAULT 0,
    create_time     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (milestone_id)
);

CREATE TABLE IF NOT EXISTS pm_project_change (
    change_id       VARCHAR(64)  NOT NULL,
    project_id      VARCHAR(64)  NOT NULL,
    change_type     VARCHAR(32),
    content         CLOB,
    reason          CLOB,
    approve_status  VARCHAR(32)  DEFAULT 'PENDING',
    create_user     VARCHAR(64),
    create_time     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (change_id)
);

CREATE TABLE IF NOT EXISTS pm_project_close (
    close_id        VARCHAR(64)  NOT NULL,
    project_id      VARCHAR(64)  NOT NULL,
    close_time      TIMESTAMP,
    summary         CLOB,
    cost_summary    CLOB,
    lessons_learned CLOB,
    create_user     VARCHAR(64),
    create_time     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (close_id),
    CONSTRAINT uk_project_close UNIQUE (project_id)
);

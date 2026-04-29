-- V5__init_cost_tables.sql
-- 成本管理表

CREATE TABLE IF NOT EXISTS pm_cost (
    cost_id         VARCHAR(64)   NOT NULL COMMENT '成本ID',
    project_id      VARCHAR(64)   NOT NULL COMMENT '项目ID',
    cost_type       VARCHAR(32)   COMMENT '成本类型: OUTSOURCE/MATERIAL/OTHER',
    amount          DECIMAL(15,2) COMMENT '金额',
    calculate_time  DATETIME      COMMENT '核算时间',
    evm_pv          DECIMAL(15,2) DEFAULT 0 COMMENT '计划价值',
    evm_ev          DECIMAL(15,2) DEFAULT 0 COMMENT '挣值',
    evm_ac          DECIMAL(15,2) DEFAULT 0 COMMENT '实际成本',
    create_time     DATETIME      DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cost_id),
    INDEX idx_project_id (project_id),
    INDEX idx_cost_type (cost_type),
    INDEX idx_calculate_time (calculate_time)
) COMMENT '成本主表';

CREATE TABLE IF NOT EXISTS pm_cost_outsource (
    outsource_cost_id VARCHAR(64)  NOT NULL COMMENT '外包成本ID',
    cost_id           VARCHAR(64)  NOT NULL COMMENT '关联成本ID',
    staff_id          VARCHAR(64)  NOT NULL COMMENT '人员ID',
    timesheet_id      VARCHAR(64)  NOT NULL COMMENT '工时ID',
    amount            DECIMAL(10,2) COMMENT '金额',
    create_time       DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (outsource_cost_id),
    INDEX idx_cost_id (cost_id),
    INDEX idx_staff_id (staff_id)
) COMMENT '外包成本明细表';

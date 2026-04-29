-- V2__init_project_tables.sql
-- 项目管理核心表

CREATE TABLE IF NOT EXISTS pm_project (
    project_id      VARCHAR(64)   NOT NULL COMMENT '项目ID',
    project_name    VARCHAR(128)  NOT NULL COMMENT '项目名称',
    project_type    VARCHAR(32)   COMMENT '项目类型',
    status          VARCHAR(32)   DEFAULT 'DRAFT' COMMENT '状态: DRAFT/APPROVED/ACTIVE/CHANGED/CLOSED/REJECTED',
    manager_id      VARCHAR(64)   COMMENT '项目经理ID',
    budget          DECIMAL(15,2) COMMENT '预算金额',
    wbs_json        TEXT          COMMENT 'WBS结构JSON',
    milestone_json  TEXT          COMMENT '里程碑JSON',
    evm_pv          DECIMAL(15,2) DEFAULT 0 COMMENT '计划价值 PV',
    evm_ev          DECIMAL(15,2) DEFAULT 0 COMMENT '挣值 EV',
    evm_ac          DECIMAL(15,2) DEFAULT 0 COMMENT '实际成本 AC',
    evm_cpi         DECIMAL(10,4) DEFAULT 0 COMMENT '成本绩效指数 CPI',
    evm_spi         DECIMAL(10,4) DEFAULT 0 COMMENT '进度绩效指数 SPI',
    init_time       DATETIME      COMMENT '立项时间',
    start_time      DATETIME      COMMENT '开始时间',
    end_time        DATETIME      COMMENT '预计结束时间',
    actual_end_time DATETIME      COMMENT '实际结束时间',
    create_user     VARCHAR(64)   COMMENT '创建人',
    create_time     DATETIME      DEFAULT CURRENT_TIMESTAMP,
    update_time     DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id),
    INDEX idx_manager_id (manager_id),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) COMMENT '项目主表';

CREATE TABLE IF NOT EXISTS pm_project_milestone (
    milestone_id    VARCHAR(64)  NOT NULL COMMENT '里程碑ID',
    project_id      VARCHAR(64)  NOT NULL COMMENT '项目ID',
    milestone_name  VARCHAR(128) NOT NULL COMMENT '里程碑名称',
    plan_time       DATETIME     COMMENT '计划时间',
    actual_time     DATETIME     COMMENT '实际时间',
    status          VARCHAR(32)  DEFAULT 'PENDING' COMMENT '状态: PENDING/COMPLETED/DELAYED',
    sort            INT          DEFAULT 0,
    create_time     DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (milestone_id),
    INDEX idx_project_id (project_id),
    INDEX idx_status (status)
) COMMENT '项目里程碑表';

CREATE TABLE IF NOT EXISTS pm_project_change (
    change_id       VARCHAR(64)  NOT NULL COMMENT '变更ID',
    project_id      VARCHAR(64)  NOT NULL COMMENT '项目ID',
    change_type     VARCHAR(32)  COMMENT '变更类型: BUDGET/SCHEDULE/SCOPE/MANAGER',
    content         TEXT         COMMENT '变更内容',
    reason          TEXT         COMMENT '变更原因',
    approve_status  VARCHAR(32)  DEFAULT 'PENDING' COMMENT '审批状态: PENDING/APPROVED/REJECTED',
    create_user     VARCHAR(64)  COMMENT '创建人',
    create_time     DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (change_id),
    INDEX idx_project_id (project_id),
    INDEX idx_approve_status (approve_status)
) COMMENT '项目变更记录表';

CREATE TABLE IF NOT EXISTS pm_project_close (
    close_id        VARCHAR(64)  NOT NULL COMMENT '收尾ID',
    project_id      VARCHAR(64)  NOT NULL COMMENT '项目ID',
    close_time      DATETIME     COMMENT '收尾时间',
    summary         TEXT         COMMENT '项目总结',
    cost_summary    TEXT         COMMENT '成本总结',
    lessons_learned TEXT         COMMENT '经验教训',
    create_user     VARCHAR(64),
    create_time     DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (close_id),
    UNIQUE INDEX idx_project_id (project_id)
) COMMENT '项目收尾记录表';

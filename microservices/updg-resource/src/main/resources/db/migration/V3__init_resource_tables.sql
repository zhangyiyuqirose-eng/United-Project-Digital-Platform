-- V3__init_resource_tables.sql
-- 人力外包资源池表

CREATE TABLE IF NOT EXISTS pm_resource_outsourcing (
    staff_id    VARCHAR(64)  NOT NULL COMMENT '人员ID',
    name        VARCHAR(32)  NOT NULL COMMENT '姓名',
    id_card     VARCHAR(32)  COMMENT '身份证号(加密存储)',
    skill       VARCHAR(256) COMMENT '技能标签',
    resource_pool VARCHAR(64) COMMENT '资源池',
    entry_time  DATETIME     COMMENT '入场时间',
    exit_time   DATETIME     COMMENT '离场时间',
    rate        DECIMAL(10,2) COMMENT '日费率',
    status      VARCHAR(16)  DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE/EXITED',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (staff_id),
    INDEX idx_pool (resource_pool),
    INDEX idx_status (status)
) COMMENT '外包人员表'
PARTITION BY HASH(staff_id) PARTITIONS 4;

CREATE TABLE IF NOT EXISTS pm_resource_pool (
    pool_id     VARCHAR(64)  NOT NULL COMMENT '资源池ID',
    pool_name   VARCHAR(64)  NOT NULL COMMENT '资源池名称',
    manager_id  VARCHAR(64)  COMMENT '资源经理ID',
    description VARCHAR(256) COMMENT '描述',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pool_id)
) COMMENT '资源池表';

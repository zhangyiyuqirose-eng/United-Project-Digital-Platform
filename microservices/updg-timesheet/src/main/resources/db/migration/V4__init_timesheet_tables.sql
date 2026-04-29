-- V4__init_timesheet_tables.sql
-- 工时管理表（按月分表，此处创建基础表）

CREATE TABLE IF NOT EXISTS pm_timesheet (
    timesheet_id          VARCHAR(64)  NOT NULL COMMENT '工时ID',
    staff_id              VARCHAR(64)  NOT NULL COMMENT '人员ID',
    project_id            VARCHAR(64)  NOT NULL COMMENT '项目ID',
    work_date             DATE         NOT NULL COMMENT '工作日期',
    hours                 DECIMAL(4,1) NOT NULL COMMENT '工时数',
    check_status          VARCHAR(16)  DEFAULT 'PENDING' COMMENT '审核状态: PENDING/APPROVED/REJECTED',
    attendance_check_result VARCHAR(16) COMMENT '考勤比对结果: MATCH/MISMATCH',
    remark                VARCHAR(256) COMMENT '备注',
    create_time           DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time           DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (timesheet_id),
    INDEX idx_staff_date (staff_id, work_date),
    INDEX idx_project_date (project_id, work_date),
    INDEX idx_check_status (check_status)
) COMMENT '工时记录表';

CREATE TABLE IF NOT EXISTS pm_timesheet_attendance (
    attendance_id VARCHAR(64)  NOT NULL COMMENT '考勤ID',
    staff_id      VARCHAR(64)  NOT NULL COMMENT '人员ID',
    attendance_date DATE       NOT NULL COMMENT '考勤日期',
    check_in_time   DATETIME   COMMENT '签到时间',
    check_out_time  DATETIME   COMMENT '签退时间',
    sync_time       DATETIME   DEFAULT CURRENT_TIMESTAMP COMMENT '同步时间',
    PRIMARY KEY (attendance_id),
    INDEX idx_staff_date (staff_id, attendance_date)
) COMMENT '考勤对接表';

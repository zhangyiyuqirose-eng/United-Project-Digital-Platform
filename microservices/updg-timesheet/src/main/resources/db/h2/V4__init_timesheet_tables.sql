-- V4__init_timesheet_tables.sql (H2 compatible)

CREATE TABLE IF NOT EXISTS pm_timesheet (
    timesheet_id            VARCHAR(64)  NOT NULL,
    staff_id                VARCHAR(64)  NOT NULL,
    project_id              VARCHAR(64)  NOT NULL,
    work_date               DATE         NOT NULL,
    hours                   DECIMAL(4,1) NOT NULL,
    check_status            VARCHAR(16)  DEFAULT 'PENDING',
    attendance_check_result VARCHAR(16),
    remark                  VARCHAR(256),
    create_time             TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    update_time             TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (timesheet_id)
);

CREATE TABLE IF NOT EXISTS pm_timesheet_attendance (
    attendance_id   VARCHAR(64)  NOT NULL,
    staff_id        VARCHAR(64)  NOT NULL,
    attendance_date DATE         NOT NULL,
    check_in_time   TIMESTAMP,
    check_out_time  TIMESTAMP,
    sync_time       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (attendance_id)
);

-- V7__add_performance_eval_table.sql
-- Performance evaluation table

CREATE TABLE IF NOT EXISTS pm_performance_eval (
    eval_id           VARCHAR(64)    NOT NULL COMMENT 'Evaluation ID',
    staff_id          VARCHAR(64)    NOT NULL COMMENT 'Staff ID',
    evaluator         VARCHAR(64)    COMMENT 'Evaluator user ID',
    eval_period       VARCHAR(32)    COMMENT 'Evaluation period, e.g. 2026-Q1',
    quality_score     INT            COMMENT 'Quality score',
    efficiency_score  INT            COMMENT 'Efficiency score',
    attitude_score    INT            COMMENT 'Attitude score',
    skill_score       INT            COMMENT 'Skill score',
    overall_score     INT            COMMENT 'Overall score',
    comment           VARCHAR(1000)  COMMENT 'Evaluation comment',
    create_time       DATETIME       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (eval_id),
    INDEX idx_staff_id (staff_id),
    INDEX idx_eval_period (eval_period)
) COMMENT 'Performance evaluation table';

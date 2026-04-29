-- V7__add_performance_eval_table.sql
-- Performance evaluation table (H2)

CREATE TABLE IF NOT EXISTS pm_performance_eval (
    eval_id           VARCHAR(64)    NOT NULL,
    staff_id          VARCHAR(64)    NOT NULL,
    evaluator         VARCHAR(64),
    eval_period       VARCHAR(32),
    quality_score     INT,
    efficiency_score  INT,
    attitude_score    INT,
    skill_score       INT,
    overall_score     INT,
    comment           VARCHAR(1000),
    create_time       TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (eval_id)
);

CREATE INDEX IF NOT EXISTS idx_pm_eval_staff ON pm_performance_eval(staff_id);
CREATE INDEX IF NOT EXISTS idx_pm_eval_period ON pm_performance_eval(eval_period);

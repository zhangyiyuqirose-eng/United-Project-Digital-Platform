-- V2__add_notify_template_table.sql
-- Add notification template table

CREATE TABLE IF NOT EXISTS pm_notify_template (
    template_id     VARCHAR(64)     NOT NULL PRIMARY KEY COMMENT 'Template ID',
    name            VARCHAR(128)    NOT NULL COMMENT 'Template name',
    channel         VARCHAR(32)     NOT NULL COMMENT 'Channel: WECHAT, EMAIL, SMS',
    subject         VARCHAR(256)    COMMENT 'Subject (for EMAIL)',
    content         TEXT            NOT NULL COMMENT 'Template content with placeholders',
    variables       VARCHAR(512)    COMMENT 'JSON array of variable names',
    is_active       VARCHAR(1)      NOT NULL DEFAULT 'Y' COMMENT 'Y or N',
    created_by      VARCHAR(64)     COMMENT 'Creator user ID',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created at',
    update_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated at',
    INDEX idx_channel (channel),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Notification templates';
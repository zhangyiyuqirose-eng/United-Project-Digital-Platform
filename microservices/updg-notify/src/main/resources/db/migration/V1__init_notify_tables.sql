-- V1__init_notify_tables.sql
-- Initialize notification message and preference tables

CREATE TABLE IF NOT EXISTS pm_notify_message (
    message_id      VARCHAR(64)     NOT NULL PRIMARY KEY COMMENT 'Message ID',
    title           VARCHAR(256)    NOT NULL COMMENT 'Message title',
    content         TEXT            COMMENT 'Message content',
    channel         VARCHAR(32)     NOT NULL COMMENT 'Channel: WECHAT, EMAIL, SMS',
    receiver        VARCHAR(128)    NOT NULL COMMENT 'Receiver identifier',
    sender          VARCHAR(128)    COMMENT 'Sender identifier',
    status          VARCHAR(16)     NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING, SENT, FAILED, READ',
    priority        VARCHAR(16)     NOT NULL DEFAULT 'NORMAL' COMMENT 'LOW, NORMAL, HIGH, URGENT',
    biz_type        VARCHAR(64)     COMMENT 'Business type identifier',
    biz_id          VARCHAR(64)     COMMENT 'Related business record ID',
    send_time       DATETIME        COMMENT 'Actual send time',
    read_time       DATETIME        COMMENT 'Read time',
    error_msg       VARCHAR(512)    COMMENT 'Error message on failure',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created at',
    update_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated at',
    INDEX idx_receiver (receiver),
    INDEX idx_channel (channel),
    INDEX idx_status (status),
    INDEX idx_biz (biz_type, biz_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Notification messages';

CREATE TABLE IF NOT EXISTS pm_notify_preference (
    pref_id         VARCHAR(64)     NOT NULL PRIMARY KEY COMMENT 'Preference ID',
    user_id         VARCHAR(64)     NOT NULL COMMENT 'User ID',
    channel         VARCHAR(32)     NOT NULL COMMENT 'Channel: WECHAT, EMAIL, SMS',
    enabled         TINYINT         NOT NULL DEFAULT 1 COMMENT 'Whether this channel is enabled',
    biz_types       VARCHAR(512)    COMMENT 'Comma-separated business types to receive',
    quiet_start     VARCHAR(8)      COMMENT 'Quiet period start (HH:mm)',
    quiet_end       VARCHAR(8)      COMMENT 'Quiet period end (HH:mm)',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created at',
    update_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated at',
    UNIQUE INDEX idx_user_channel (user_id, channel)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Notification preferences per user per channel';

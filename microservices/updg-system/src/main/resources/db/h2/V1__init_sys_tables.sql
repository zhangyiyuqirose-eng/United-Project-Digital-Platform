-- V1__init_sys_tables.sql (H2 compatible)

CREATE TABLE IF NOT EXISTS pm_sys_dept (
    dept_id     VARCHAR(64)  NOT NULL,
    dept_name   VARCHAR(128) NOT NULL,
    parent_id   VARCHAR(64)  DEFAULT '0',
    sort        INT          DEFAULT 0,
    status      TINYINT      DEFAULT 1,
    create_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_sys_user (
    user_id     VARCHAR(64)  NOT NULL,
    username    VARCHAR(32)  NOT NULL,
    password    VARCHAR(128) NOT NULL,
    name        VARCHAR(32)  NOT NULL,
    dept_id     VARCHAR(64),
    email       VARCHAR(128),
    phone       VARCHAR(16),
    status      TINYINT      DEFAULT 1,
    create_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_username UNIQUE (username)
);

CREATE TABLE IF NOT EXISTS pm_sys_role (
    role_id     VARCHAR(64)  NOT NULL,
    role_name   VARCHAR(64)  NOT NULL,
    role_code   VARCHAR(32)  NOT NULL,
    description VARCHAR(256),
    status      TINYINT      DEFAULT 1,
    create_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_role_code UNIQUE (role_code)
);

CREATE TABLE IF NOT EXISTS pm_sys_permission (
    permission_id   VARCHAR(64)  NOT NULL,
    permission_name VARCHAR(64)  NOT NULL,
    permission_code VARCHAR(64)  NOT NULL,
    type            VARCHAR(16)  NOT NULL,
    parent_id       VARCHAR(64)  DEFAULT '0',
    sort            INT          DEFAULT 0,
    create_time     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_permission_code UNIQUE (permission_code)
);

CREATE TABLE IF NOT EXISTS pm_sys_user_role (
    user_id VARCHAR(64) NOT NULL,
    role_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS pm_sys_role_permission (
    role_id       VARCHAR(64) NOT NULL,
    permission_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS pm_sys_dict (
    dict_id     VARCHAR(64)  NOT NULL,
    dict_name   VARCHAR(64)  NOT NULL,
    dict_code   VARCHAR(32)  NOT NULL,
    create_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_dict_code UNIQUE (dict_code)
);

CREATE TABLE IF NOT EXISTS pm_sys_dict_item (
    item_id VARCHAR(64)  NOT NULL,
    dict_id VARCHAR(64)  NOT NULL,
    label   VARCHAR(64)  NOT NULL,
    "value"   VARCHAR(128) NOT NULL,
    sort    INT          DEFAULT 0,
    status  TINYINT      DEFAULT 1,
    PRIMARY KEY (item_id)
);

CREATE TABLE IF NOT EXISTS pm_sys_audit_log (
    audit_id      VARCHAR(64)  NOT NULL,
    user_id       VARCHAR(64)  NOT NULL,
    module        VARCHAR(32),
    operation     VARCHAR(64),
    ip_address    VARCHAR(45),
    request_uri   VARCHAR(256),
    request_body  CLOB,
    response_code VARCHAR(32),
    before_value  CLOB,
    after_value   CLOB,
    create_time   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (audit_id)
);

-- Default data
INSERT INTO pm_sys_dept (dept_id, dept_name, parent_id, sort) VALUES ('1', '信息技术部', '0', 1);
INSERT INTO pm_sys_role (role_id, role_name, role_code, description) VALUES ('1', '超级管理员', 'SUPER_ADMIN', '系统最高权限');
INSERT INTO pm_sys_user (user_id, username, password, name, dept_id) VALUES ('1', 'admin', 'admin_encrypted', '系统管理员', '1');
INSERT INTO pm_sys_user_role (user_id, role_id) VALUES ('1', '1');

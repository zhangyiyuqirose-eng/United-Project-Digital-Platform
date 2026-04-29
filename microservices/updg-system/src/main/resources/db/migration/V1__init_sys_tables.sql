-- V1__init_sys_tables.sql
-- 系统管理核心表（MySQL / DM8 兼容）

CREATE TABLE IF NOT EXISTS pm_sys_dept (
    dept_id     VARCHAR(64)  NOT NULL COMMENT '部门ID',
    dept_name   VARCHAR(128) NOT NULL COMMENT '部门名称',
    parent_id   VARCHAR(64)  DEFAULT '0' COMMENT '上级部门',
    sort        INT          DEFAULT 0 COMMENT '排序',
    status      TINYINT      DEFAULT 1 COMMENT '状态 0禁用 1启用',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (dept_id),
    INDEX idx_parent_id (parent_id)
) COMMENT '部门表';

CREATE TABLE IF NOT EXISTS pm_sys_user (
    user_id     VARCHAR(64)  NOT NULL COMMENT '用户ID',
    username    VARCHAR(32)  NOT NULL COMMENT '用户名',
    password    VARCHAR(128) NOT NULL COMMENT '密码(SM3+盐值)',
    name        VARCHAR(32)  NOT NULL COMMENT '姓名',
    dept_id     VARCHAR(64)  COMMENT '所属部门',
    email       VARCHAR(128) COMMENT '邮箱',
    phone       VARCHAR(16)  COMMENT '手机号',
    status      TINYINT      DEFAULT 1 COMMENT '状态 0禁用 1启用',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE INDEX uk_username (username),
    INDEX idx_dept_id (dept_id)
) COMMENT '用户表';

CREATE TABLE IF NOT EXISTS pm_sys_role (
    role_id     VARCHAR(64)  NOT NULL COMMENT '角色ID',
    role_name   VARCHAR(64)  NOT NULL COMMENT '角色名称',
    role_code   VARCHAR(32)  NOT NULL COMMENT '角色编码',
    description VARCHAR(256) COMMENT '描述',
    status      TINYINT      DEFAULT 1 COMMENT '状态 0禁用 1启用',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id),
    UNIQUE INDEX uk_role_code (role_code)
) COMMENT '角色表';

CREATE TABLE IF NOT EXISTS pm_sys_permission (
    permission_id   VARCHAR(64)  NOT NULL COMMENT '权限ID',
    permission_name VARCHAR(64)  NOT NULL COMMENT '权限名称',
    permission_code VARCHAR(64)  NOT NULL COMMENT '权限编码',
    type            VARCHAR(16)  NOT NULL COMMENT '类型 menu/button/api',
    parent_id       VARCHAR(64)  DEFAULT '0' COMMENT '上级权限',
    sort            INT          DEFAULT 0,
    create_time     DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (permission_id),
    UNIQUE INDEX uk_permission_code (permission_code)
) COMMENT '权限表';

CREATE TABLE IF NOT EXISTS pm_sys_user_role (
    user_id VARCHAR(64) NOT NULL,
    role_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (user_id, role_id),
    INDEX idx_role_id (role_id)
) COMMENT '用户-角色关联表';

CREATE TABLE IF NOT EXISTS pm_sys_role_permission (
    role_id       VARCHAR(64) NOT NULL,
    permission_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    INDEX idx_permission_id (permission_id)
) COMMENT '角色-权限关联表';

CREATE TABLE IF NOT EXISTS pm_sys_dict (
    dict_id     VARCHAR(64)  NOT NULL COMMENT '字典ID',
    dict_name   VARCHAR(64)  NOT NULL COMMENT '字典名称',
    dict_code   VARCHAR(32)  NOT NULL COMMENT '字典编码',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dict_id),
    UNIQUE INDEX uk_dict_code (dict_code)
) COMMENT '字典表';

CREATE TABLE IF NOT EXISTS pm_sys_dict_item (
    item_id VARCHAR(64)  NOT NULL COMMENT '字典项ID',
    dict_id VARCHAR(64)  NOT NULL COMMENT '所属字典',
    label   VARCHAR(64)  NOT NULL COMMENT '显示标签',
    value   VARCHAR(128) NOT NULL COMMENT '实际值',
    sort    INT          DEFAULT 0,
    status  TINYINT      DEFAULT 1,
    PRIMARY KEY (item_id),
    INDEX idx_dict_id (dict_id)
) COMMENT '字典项表';

CREATE TABLE IF NOT EXISTS pm_sys_audit_log (
    audit_id      VARCHAR(64)  NOT NULL COMMENT '审计ID',
    user_id       VARCHAR(64)  NOT NULL COMMENT '操作人',
    module        VARCHAR(32)  COMMENT '模块',
    operation     VARCHAR(64)  COMMENT '操作类型',
    ip_address    VARCHAR(45)  COMMENT 'IP地址',
    request_uri   VARCHAR(256) COMMENT '请求路径',
    request_body  TEXT         COMMENT '请求体',
    response_code VARCHAR(32)  COMMENT '响应码',
    before_value  TEXT         COMMENT '变更前值',
    after_value   TEXT         COMMENT '变更后值',
    create_time   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (audit_id),
    INDEX idx_user_id (user_id),
    INDEX idx_create_time (create_time)
) COMMENT '审计日志表';

-- 初始化默认数据
INSERT INTO pm_sys_dept (dept_id, dept_name, parent_id, sort) VALUES ('1', '信息技术部', '0', 1);
INSERT INTO pm_sys_role (role_id, role_name, role_code, description) VALUES ('1', '超级管理员', 'SUPER_ADMIN', '系统最高权限');
INSERT INTO pm_sys_user (user_id, username, password, name, dept_id) VALUES ('1', 'admin', 'admin_encrypted', '系统管理员', '1');
INSERT INTO pm_sys_user_role (user_id, role_id) VALUES ('1', '1');

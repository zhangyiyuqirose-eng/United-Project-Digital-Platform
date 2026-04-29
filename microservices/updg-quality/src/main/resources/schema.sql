-- UPDG Platform Database Schema for H2 - ALIGNED WITH ENTITY CLASSES
-- Created: 2026-04-26
-- This schema matches ALL entity class field names for MyBatis-Plus mapping

-- System Service Tables
CREATE TABLE IF NOT EXISTS pm_sys_user (
    user_id VARCHAR(64) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    name VARCHAR(100),
    dept_id VARCHAR(64),
    email VARCHAR(100),
    phone VARCHAR(20),
    status INT DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_sys_dept (
    dept_id VARCHAR(64) PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    parent_id VARCHAR(64),
    leader_id VARCHAR(64),
    sort_order INT DEFAULT 0,
    status INT DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_sys_role (
    role_id VARCHAR(64) PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL,
    role_code VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200),
    status INT DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_sys_permission (
    permission_id VARCHAR(64) PRIMARY KEY,
    permission_name VARCHAR(50) NOT NULL,
    permission_code VARCHAR(100) NOT NULL UNIQUE,
    resource_type VARCHAR(20),
    resource_url VARCHAR(200),
    parent_id VARCHAR(64),
    status INT DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_sys_user_role (
    user_id VARCHAR(64) NOT NULL,
    role_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS pm_sys_role_permission (
    role_id VARCHAR(64) NOT NULL,
    permission_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS pm_sys_dict (
    dict_id VARCHAR(64) PRIMARY KEY,
    dict_type VARCHAR(50) NOT NULL,
    dict_label VARCHAR(100) NOT NULL,
    dict_value VARCHAR(100) NOT NULL,
    sort_order INT DEFAULT 0,
    status INT DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_sys_config (
    config_id VARCHAR(64) PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value VARCHAR(500),
    description VARCHAR(200),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_sys_announcement (
    announcement_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    type VARCHAR(20),
    status INT DEFAULT 1,
    publisher_id VARCHAR(64),
    publish_time TIMESTAMP,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_sys_audit_log (
    log_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    operation VARCHAR(50),
    method VARCHAR(100),
    params TEXT,
    ip VARCHAR(50),
    status INT,
    error_msg TEXT,
    execute_time INT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_meeting (
    meeting_id VARCHAR(64) PRIMARY KEY,
    meeting_name VARCHAR(200) NOT NULL,
    meeting_type VARCHAR(20),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    location VARCHAR(200),
    organizer_id VARCHAR(64),
    participants TEXT,
    status VARCHAR(20),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_review_meeting (
    review_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64),
    review_type VARCHAR(20),
    review_date TIMESTAMP,
    reviewer_id VARCHAR(64),
    conclusion VARCHAR(200),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_review_opinion (
    opinion_id VARCHAR(64) PRIMARY KEY,
    review_id VARCHAR(64),
    reviewer_id VARCHAR(64),
    opinion_type VARCHAR(20),
    opinion_content TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_asset (
    asset_id VARCHAR(64) PRIMARY KEY,
    asset_name VARCHAR(200) NOT NULL,
    asset_type VARCHAR(20),
    asset_code VARCHAR(50) UNIQUE,
    owner_id VARCHAR(64),
    location VARCHAR(200),
    status VARCHAR(20),
    purchase_date TIMESTAMP,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project Service Tables
CREATE TABLE IF NOT EXISTS pm_project (
    project_id VARCHAR(64) PRIMARY KEY,
    project_name VARCHAR(200) NOT NULL,
    project_code VARCHAR(50) UNIQUE,
    project_type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'draft',
    manager_id VARCHAR(64),
    manager_name VARCHAR(100),
    department_id VARCHAR(64),
    department_name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15,2),
    customer VARCHAR(200),
    description TEXT,
    progress INT DEFAULT 0,
    wbs_json TEXT,
    milestone_json TEXT,
    evm_pv DECIMAL(15,2),
    evm_ev DECIMAL(15,2),
    evm_ac DECIMAL(15,2),
    evm_cpi DECIMAL(10,4),
    evm_spi DECIMAL(10,4),
    health_score DECIMAL(5,2),
    init_time TIMESTAMP,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    create_user VARCHAR(64),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_project_task (
    task_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    task_name VARCHAR(200) NOT NULL,
    assignee_id VARCHAR(64),
    assignee_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    start_date DATE,
    end_date DATE,
    progress INT DEFAULT 0,
    wbs_id VARCHAR(64),
    parent_task_id VARCHAR(64),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_wbs_node (
    wbs_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50),
    parent_id VARCHAR(64),
    level INT,
    sort_order INT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_project_risk (
    risk_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    risk_name VARCHAR(200) NOT NULL,
    risk_type VARCHAR(20),
    probability INT,
    impact INT,
    level VARCHAR(20),
    status VARCHAR(20) DEFAULT 'open',
    mitigation TEXT,
    owner_id VARCHAR(64),
    owner_name VARCHAR(100),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_project_milestone (
    milestone_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    milestone_name VARCHAR(200) NOT NULL,
    planned_date DATE,
    actual_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_project_change (
    change_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    change_type VARCHAR(20),
    change_reason TEXT,
    impact_analysis TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approver_id VARCHAR(64),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_project_close (
    close_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    close_type VARCHAR(20),
    close_date TIMESTAMP,
    summary TEXT,
    lessons_learned TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_sprint (
    sprint_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    sprint_name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'planning',
    goal TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_pre_initiation (
    pre_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    feasibility_study TEXT,
    business_case TEXT,
    initial_budget DECIMAL(15,2),
    expected_roi DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'draft',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_progress_alert (
    alert_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    task_id VARCHAR(64),
    alert_type VARCHAR(20),
    alert_level VARCHAR(20),
    message TEXT,
    is_handled INT DEFAULT 0,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_code_repo (
    repo_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    repo_name VARCHAR(200) NOT NULL,
    repo_url VARCHAR(500),
    branch VARCHAR(100),
    last_commit VARCHAR(100),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_build_record (
    build_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    build_number VARCHAR(50),
    build_status VARCHAR(20),
    build_time TIMESTAMP,
    duration INT,
    log_url VARCHAR(500),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_project_dependency (
    dep_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    depends_on_project_id VARCHAR(64) NOT NULL,
    dependency_type VARCHAR(20),
    description TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resource Service Tables - ALIGNED TO ENTITY
CREATE TABLE IF NOT EXISTS pm_resource_pool (
    pool_id VARCHAR(64) PRIMARY KEY,
    pool_name VARCHAR(100) NOT NULL,
    manager_id VARCHAR(64),
    description VARCHAR(500),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_leave_request (
    leave_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    leave_type VARCHAR(20),
    start_date DATE,
    end_date DATE,
    days INT,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approver_id VARCHAR(64),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_performance_eval (
    eval_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    project_id VARCHAR(64),
    period VARCHAR(20),
    score DECIMAL(5,2),
    evaluator_id VARCHAR(64),
    comments TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_personnel_replacement (
    replace_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    original_user_id VARCHAR(64),
    new_user_id VARCHAR(64),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_resource_outsourcing (
    outsource_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    vendor_name VARCHAR(200),
    resource_count INT,
    start_date DATE,
    end_date DATE,
    contract_id VARCHAR(64),
    status VARCHAR(20) DEFAULT 'active',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Timesheet Service Tables - ALIGNED TO ENTITY
CREATE TABLE IF NOT EXISTS pm_timesheet (
    timesheet_id VARCHAR(64) PRIMARY KEY,
    staff_id VARCHAR(64) NOT NULL,
    project_id VARCHAR(64) NOT NULL,
    work_date DATE NOT NULL,
    hours DECIMAL(5,2) NOT NULL,
    check_status VARCHAR(20) DEFAULT 'pending',
    attendance_check_result VARCHAR(200),
    remark TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_timesheet_attendance (
    attendance_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    date DATE NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    status VARCHAR(20),
    project_id VARCHAR(64),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cost Service Tables - ALIGNED TO ENTITY
CREATE TABLE IF NOT EXISTS pm_budget (
    budget_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    budget_year INT,
    total_budget DECIMAL(15,2),
    labor_budget DECIMAL(15,2),
    outsource_budget DECIMAL(15,2),
    procurement_budget DECIMAL(15,2),
    other_budget DECIMAL(15,2),
    approved_by VARCHAR(64),
    approved_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'DRAFT',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_cost (
    cost_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    cost_type VARCHAR(20) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    calculate_time TIMESTAMP,
    evm_pv DECIMAL(15,2),
    evm_ev DECIMAL(15,2),
    evm_ac DECIMAL(15,2),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_cost_alert (
    alert_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    budget_id VARCHAR(64),
    alert_type VARCHAR(20),
    threshold DECIMAL(15,2),
    current_value DECIMAL(15,2),
    message TEXT,
    is_handled INT DEFAULT 0,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_cost_outsource (
    outsource_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    vendor_name VARCHAR(200),
    contract_amount DECIMAL(15,2),
    paid_amount DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_expense_reimbursement (
    expense_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    project_id VARCHAR(64),
    expense_type VARCHAR(20),
    amount DECIMAL(15,2) NOT NULL,
    apply_date DATE,
    description TEXT,
    attachments TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approver_id VARCHAR(64),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business Service Tables - ALIGNED TO ENTITY
CREATE TABLE IF NOT EXISTS pm_contract (
    contract_id VARCHAR(64) PRIMARY KEY,
    contract_code VARCHAR(50) UNIQUE,
    contract_name VARCHAR(200) NOT NULL,
    contract_type VARCHAR(20),
    party_a VARCHAR(200),
    party_b VARCHAR(200),
    total_amount DECIMAL(15,2),
    currency VARCHAR(10),
    sign_date VARCHAR(20),
    start_date VARCHAR(20),
    end_date VARCHAR(20),
    project_id VARCHAR(64),
    status VARCHAR(20) DEFAULT 'draft',
    created_by VARCHAR(64),
    create_time VARCHAR(30),
    update_time VARCHAR(30),
    reminder_days INT
);

CREATE TABLE IF NOT EXISTS pm_contract_payment (
    payment_id VARCHAR(64) PRIMARY KEY,
    contract_id VARCHAR(64) NOT NULL,
    payment_type VARCHAR(20),
    planned_amount DECIMAL(15,2),
    actual_amount DECIMAL(15,2),
    planned_date DATE,
    actual_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_customer (
    customer_id VARCHAR(64) PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(20),
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(500),
    industry VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_supplier (
    supplier_id VARCHAR(64) PRIMARY KEY,
    supplier_name VARCHAR(200) NOT NULL,
    supplier_type VARCHAR(20),
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_business_opportunity (
    opportunity_id VARCHAR(64) PRIMARY KEY,
    opportunity_name VARCHAR(200) NOT NULL,
    customer_id VARCHAR(64),
    expected_amount DECIMAL(15,2),
    probability INT,
    stage VARCHAR(20),
    owner_id VARCHAR(64),
    expected_close_date DATE,
    status VARCHAR(20) DEFAULT 'open',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_quotation (
    quotation_id VARCHAR(64) PRIMARY KEY,
    opportunity_id VARCHAR(64),
    customer_id VARCHAR(64),
    quotation_no VARCHAR(50),
    amount DECIMAL(15,2),
    valid_until DATE,
    status VARCHAR(20) DEFAULT 'draft',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_procurement_plan (
    plan_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    plan_name VARCHAR(200) NOT NULL,
    procurement_type VARCHAR(20),
    budget DECIMAL(15,2),
    planned_date DATE,
    status VARCHAR(20) DEFAULT 'draft',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge Service Tables
CREATE TABLE IF NOT EXISTS pm_knowledge_doc (
    doc_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    doc_type VARCHAR(20),
    category VARCHAR(100),
    content TEXT,
    author_id VARCHAR(64),
    version VARCHAR(20),
    status VARCHAR(20) DEFAULT 'draft',
    publish_time TIMESTAMP,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_knowledge_template (
    template_id VARCHAR(64) PRIMARY KEY,
    template_name VARCHAR(200) NOT NULL,
    template_type VARCHAR(20),
    content TEXT,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_knowledge_review (
    review_id VARCHAR(64) PRIMARY KEY,
    doc_id VARCHAR(64) NOT NULL,
    reviewer_id VARCHAR(64),
    review_status VARCHAR(20),
    comments TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_compliance_checklist (
    checklist_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    checklist_name VARCHAR(200) NOT NULL,
    checklist_type VARCHAR(20),
    items TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quality Service Tables
CREATE TABLE IF NOT EXISTS pm_quality_defect (
    defect_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    defect_name VARCHAR(200) NOT NULL,
    defect_type VARCHAR(20),
    severity VARCHAR(20),
    status VARCHAR(20) DEFAULT 'open',
    found_by VARCHAR(64),
    assigned_to VARCHAR(64),
    found_date DATE,
    fixed_date DATE,
    description TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_quality_metric (
    metric_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2),
    target_value DECIMAL(10,2),
    measurement_date DATE,
    unit VARCHAR(20),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- File Service Tables
CREATE TABLE IF NOT EXISTS pm_file_info (
    file_id VARCHAR(64) PRIMARY KEY,
    file_name VARCHAR(200) NOT NULL,
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size BIGINT,
    project_id VARCHAR(64),
    uploader_id VARCHAR(64),
    download_count INT DEFAULT 0,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notify Service Tables
CREATE TABLE IF NOT EXISTS pm_notify_message (
    message_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    type VARCHAR(20),
    sender_id VARCHAR(64),
    receiver_id VARCHAR(64),
    status VARCHAR(20) DEFAULT 'unread',
    send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_notify_template (
    template_id VARCHAR(64) PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    template_code VARCHAR(50) UNIQUE,
    template_content TEXT,
    type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pm_notify_preference (
    pref_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    notify_type VARCHAR(20),
    enabled INT DEFAULT 1,
    channel VARCHAR(20),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Service Tables
CREATE TABLE IF NOT EXISTS pm_audit_log_entry (
    entry_id VARCHAR(64) PRIMARY KEY,
    audit_id VARCHAR(64),
    user_id VARCHAR(64),
    action VARCHAR(50),
    resource_type VARCHAR(50),
    resource_id VARCHAR(64),
    details TEXT,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Auth Service Tables
CREATE TABLE IF NOT EXISTS pm_login_attempt (
    attempt_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    username VARCHAR(50),
    ip_address VARCHAR(50),
    success INT DEFAULT 0,
    failure_reason VARCHAR(200),
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow Service Tables
CREATE TABLE IF NOT EXISTS pm_process_definition (
    def_id VARCHAR(64) PRIMARY KEY,
    process_key VARCHAR(100) NOT NULL UNIQUE,
    process_name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    deployment_id VARCHAR(100),
    version INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user (dept first to avoid FK violation)
INSERT INTO pm_sys_dept (dept_id, dept_name, parent_id, leader_id, sort_order, status) VALUES
('1', '总部', NULL, 'admin', 0, 1);

INSERT INTO pm_sys_user (user_id, username, password, name, dept_id, email, phone, status) VALUES
('admin', 'admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '系统管理员', '1', 'admin@updg.com', '13800138000', 1);

INSERT INTO pm_sys_role (role_id, role_name, role_code, description, status) VALUES
('1', '管理员', 'admin', '系统管理员角色', 1),
('2', '普通用户', 'user', '普通用户角色', 1);

INSERT INTO pm_sys_user_role (user_id, role_id) VALUES
('admin', '1');

-- Insert sample projects
INSERT INTO pm_project (project_id, project_name, project_code, project_type, status, manager_id, manager_name, department_name, start_date, end_date, budget, customer, description, progress) VALUES
('proj001', '数字化运营平台建设', 'PRJ-2026-001', 'internal', 'active', 'admin', '张经理', '信息技术部', '2026-01-01', '2026-12-31', 5000000.00, '内部客户', '建设一站式项目数字化运营管理平台', 45),
('proj002', '核心系统升级改造', 'PRJ-2026-002', 'internal', 'planning', 'admin', '李经理', '研发中心', '2026-03-01', '2026-09-30', 2000000.00, '内部客户', '核心业务系统升级改造项目', 10),
('proj003', '智能风控系统建设', 'PRJ-2026-003', 'internal', 'draft', 'admin', '王经理', '风险管理部', '2026-04-01', '2026-10-31', 3000000.00, '内部客户', '构建智能风险控制系统', 0);

-- Insert sample resource pools (ALIGNED)
INSERT INTO pm_resource_pool (pool_id, pool_name, manager_id, description, create_time) VALUES
('pool001', '开发团队', 'admin', '核心开发人员池', CURRENT_TIMESTAMP),
('pool002', '测试团队', 'admin', '测试人员池', CURRENT_TIMESTAMP);

-- Insert sample contracts (ALIGNED)
INSERT INTO pm_contract (contract_id, contract_code, contract_name, contract_type, party_a, party_b, total_amount, currency, sign_date, start_date, end_date, status) VALUES
('contract001', 'HT-2026-001', '软件开发服务合同', 'sales', 'UPDG', '科技公司A', 500000.00, 'CNY', '2026-01-15', '2026-01-01', '2026-12-31', 'active'),
('contract002', 'HT-2026-002', '服务器采购合同', 'purchase', '服务器厂商B', 'UPDG', 200000.00, 'CNY', '2026-02-20', '2026-02-01', '2026-06-30', 'active');

-- Insert sample budgets (ALIGNED)
INSERT INTO pm_budget (budget_id, project_id, budget_year, total_budget, labor_budget, outsource_budget, procurement_budget, other_budget, status) VALUES
('budget001', 'proj001', 2026, 5000000.00, 2000000.00, 1500000.00, 1000000.00, 500000.00, 'APPROVED'),
('budget002', 'proj002', 2026, 2000000.00, 1000000.00, 500000.00, 300000.00, 200000.00, 'DRAFT');

-- Insert sample timesheets (ALIGNED)
INSERT INTO pm_timesheet (timesheet_id, staff_id, project_id, work_date, hours, check_status, remark) VALUES
('ts001', 'admin', 'proj001', '2026-04-25', 8.0, 'approved', '开发工作'),
('ts002', 'admin', 'proj001', '2026-04-26', 6.0, 'pending', '测试工作');
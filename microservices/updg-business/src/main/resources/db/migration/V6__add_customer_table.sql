-- V6__add_customer_table.sql
-- External customer archive table

CREATE TABLE IF NOT EXISTS pm_customer (
    customer_id       VARCHAR(64)    NOT NULL COMMENT 'Customer ID',
    name              VARCHAR(256)   NOT NULL COMMENT 'Customer name',
    type              VARCHAR(32)    COMMENT 'Type: ENTERPRISE/GOVERNMENT/INDIVIDUAL',
    industry          VARCHAR(128)   COMMENT 'Industry',
    contact_person    VARCHAR(128)   COMMENT 'Contact person',
    phone             VARCHAR(32)    COMMENT 'Phone number',
    email             VARCHAR(128)   COMMENT 'Email',
    address           VARCHAR(512)   COMMENT 'Address',
    credit_code       VARCHAR(64)    COMMENT 'Unified credit code',
    rating            VARCHAR(16)    COMMENT 'Customer rating',
    status            VARCHAR(32)    DEFAULT 'ACTIVE' COMMENT 'Status',
    notes             VARCHAR(2000)  COMMENT 'Notes',
    created_at        VARCHAR(32)    COMMENT 'Created time',
    updated_at        VARCHAR(32)    COMMENT 'Updated time',
    PRIMARY KEY (customer_id),
    INDEX idx_name (name),
    INDEX idx_type (type),
    INDEX idx_industry (industry)
) COMMENT 'Customer archive table';

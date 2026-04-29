-- V6__add_customer_table.sql
-- External customer archive table (H2)

CREATE TABLE IF NOT EXISTS pm_customer (
    customer_id       VARCHAR(64)    NOT NULL,
    name              VARCHAR(256)   NOT NULL,
    type              VARCHAR(32),
    industry          VARCHAR(128),
    contact_person    VARCHAR(128),
    phone             VARCHAR(32),
    email             VARCHAR(128),
    address           VARCHAR(512),
    credit_code       VARCHAR(64),
    rating            VARCHAR(16),
    status            VARCHAR(32)    DEFAULT 'ACTIVE',
    notes             VARCHAR(2000),
    created_at        VARCHAR(32),
    updated_at        VARCHAR(32),
    PRIMARY KEY (customer_id)
);

CREATE INDEX IF NOT EXISTS idx_cust_name ON pm_customer(name);
CREATE INDEX IF NOT EXISTS idx_cust_type ON pm_customer(type);
CREATE INDEX IF NOT EXISTS idx_cust_industry ON pm_customer(industry);

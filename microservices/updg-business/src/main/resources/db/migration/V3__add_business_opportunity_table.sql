-- V3__add_business_opportunity_table.sql
-- Business opportunity management table

CREATE TABLE IF NOT EXISTS pm_business_opportunity (
    opportunity_id    VARCHAR(64)    NOT NULL COMMENT 'Opportunity ID',
    name              VARCHAR(256)   NOT NULL COMMENT 'Opportunity name',
    customer_id       VARCHAR(64)    COMMENT 'Customer ID',
    stage             VARCHAR(32)    DEFAULT 'LEAD' COMMENT 'Stage: LEAD/QUALIFIED/PROPOSAL/NEGOTIATION/WON/LOST',
    estimated_value   DECIMAL(18,2)  COMMENT 'Estimated value',
    probability       INT            DEFAULT 10 COMMENT 'Win probability percentage',
    owner_id          VARCHAR(64)    COMMENT 'Owner user ID',
    expected_close_date VARCHAR(32)  COMMENT 'Expected close date',
    source            VARCHAR(128)   COMMENT 'Lead source',
    description       VARCHAR(2000)  COMMENT 'Description',
    project_id        VARCHAR(64)    COMMENT 'Linked project ID (when won)',
    created_at        VARCHAR(32)    COMMENT 'Created time',
    updated_at        VARCHAR(32)    COMMENT 'Updated time',
    PRIMARY KEY (opportunity_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_stage (stage),
    INDEX idx_owner_id (owner_id)
) COMMENT 'Business opportunity table';

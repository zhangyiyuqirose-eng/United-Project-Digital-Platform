-- V3__add_business_opportunity_table.sql
-- Business opportunity management table (H2)

CREATE TABLE IF NOT EXISTS pm_business_opportunity (
    opportunity_id    VARCHAR(64)    NOT NULL,
    name              VARCHAR(256)   NOT NULL,
    customer_id       VARCHAR(64),
    stage             VARCHAR(32)    DEFAULT 'LEAD',
    estimated_value   DECIMAL(18,2),
    probability       INT            DEFAULT 10,
    owner_id          VARCHAR(64),
    expected_close_date VARCHAR(32),
    source            VARCHAR(128),
    description       VARCHAR(2000),
    project_id        VARCHAR(64),
    created_at        VARCHAR(32),
    updated_at        VARCHAR(32),
    PRIMARY KEY (opportunity_id)
);

CREATE INDEX IF NOT EXISTS idx_opp_customer_id ON pm_business_opportunity(customer_id);
CREATE INDEX IF NOT EXISTS idx_opp_stage ON pm_business_opportunity(stage);
CREATE INDEX IF NOT EXISTS idx_opp_owner_id ON pm_business_opportunity(owner_id);

-- V4__add_quotation_table.sql
-- Quotation management table (H2)

CREATE TABLE IF NOT EXISTS pm_quotation (
    quotation_id      VARCHAR(64)    NOT NULL,
    opportunity_id    VARCHAR(64),
    project_id        VARCHAR(64),
    quote_number      VARCHAR(64)    NOT NULL,
    total_price       DECIMAL(18,2),
    tax_rate          DECIMAL(5,2),
    valid_until       VARCHAR(32),
    status            VARCHAR(32)    DEFAULT 'DRAFT',
    items             TEXT,
    created_by        VARCHAR(64),
    created_at        VARCHAR(32),
    updated_at        VARCHAR(32),
    PRIMARY KEY (quotation_id)
);

CREATE INDEX IF NOT EXISTS idx_quote_opp_id ON pm_quotation(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_quote_proj_id ON pm_quotation(project_id);
CREATE INDEX IF NOT EXISTS idx_quote_status ON pm_quotation(status);

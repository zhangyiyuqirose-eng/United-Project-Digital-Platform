-- V4__add_quotation_table.sql
-- Quotation management table

CREATE TABLE IF NOT EXISTS pm_quotation (
    quotation_id      VARCHAR(64)    NOT NULL COMMENT 'Quotation ID',
    opportunity_id    VARCHAR(64)    COMMENT 'Related opportunity ID',
    project_id        VARCHAR(64)    COMMENT 'Related project ID',
    quote_number      VARCHAR(64)    NOT NULL COMMENT 'Quote number',
    total_price       DECIMAL(18,2)  COMMENT 'Total price',
    tax_rate          DECIMAL(5,2)   COMMENT 'Tax rate percentage',
    valid_until       VARCHAR(32)    COMMENT 'Validity end date',
    status            VARCHAR(32)    DEFAULT 'DRAFT' COMMENT 'Status: DRAFT/SENT/ACCEPTED/REJECTED/EXPIRED',
    items             TEXT           COMMENT 'Quotation items as JSON',
    created_by        VARCHAR(64)    COMMENT 'Created by user ID',
    created_at        VARCHAR(32)    COMMENT 'Created time',
    updated_at        VARCHAR(32)    COMMENT 'Updated time',
    PRIMARY KEY (quotation_id),
    INDEX idx_opportunity_id (opportunity_id),
    INDEX idx_project_id (project_id),
    INDEX idx_status (status)
) COMMENT 'Quotation table';

-- V6__add_health_score_column.sql
ALTER TABLE pm_project ADD COLUMN IF NOT EXISTS health_score DECIMAL(5,2) DEFAULT 0;

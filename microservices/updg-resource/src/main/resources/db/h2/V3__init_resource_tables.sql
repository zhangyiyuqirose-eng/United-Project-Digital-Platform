-- V3__init_resource_tables.sql (H2 compatible)
-- Note: Removed ShardingSphere PARTITION BY HASH for H2

CREATE TABLE IF NOT EXISTS pm_resource_outsourcing (
    staff_id    VARCHAR(64)  NOT NULL,
    name        VARCHAR(32)  NOT NULL,
    id_card     VARCHAR(32),
    skill       VARCHAR(256),
    resource_pool VARCHAR(64),
    entry_time  TIMESTAMP,
    exit_time   TIMESTAMP,
    rate        DECIMAL(10,2),
    status      VARCHAR(16)  DEFAULT 'ACTIVE',
    create_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (staff_id)
);

CREATE TABLE IF NOT EXISTS pm_resource_pool (
    pool_id     VARCHAR(64)  NOT NULL,
    pool_name   VARCHAR(64)  NOT NULL,
    manager_id  VARCHAR(64),
    description VARCHAR(256),
    create_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pool_id)
);

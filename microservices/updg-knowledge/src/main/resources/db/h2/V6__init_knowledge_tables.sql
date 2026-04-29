-- V6__init_knowledge_tables.sql (H2 compatible)

CREATE TABLE IF NOT EXISTS pm_knowledge_doc (
    doc_id        VARCHAR(64)  NOT NULL,
    title         VARCHAR(128),
    category      VARCHAR(64),
    template_type VARCHAR(64),
    file_path     VARCHAR(256),
    version       VARCHAR(16),
    created_by    VARCHAR(64),
    version_num   INT          DEFAULT 1,
    create_time   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    update_time   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (doc_id)
);

CREATE TABLE IF NOT EXISTS pm_knowledge_template (
    template_id   VARCHAR(64)  NOT NULL,
    template_name VARCHAR(128) NOT NULL,
    template_type VARCHAR(64),
    content       CLOB,
    create_time   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (template_id)
);

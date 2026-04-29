CREATE TABLE pm_meeting (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(32) NOT NULL,
    project_id VARCHAR(36),
    organizer VARCHAR(36),
    attendees TEXT,
    scheduled_at TIMESTAMP,
    location VARCHAR(200),
    agenda TEXT,
    status VARCHAR(16) NOT NULL,
    minutes TEXT,
    created_at TIMESTAMP
);

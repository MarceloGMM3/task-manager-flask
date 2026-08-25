DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS schema_migrations;

CREATE TABLE task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    is_completed INTEGER NOT NULL DEFAULT 0 CHECK (is_completed IN (0, 1)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_task_listing
ON task (is_completed ASC, created_at DESC, id DESC);

CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (version) VALUES ('0001_optimize_task_listing');

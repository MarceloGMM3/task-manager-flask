DROP INDEX IF EXISTS idx_task_is_completed;

CREATE INDEX IF NOT EXISTS idx_task_listing
ON task (is_completed ASC, created_at DESC, id DESC);

-- Migration: Add Academic Formula Fields
-- Date: 2026-02-03
-- Purpose: Add fields required for explicit formula calculations

-- Add completion_timestamp to tasks table (Formula 1)
ALTER TABLE tasks ADD COLUMN completion_timestamp TIMESTAMP NULL;

-- Add delay_duration to delays table (Formula 4)
ALTER TABLE delays ADD COLUMN delay_duration INT DEFAULT 0 COMMENT 'Delay duration in minutes (Formula 4)';

-- Add index for better performance on completion queries
CREATE INDEX idx_tasks_completion ON tasks(completion_timestamp);
CREATE INDEX idx_tasks_status ON tasks(status);

-- Add index for delay queries
CREATE INDEX idx_delays_user ON delays(user_id, submitted_at);

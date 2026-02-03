-- Optimizing for Time Complexity: Adding Indexes to frequently searched columns

-- Tasks Table Indexes
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);

-- Delays Table Indexes
CREATE INDEX idx_delays_user_id ON delays(user_id);
CREATE INDEX idx_delays_task_id ON delays(task_id);
CREATE INDEX idx_delays_risk_level ON delays(risk_level);

-- Audit Logs Indexes (Time based searching)
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Users Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

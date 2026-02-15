-- PostgreSQL Schema for Supabase
-- Task Management System with AI-powered Delay Analysis

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('employee', 'manager', 'admin')) DEFAULT 'employee',
    active_status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    priority VARCHAR(50) DEFAULT 'Medium',
    deadline DATE,
    estimated_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_timestamp TIMESTAMP NULL,
    CONSTRAINT chk_status CHECK (status IN ('Pending', 'In Progress', 'Completed', 'Delayed')),
    CONSTRAINT chk_priority CHECK (priority IN ('Low', 'Medium', 'High'))
);

-- Create indexes for tasks
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_created_by ON tasks(created_by);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline);

-- Attachments/Resources table
CREATE TABLE IF NOT EXISTS attachments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    resource_type VARCHAR(50),
    url_or_path TEXT,
    title VARCHAR(255),
    ai_summary TEXT,
    requirements_json JSONB,
    deadlines_json JSONB,
    completeness_score INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_attachments_task_id ON attachments(task_id);

-- Delays table
CREATE TABLE IF NOT EXISTS delays (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reason_text TEXT,
    reason_audio_path TEXT,
    score_authenticity INTEGER CHECK (score_authenticity BETWEEN 0 AND 100),
    score_avoidance INTEGER CHECK (score_avoidance BETWEEN 0 AND 100),
    risk_level VARCHAR(50) CHECK (risk_level IN ('Low', 'Medium', 'High')),
    ai_feedback TEXT,
    ai_analysis_json JSONB,
    delay_duration INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_delays_task_id ON delays(task_id);
CREATE INDEX IF NOT EXISTS idx_delays_user_id ON delays(user_id);
CREATE INDEX IF NOT EXISTS idx_delays_risk_level ON delays(risk_level);

-- Resource access logs
CREATE TABLE IF NOT EXISTS resource_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    attachment_id INTEGER REFERENCES attachments(id) ON DELETE CASCADE,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_resource_logs_user_id ON resource_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_resource_logs_attachment_id ON resource_logs(attachment_id);

-- Audit logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- Insert default admin user (password: admin123)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (full_name, email, password_hash, role, active_status)
VALUES (
    'System Administrator',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIpKWpceaG',
    'admin',
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- Create view for task statistics
CREATE OR REPLACE VIEW task_statistics AS
SELECT 
    u.id as user_id,
    u.full_name,
    u.email,
    u.role,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'Completed' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.status = 'Delayed' THEN 1 END) as delayed_tasks,
    COUNT(CASE WHEN t.status = 'Pending' THEN 1 END) as pending_tasks,
    COUNT(d.id) as total_delays,
    AVG(d.score_authenticity) as avg_authenticity_score
FROM users u
LEFT JOIN tasks t ON t.assigned_to = u.id
LEFT JOIN delays d ON d.user_id = u.id
GROUP BY u.id, u.full_name, u.email, u.role;

-- Enable Row Level Security (RLS) - Recommended for Production
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE delays ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Secure View (Respect RLS)
ALTER VIEW task_statistics SET (security_invoker = true);

-- Simple RLS Policies (uncomment if needed)
-- Note: These policies assume you're using Supabase Auth
-- If using custom Flask auth, you may not need RLS

-- CREATE POLICY users_select_all ON users
--     FOR SELECT
--     USING (true);  -- Allow all reads (Flask handles auth)

-- CREATE POLICY tasks_select_all ON tasks
--     FOR SELECT
--     USING (true);  -- Allow all reads (Flask handles auth)

-- CREATE POLICY delays_select_all ON delays
--     FOR SELECT
--     USING (true);  -- Allow all reads (Flask handles auth)

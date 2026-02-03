-- TiDB / MySQL Compatible Schema

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('employee', 'manager', 'admin') DEFAULT 'employee',
    active_status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_to INT,
    created_by INT,
    status VARCHAR(50) DEFAULT 'Pending',
    priority VARCHAR(50) DEFAULT 'Medium',
    deadline DATE,
    estimated_minutes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_timestamp TIMESTAMP NULL COMMENT 'Formula 1: Used to calculate elapsed_time',
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT,
    resource_type VARCHAR(50), -- 'file', 'link'
    url_or_path TEXT,
    title VARCHAR(255),
    ai_summary TEXT,
    requirements_json JSON,
    deadlines_json JSON,
    completeness_score INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS delays (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT,
    user_id INT,
    reason_text TEXT,
    reason_audio_path TEXT,
    score_authenticity INT COMMENT 'Formula 11: Rule-based score (0-100)', 
    score_avoidance INT COMMENT 'Formula 12: 100 - authenticity',
    risk_level VARCHAR(50) COMMENT 'Formulas 16-18: Low/Medium/High based on delay_count', 
    ai_feedback TEXT COMMENT 'Supplementary AI feedback (not used for scoring)',
    ai_analysis_json JSON COMMENT 'Stores rule breakdown and category',
    delay_duration INT DEFAULT 0 COMMENT 'Formula 4: elapsed_time - estimated_time (minutes)',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS resource_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    attachment_id INT,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (attachment_id) REFERENCES attachments(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(255),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

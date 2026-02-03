-- RBAC Permission System Migration
-- Run this after schema.sql

-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code (code)
);

-- Create role_permissions junction table
CREATE TABLE IF NOT EXISTS role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role VARCHAR(50) NOT NULL,
    permission_code VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_role_permission (role, permission_code),
    FOREIGN KEY (permission_code) REFERENCES permissions(code) ON DELETE CASCADE,
    INDEX idx_role (role)
);

-- Seed permission data
INSERT INTO permissions (code, description) VALUES
('VIEW_DASHBOARD', 'Access main dashboard'),
('VIEW_TASKS', 'View tasks'),
('CREATE_TASK', 'Create new tasks'),
('EDIT_TASK', 'Edit existing tasks'),
('DELETE_TASK', 'Delete tasks'),
('VIEW_ANALYTICS', 'View analytics and reports'),
('MANAGE_EMPLOYEES', 'View and manage employee profiles'),
('ADMIN_PANEL', 'Access admin panel'),
('VIEW_AUDIT_LOGS', 'View system audit logs'),
('EDIT_PROFILE', 'Edit own profile'),
('MANAGE_ROLES', 'Change user roles'),
('USE_CHATBOT', 'Access AI chatbot');

-- Employee Role Permissions
INSERT INTO role_permissions (role, permission_code) VALUES
('employee', 'VIEW_DASHBOARD'),
('employee', 'VIEW_TASKS'),
('employee', 'EDIT_PROFILE'),
('employee', 'USE_CHATBOT');

-- Manager Role Permissions
INSERT INTO role_permissions (role, permission_code) VALUES
('manager', 'VIEW_DASHBOARD'),
('manager', 'VIEW_TASKS'),
('manager', 'CREATE_TASK'),
('manager', 'EDIT_TASK'),
('manager', 'VIEW_ANALYTICS'),
('manager', 'MANAGE_EMPLOYEES'),
('manager', 'EDIT_PROFILE'),
('manager', 'USE_CHATBOT');

-- Admin Role Permissions (all permissions)
INSERT INTO role_permissions (role, permission_code) VALUES
('admin', 'VIEW_DASHBOARD'),
('admin', 'VIEW_TASKS'),
('admin', 'CREATE_TASK'),
('admin', 'EDIT_TASK'),
('admin', 'DELETE_TASK'),
('admin', 'VIEW_ANALYTICS'),
('admin', 'MANAGE_EMPLOYEES'),
('admin', 'ADMIN_PANEL'),
('admin', 'VIEW_AUDIT_LOGS'),
('admin', 'EDIT_PROFILE'),
('admin', 'MANAGE_ROLES'),
('admin', 'USE_CHATBOT');

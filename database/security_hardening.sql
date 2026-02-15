-- Security Hardening Migration
-- Run this in Supabase SQL Editor

-- 1. Enable Row Level Security (RLS) on all tables
-- This blocks all access via API unless policies exist (or Service Role is used)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE delays ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 2. Secure the Analytics View
-- Forces the view to check RLS permissions of the invoking user
-- Resolves "Security Advisor" warnings
ALTER VIEW task_statistics SET (security_invoker = true);

-- Note: 
-- Backend (Flask) connects as 'postgres' or uses Service Role Key, so it bypasses RLS.
-- Frontend (if used) using Anon Key will be BLOCKED until you add specific Policies.

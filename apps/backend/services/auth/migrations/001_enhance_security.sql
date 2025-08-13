-- Migration: Enhance Authentication and Security Infrastructure
-- Add new columns to users table for enhanced security

-- Add new columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS backup_codes TEXT[];
ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';
ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'ru';
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP DEFAULT NOW()
);

-- Create indexes for user_sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token_hash ON user_sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Create rate_limits table
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    attempts INTEGER DEFAULT 0,
    window_start TIMESTAMP DEFAULT NOW(),
    blocked_until TIMESTAMP
);

-- Create indexes for rate_limits
CREATE INDEX IF NOT EXISTS idx_rate_limits_identifier ON rate_limits(identifier);
CREATE INDEX IF NOT EXISTS idx_rate_limits_endpoint ON rate_limits(endpoint);
CREATE INDEX IF NOT EXISTS idx_rate_limits_blocked_until ON rate_limits(blocked_until);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_description TEXT NOT NULL,
    ip_address INET,
    user_agent TEXT,
    endpoint VARCHAR(255),
    request_id VARCHAR(100),
    metadata TEXT,
    severity VARCHAR(20) DEFAULT 'info',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for audit_logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON audit_logs(severity);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_request_id ON audit_logs(request_id);

-- Add constraints
ALTER TABLE user_sessions ADD CONSTRAINT chk_user_sessions_expires_at CHECK (expires_at > created_at);
ALTER TABLE audit_logs ADD CONSTRAINT chk_audit_logs_severity CHECK (severity IN ('info', 'warning', 'error', 'critical'));

-- Update existing users to have default values for new columns
UPDATE users SET 
    is_verified = FALSE,
    failed_login_attempts = 0,
    timezone = 'UTC',
    language = 'ru'
WHERE is_verified IS NULL OR failed_login_attempts IS NULL OR timezone IS NULL OR language IS NULL;
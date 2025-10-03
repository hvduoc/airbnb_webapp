-- Create user authentication tables
-- Migration: add User and UserSession tables

-- Create User table
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL, 
    full_name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    
    -- Role-based access control
    role VARCHAR DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    is_verified BOOLEAN DEFAULT 0 NOT NULL,
    
    -- Audit trail
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    last_login DATETIME,
    
    -- Property access control (JSON list)
    accessible_properties TEXT DEFAULT '[]'
);

-- Create UserSession table for session tracking
CREATE TABLE IF NOT EXISTS usersession (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_jti VARCHAR UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    ip_address VARCHAR,
    user_agent TEXT,
    
    FOREIGN KEY (user_id) REFERENCES user (id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_user_username ON user(username);
CREATE INDEX IF NOT EXISTS idx_user_role ON user(role);
CREATE INDEX IF NOT EXISTS idx_usersession_user_id ON usersession(user_id);
CREATE INDEX IF NOT EXISTS idx_usersession_token_jti ON usersession(token_jti);
CREATE INDEX IF NOT EXISTS idx_usersession_active ON usersession(is_active, expires_at);

-- Insert default admin user (password: admin123)
-- Password hash for "admin123" using bcrypt
INSERT OR IGNORE INTO user (
    email, username, full_name, hashed_password, role, is_active, is_verified, accessible_properties
) VALUES (
    'admin@airbnb.local',
    'admin', 
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYkAONRpjQ7S8Cu',
    'admin',
    1,
    1,
    '[]'
);

-- Insert demo user (password: user123)  
INSERT OR IGNORE INTO user (
    email, username, full_name, hashed_password, role, is_active, is_verified, accessible_properties
) VALUES (
    'user@airbnb.local',
    'user',
    'Demo User', 
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
    'user',
    1,
    1,
    '[1, 2, 3]'
);
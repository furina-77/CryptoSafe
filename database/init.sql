"""
PostgreSQL 数据库初始化脚本
密钥元数据存储和审计日志
"""

-- 创建密钥表
CREATE TABLE IF NOT EXISTS keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_type VARCHAR(50) NOT NULL,  -- symmetric, asymmetric_public, asymmetric_private, hmac
    algorithm VARCHAR(50) NOT NULL,  -- AES-256, RSA-2048, SM2, SM4, etc.
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, disabled, deleted, expired
    description TEXT,
    tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    rotation_days INTEGER DEFAULT 90
);

-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_id UUID REFERENCES keys(id) ON DELETE CASCADE,
    operation VARCHAR(20) NOT NULL,  -- CREATE, ENABLE, DISABLE, DELETE, EXPORT, ROTATE
    operator VARCHAR(100) DEFAULT 'system',
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_keys_status ON keys(status);
CREATE INDEX IF NOT EXISTS idx_keys_algorithm ON keys(algorithm);
CREATE INDEX IF NOT EXISTS idx_audit_logs_key_id ON audit_logs(key_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_keys_updated_at BEFORE UPDATE ON keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入测试数据（可选）
-- INSERT INTO keys (key_type, algorithm, description, tags) VALUES
-- ('symmetric', 'AES-256', '测试密钥', '["test", "dev"]');

-- 邮件验证功能数据库字段添加脚本
-- 作者: 王梓涵
-- 邮箱: wangzh011031@163.com
-- 时间: 2025年

-- 添加邮箱验证相关字段到用户表
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE;

-- 添加注释
COMMENT ON COLUMN users.email_verified IS '邮箱是否已验证';
COMMENT ON COLUMN users.email_verified_at IS '邮箱验证时间';

-- 显示表结构确认
\d users;


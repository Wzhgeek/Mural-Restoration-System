-- 克孜尔石窟壁画智慧修复全生命周期管理系统 - 数据库表结构SQL脚本
-- 作者: 王梓涵
-- 邮箱: wangzh011031@163.com
-- 时间: 2025年

-- 创建数据库（如果不存在）
-- CREATE DATABASE repair_system;

-- 使用数据库
-- \c repair_system;

-- 创建角色表
CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    role_key VARCHAR(20) UNIQUE NOT NULL,
    role_name VARCHAR(50) NOT NULL
);

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(role_id),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    unit VARCHAR(100),  -- 用户单位字段
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 创建工作流表
CREATE TABLE IF NOT EXISTS workflows (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    initiator_id INTEGER NOT NULL REFERENCES users(user_id),
    current_step INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft',
    is_finalized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 创建表单表
CREATE TABLE IF NOT EXISTS forms (
    form_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id),
    step_no INTEGER NOT NULL,
    submitter_id INTEGER NOT NULL REFERENCES users(user_id),
    image_url TEXT,
    image_meta JSONB,
    image_desc TEXT,
    image_desc_file TEXT,
    restoration_opinion TEXT,
    opinion_tags TEXT[],
    opinion_file TEXT,
    remark TEXT,
    attachment TEXT,
    is_rollback_from UUID REFERENCES forms(form_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 创建步骤日志表
CREATE TABLE IF NOT EXISTS step_logs (
    step_log_id SERIAL PRIMARY KEY,
    form_id UUID NOT NULL REFERENCES forms(form_id),
    action VARCHAR(20) NOT NULL,
    operator_id INTEGER NOT NULL REFERENCES users(user_id),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建评估表
CREATE TABLE IF NOT EXISTS evaluations (
    evaluate_id SERIAL PRIMARY KEY,
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id),
    evaluator_id INTEGER NOT NULL REFERENCES users(user_id),
    score SMALLINT CHECK (score >= 0 AND score <= 100),
    comment TEXT,
    evaluation_file TEXT,
    personnel_confirmation VARCHAR(200),  -- 人员确认字段（用户名+单位）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建回溯请求表
CREATE TABLE IF NOT EXISTS rollback_requests (
    rollback_id SERIAL PRIMARY KEY,
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id),
    requester_id INTEGER NOT NULL REFERENCES users(user_id),
    target_form_id UUID NOT NULL REFERENCES forms(form_id),
    reason TEXT NOT NULL,
    support_file_url TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approver_id INTEGER REFERENCES users(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    config_key VARCHAR(50) PRIMARY KEY,
    config_value TEXT,
    description VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建知识体系文件表
CREATE TABLE IF NOT EXISTS knowledge_system_files (
    id SERIAL PRIMARY KEY,
    unit VARCHAR(100) NOT NULL,  -- 单位或提供人
    filename VARCHAR(255) NOT NULL,  -- 文件名
    file_url TEXT NOT NULL,  -- 文件链接（MinIO存储桶）
    file_type VARCHAR(20) NOT NULL,  -- 文件类型：doc, jpg, png, pdf, docx, caj, xlsx, tif等
    submission_info VARCHAR(100) NOT NULL,  -- 提交信息：论文，洞窟照片，建模文件，海外残片，绘画手稿
    status VARCHAR(20) DEFAULT 'active',  -- 状态：active, archived, deleted
    remark TEXT,  -- 备注
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE  -- 软删除字段
);

-- 插入基础角色数据
INSERT INTO roles (role_key, role_name) VALUES 
    ('admin', '管理员'),
    ('restorer', '修复专家'),
    ('evaluator', '评估专家')
ON CONFLICT (role_key) DO NOTHING;

-- 插入默认管理员用户（密码: admin123）
INSERT INTO users (username, password_hash, full_name, role_id, email) VALUES 
    ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8.5.5.2', '系统管理员', 
     (SELECT role_id FROM roles WHERE role_key = 'admin'), 'admin@repair.com')
ON CONFLICT (username) DO NOTHING;

-- 插入测试用户（密码: 123456）
INSERT INTO users (username, password_hash, full_name, role_id, email, unit) VALUES 
    ('restorer1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8.5.5.2', '修复专家张三', 
     (SELECT role_id FROM roles WHERE role_key = 'restorer'), 'restorer1@repair.com', '克孜尔石窟研究院'),
    ('evaluator1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8.5.5.2', '评估专家李四', 
     (SELECT role_id FROM roles WHERE role_key = 'evaluator'), 'evaluator1@repair.com', '文物保护中心')
ON CONFLICT (username) DO NOTHING;

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, description) VALUES 
    ('privacy_agreement', '保密协议

尊敬的用户：

感谢您使用克孜尔石窟壁画智慧修复全生命周期管理系统。为了保护珍贵的文物信息和相关技术资料，请您仔细阅读并同意以下保密条款：

1. 保密义务
   您承诺对在使用本系统过程中接触到的所有壁画图像、修复技术、工艺流程等信息严格保密。

2. 信息安全
   未经授权，不得复制、传播、泄露任何系统中的文物信息。

3. 使用限制
   仅可将获得的信息用于指定的修复工作，不得用于其他商业或个人目的。

4. 责任承担
   如违反保密义务造成损失，将承担相应的法律责任。

请仔细阅读上述条款，点击"同意"按钮表示您已完全理解并同意遵守本保密协议。', '用户保密协议内容')
ON CONFLICT (config_key) DO NOTHING;

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_workflows_initiator_id ON workflows(initiator_id);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_forms_workflow_id ON forms(workflow_id);
CREATE INDEX IF NOT EXISTS idx_forms_submitter_id ON forms(submitter_id);
CREATE INDEX IF NOT EXISTS idx_step_logs_form_id ON step_logs(form_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_workflow_id ON evaluations(workflow_id);
CREATE INDEX IF NOT EXISTS idx_rollback_requests_workflow_id ON rollback_requests(workflow_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_files_unit ON knowledge_system_files(unit);
CREATE INDEX IF NOT EXISTS idx_knowledge_files_file_type ON knowledge_system_files(file_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_files_submission_info ON knowledge_system_files(submission_info);
CREATE INDEX IF NOT EXISTS idx_knowledge_files_status ON knowledge_system_files(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_files_created_at ON knowledge_system_files(created_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_files_deleted_at ON knowledge_system_files(deleted_at);

-- 显示创建结果
SELECT 'Database initialization completed successfully!' as message;

-- 知识体系文件存储功能已添加
-- 表: knowledge_system_files
-- MinIO存储桶: knowledge-files
-- 作者: 王梓涵
-- 时间: 2025年

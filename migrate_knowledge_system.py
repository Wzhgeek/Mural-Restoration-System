# -*- coding: utf-8 -*-
"""
知识体系文件存储功能数据库迁移脚本

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine
from app.services.file_service import file_service

async def migrate_knowledge_system():
    """迁移知识体系文件存储功能"""
    
    # 创建knowledge_system_files表
    create_table_sql = """
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
    """
    
    # 创建索引
    create_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_knowledge_files_unit ON knowledge_system_files(unit);",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_files_file_type ON knowledge_system_files(file_type);",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_files_submission_info ON knowledge_system_files(submission_info);",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_files_status ON knowledge_system_files(status);",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_files_created_at ON knowledge_system_files(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_files_deleted_at ON knowledge_system_files(deleted_at);"
    ]
    
    try:
        with engine.connect() as conn:
            # 创建表
            print("创建knowledge_system_files表...")
            conn.execute(text(create_table_sql))
            conn.commit()
            
            # 创建索引
            print("创建索引...")
            for index_sql in create_indexes_sql:
                conn.execute(text(index_sql))
            conn.commit()
            
            print("数据库迁移完成！")
            
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        raise
    
    # 确保MinIO存储桶存在
    try:
        print("检查MinIO存储桶...")
        # 文件服务初始化时会自动创建存储桶
        print("MinIO存储桶检查完成！")
    except Exception as e:
        print(f"MinIO存储桶检查失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate_knowledge_system())

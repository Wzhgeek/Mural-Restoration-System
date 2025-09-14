# -*- coding: utf-8 -*-
"""
知识体系文件存储功能数据库迁移脚本（简化版）

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
import psycopg2
import os
from minio import Minio
from minio.error import S3Error

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'repair_system',
    'user': 'postgres',
    'password': 'postgres123'
}

# MinIO配置
MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False
}

def migrate_database():
    """迁移数据库"""
    try:
        # 连接数据库
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建knowledge_system_files表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS knowledge_system_files (
            id SERIAL PRIMARY KEY,
            unit VARCHAR(100) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_url TEXT NOT NULL,
            file_type VARCHAR(20) NOT NULL,
            submission_info VARCHAR(100) NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            remark TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            deleted_at TIMESTAMP WITH TIME ZONE
        );
        """
        
        print("创建knowledge_system_files表...")
        cursor.execute(create_table_sql)
        
        # 创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_knowledge_files_unit ON knowledge_system_files(unit);",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_files_file_type ON knowledge_system_files(file_type);",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_files_submission_info ON knowledge_system_files(submission_info);",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_files_status ON knowledge_system_files(status);",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_files_created_at ON knowledge_system_files(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_files_deleted_at ON knowledge_system_files(deleted_at);"
        ]
        
        print("创建索引...")
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        print("数据库迁移完成！")
        
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def migrate_minio():
    """迁移MinIO存储桶"""
    try:
        # 连接MinIO
        client = Minio(
            MINIO_CONFIG['endpoint'],
            access_key=MINIO_CONFIG['access_key'],
            secret_key=MINIO_CONFIG['secret_key'],
            secure=MINIO_CONFIG['secure']
        )
        
        # 创建knowledge-files存储桶
        bucket_name = "knowledge-files"
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"创建MinIO存储桶: {bucket_name}")
        else:
            print(f"MinIO存储桶 {bucket_name} 已存在")
            
    except Exception as e:
        print(f"MinIO迁移失败: {e}")
        raise

if __name__ == "__main__":
    print("开始迁移知识体系文件存储功能...")
    
    # 迁移数据库
    migrate_database()
    
    # 迁移MinIO
    migrate_minio()
    
    print("迁移完成！")

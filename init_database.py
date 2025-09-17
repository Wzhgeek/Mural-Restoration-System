# -*- coding: utf-8 -*-
"""
克孜尔石窟壁画智慧修复全生命周期管理系统 - 数据库初始化脚本

本脚本用于：
1. 创建PostgreSQL数据库（如果不存在）
2. 创建所有数据表（包括知识体系文件存储表）
3. 应用所有数据库迁移（整合了所有migrate_*.py脚本的功能）
4. 初始化基础数据（角色、用户、系统配置等）
5. 更新测试数据（用户单位、工作流用户信息等）
6. 初始化MinIO存储桶（主存储桶和知识体系文件存储桶）


作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年

使用方法:
    python init_database.py

环境要求:
    - PostgreSQL 12+
    - Python 3.8+
    - 已安装项目依赖 (pip install -r requirements.txt)

功能特性:
    - 自动创建数据库和表结构
    - 应用所有数据库迁移（用户字段、邮件验证、多文件支持、工作流字段等）
    - 初始化基础角色和用户数据
    - 更新测试数据
    - 创建MinIO存储桶（如果MinIO服务可用）
    - 支持知识体系文件存储功能
    - 完整的错误处理和状态显示
    - 事务安全：所有迁移操作都在事务中执行，失败时自动回滚

整合的迁移功能:
    - migrate_database.py: 用户单位字段、评估表人员确认字段
    - migrate_email_verification.py: 邮件验证字段
    - migrate_knowledge_system.py: 知识体系文件存储表
    - migrate_multifile_support.py: 多文件上传支持字段
    - migrate_workflow_user_fields.py: 工作流表用户字段

"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.database import create_tables, init_data
from app.models import Base

def create_database_if_not_exists():
    """
    创建数据库（如果不存在）
    
    Returns:
        bool: 创建成功返回True，否则返回False
    """
    try:
        # 构建连接字符串（不包含数据库名）
        db_host = settings.POSTGRES_HOST
        db_port = settings.POSTGRES_PORT
        db_user = settings.POSTGRES_USER
        db_password = settings.POSTGRES_PASSWORD
        db_name = settings.POSTGRES_DB
        
        # 连接到PostgreSQL服务器（默认数据库）
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres'  # 连接到默认数据库
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        
        if cursor.fetchone():
            print(f"✅ 数据库 '{db_name}' 已存在")
        else:
            # 创建数据库
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ 数据库 '{db_name}' 创建成功")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ 数据库创建失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")
        print("请检查以下配置:")
        print(f"  - 主机: {settings.POSTGRES_HOST}")
        print(f"  - 端口: {settings.POSTGRES_PORT}")
        print(f"  - 用户名: {settings.POSTGRES_USER}")
        print(f"  - 密码: {'*' * len(settings.POSTGRES_PASSWORD)}")
        return False

def test_database_connection():
    """
    测试数据库连接
    
    Returns:
        bool: 连接成功返回True，否则返回False
    """
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ 数据库连接测试成功")
            return True
    except SQLAlchemyError as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def create_all_tables():
    """
    创建所有数据表
    
    Returns:
        bool: 创建成功返回True，否则返回False
    """
    try:
        print("📋 开始创建数据表...")
        create_tables()
        print("✅ 所有数据表创建完成")
        return True
    except Exception as e:
        print(f"❌ 数据表创建失败: {e}")
        return False

def apply_database_migrations():
    """
    应用所有数据库迁移
    
    Returns:
        bool: 迁移成功返回True，否则返回False
    """
    try:
        from app.core.database import engine
        
        print("🔧 开始应用数据库迁移...")
        
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 迁移1: 添加用户表unit字段和评估表personnel_confirmation字段
                print("  📝 迁移1: 添加用户单位和人员确认字段...")
                
                # 检查并添加用户表unit字段
                check_unit = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'unit'
                """)
                if not conn.execute(check_unit).fetchone():
                    conn.execute(text("ALTER TABLE users ADD COLUMN unit VARCHAR(100)"))
                    print("    ✅ 用户表unit字段添加成功")
                else:
                    print("    ℹ️ 用户表unit字段已存在")
                
                # 检查并添加评估表personnel_confirmation字段
                check_personnel = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'evaluations' AND column_name = 'personnel_confirmation'
                """)
                if not conn.execute(check_personnel).fetchone():
                    conn.execute(text("ALTER TABLE evaluations ADD COLUMN personnel_confirmation VARCHAR(200)"))
                    print("    ✅ 评估表personnel_confirmation字段添加成功")
                else:
                    print("    ℹ️ 评估表personnel_confirmation字段已存在")
                
                # 迁移2: 添加邮件验证字段
                print("  📝 迁移2: 添加邮件验证字段...")
                
                # 检查并添加email_verified字段
                check_email_verified = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'email_verified'
                """)
                if not conn.execute(check_email_verified).fetchone():
                    conn.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE"))
                    print("    ✅ email_verified字段添加成功")
                else:
                    print("    ℹ️ email_verified字段已存在")
                
                # 检查并添加email_verified_at字段
                check_email_verified_at = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'email_verified_at'
                """)
                if not conn.execute(check_email_verified_at).fetchone():
                    conn.execute(text("ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP WITH TIME ZONE"))
                    print("    ✅ email_verified_at字段添加成功")
                else:
                    print("    ℹ️ email_verified_at字段已存在")
                
                # 迁移3: 创建知识体系文件存储表
                print("  📝 迁移3: 创建知识体系文件存储表...")
                
                create_knowledge_table = text("""
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
                    )
                """)
                conn.execute(create_knowledge_table)
                print("    ✅ knowledge_system_files表创建成功")
                
                # 创建知识体系文件表索引
                knowledge_indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_files_unit ON knowledge_system_files(unit)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_files_file_type ON knowledge_system_files(file_type)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_files_submission_info ON knowledge_system_files(submission_info)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_files_status ON knowledge_system_files(status)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_files_created_at ON knowledge_system_files(created_at)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_files_deleted_at ON knowledge_system_files(deleted_at)"
                ]
                
                for index_sql in knowledge_indexes:
                    conn.execute(text(index_sql))
                print("    ✅ knowledge_system_files表索引创建成功")
                
                # 迁移4: 添加多文件上传支持字段
                print("  📝 迁移4: 添加多文件上传支持字段...")
                
                # 为forms表添加多文件字段
                forms_alterations = [
                    "ALTER TABLE forms ADD COLUMN IF NOT EXISTS image_urls JSONB",
                    "ALTER TABLE forms ADD COLUMN IF NOT EXISTS image_metas JSONB",
                    "ALTER TABLE forms ADD COLUMN IF NOT EXISTS image_desc_files JSONB",
                    "ALTER TABLE forms ADD COLUMN IF NOT EXISTS opinion_files JSONB",
                    "ALTER TABLE forms ADD COLUMN IF NOT EXISTS attachments JSONB"
                ]
                
                for sql in forms_alterations:
                    conn.execute(text(sql))
                print("    ✅ forms表多文件字段添加成功")
                
                # 为evaluations表添加多文件字段
                conn.execute(text("ALTER TABLE evaluations ADD COLUMN IF NOT EXISTS evaluation_files JSONB"))
                print("    ✅ evaluations表多文件字段添加成功")
                
                # 为rollback_requests表添加多文件字段
                conn.execute(text("ALTER TABLE rollback_requests ADD COLUMN IF NOT EXISTS support_file_urls JSONB"))
                print("    ✅ rollback_requests表多文件字段添加成功")
                
                # 迁移5: 添加工作流表用户字段
                print("  📝 迁移5: 添加工作流表用户字段...")
                
                # 添加user_id字段
                conn.execute(text("ALTER TABLE workflows ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(user_id)"))
                print("    ✅ workflows表user_id字段添加成功")
                
                # 添加username字段
                conn.execute(text("ALTER TABLE workflows ADD COLUMN IF NOT EXISTS username VARCHAR(50)"))
                print("    ✅ workflows表username字段添加成功")
                
                # 为工作流表字段创建索引
                workflow_indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_workflows_user_id ON workflows(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_workflows_username ON workflows(username)"
                ]
                
                for index_sql in workflow_indexes:
                    conn.execute(text(index_sql))
                print("    ✅ workflows表用户字段索引创建成功")
                
                # 提交事务
                trans.commit()
                print("✅ 所有数据库迁移完成")
                return True
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"❌ 数据库迁移失败，已回滚: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

def update_test_data():
    """
    更新测试数据
    
    Returns:
        bool: 更新成功返回True，否则返回False
    """
    try:
        from app.core.database import engine
        
        print("🔧 开始更新测试数据...")
        
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 更新测试用户单位信息
                conn.execute(text("""
                    UPDATE users 
                    SET unit = '克孜尔石窟研究院' 
                    WHERE username = 'restorer1'
                """))
                
                conn.execute(text("""
                    UPDATE users 
                    SET unit = '文物保护中心' 
                    WHERE username = 'evaluator1'
                """))
                
                # 更新工作流表用户数据
                conn.execute(text("""
                    UPDATE workflows 
                    SET user_id = initiator_id 
                    WHERE user_id IS NULL
                """))
                
                conn.execute(text("""
                    UPDATE workflows 
                    SET username = u.username 
                    FROM users u 
                    WHERE workflows.initiator_id = u.user_id 
                    AND workflows.username IS NULL
                """))
                
                # 提交事务
                trans.commit()
                print("✅ 测试数据更新完成")
                return True
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"❌ 测试数据更新失败，已回滚: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 测试数据更新失败: {e}")
        return False

def initialize_base_data():
    """
    初始化基础数据
    
    Returns:
        bool: 初始化成功返回True，否则返回False
    """
    try:
        print("📊 开始初始化基础数据...")
        init_data()
        print("✅ 基础数据初始化完成")
        return True
    except Exception as e:
        print(f"❌ 基础数据初始化失败: {e}")
        return False

def show_database_info():
    """
    显示数据库信息
    """
    print("\n" + "="*60)
    print("📊 数据库配置信息")
    print("="*60)
    print(f"数据库类型: PostgreSQL")
    print(f"主机地址: {settings.POSTGRES_HOST}")
    print(f"端口号: {settings.POSTGRES_PORT}")
    print(f"数据库名: {settings.POSTGRES_DB}")
    print(f"用户名: {settings.POSTGRES_USER}")
    print(f"连接URL: postgresql://{settings.POSTGRES_USER}:***@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    print("="*60)

def show_created_tables():
    """
    显示创建的表信息
    """
    print("\n📋 已创建的数据表:")
    tables = [
        "roles - 角色表",
        "users - 用户表（包含unit、email_verified、email_verified_at字段）", 
        "workflows - 工作流表（包含user_id、username字段）",
        "forms - 表单表（包含多文件上传支持字段）",
        "step_logs - 步骤日志表",
        "evaluations - 评估表（包含personnel_confirmation、evaluation_files字段）",
        "rollback_requests - 回溯请求表（包含support_file_urls字段）",
        "system_configs - 系统配置表",
        "knowledge_system_files - 知识体系文件表"
    ]
    
    for table in tables:
        print(f"  ✓ {table}")

def show_default_accounts():
    """
    显示默认账号信息
    """
    print("\n👥 默认账号信息:")
    print("  🔑 管理员账号:")
    print("     用户名: admin")
    print("     密码: admin123")
    print("     角色: 管理员")
    print("     邮箱: admin@repair.com")
    print()
    print("  🔧 修复专家账号:")
    print("     用户名: restorer1")
    print("     密码: 123456")
    print("     角色: 修复专家")
    print("     邮箱: restorer1@repair.com")
    print()
    print("  ⚖️ 评估专家账号:")
    print("     用户名: evaluator1")
    print("     密码: 123456")
    print("     角色: 评估专家")
    print("     邮箱: evaluator1@repair.com")

def show_migration_info():
    """
    显示迁移功能信息
    """
    print("\n🔧 已应用的数据库迁移:")
    print("  ✓ 用户表字段扩展: unit（用户单位）、email_verified（邮件验证状态）、email_verified_at（验证时间）")
    print("  ✓ 评估表字段扩展: personnel_confirmation（人员确认）、evaluation_files（评估文件）")
    print("  ✓ 工作流表字段扩展: user_id（用户ID）、username（用户名）")
    print("  ✓ 表单表多文件支持: image_urls、image_metas、image_desc_files、opinion_files、attachments")
    print("  ✓ 回溯请求表多文件支持: support_file_urls")
    print("  ✓ 知识体系文件存储表: 完整的文件管理功能")
    print("  ✓ 索引优化: 为所有新增字段创建了性能索引")

def show_knowledge_system_info():
    """
    显示知识体系文件功能信息
    """
    print("\n📚 知识体系文件存储功能:")
    print("  ✓ 支持多种文件类型: doc, jpg, png, pdf, docx, caj, xlsx, tif, ppt, pptx, txt, zip, rar")
    print("  ✓ 支持多种提交信息: 论文, 洞窟照片, 建模文件, 海外残片, 绘画手稿, 研究报告, 技术文档, 其他")
    print("  ✓ 完整的CRUD操作: 创建、读取、更新、删除文件记录")
    print("  ✓ 高级查询功能: 分页、筛选、搜索、排序")
    print("  ✓ 文件上传管理: 自动生成唯一文件名，按日期组织目录")
    print("  ✓ 统计功能: 按文件类型、提交信息、单位等维度统计")
    print("  ✓ 权限控制: 需要修复专家或以上权限")
    print("  ✓ 软删除机制: 支持数据恢复")
    print("  ✓ MinIO存储: 文件存储在knowledge-files存储桶中")

def initialize_minio_buckets():
    """
    初始化MinIO存储桶
    
    创建系统所需的所有MinIO存储桶：
    - repair-file: 主存储桶（一般文件存储）
    - knowledge-files: 知识体系文件存储桶
    - repair-images: 修复图片存储桶
    - archive-files: 归档文件存储桶
    
    Returns:
        bool: 初始化成功返回True，否则返回False
    """
    try:
        print("🪣 开始初始化MinIO存储桶...")
        
        # 导入MinIO相关模块
        from minio import Minio
        from minio.error import S3Error
        from app.core.config import settings
        
        # 创建MinIO客户端
        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        
        # 定义需要创建的存储桶
        buckets = [
            {
                "name": "repair-file",
                "description": "主存储桶（一般文件存储）"
            },
            {
                "name": "knowledge-files", 
                "description": "知识体系文件存储桶"
            },
            {
                "name": "repair-images",
                "description": "修复图片存储桶"
            },
            {
                "name": "archive-files",
                "description": "归档文件存储桶"
            }
        ]
        
        created_count = 0
        existing_count = 0
        
        for bucket_info in buckets:
            bucket_name = bucket_info["name"]
            description = bucket_info["description"]
            
            try:
                # 检查存储桶是否存在
                if client.bucket_exists(bucket_name):
                    print(f"  ✓ 存储桶 '{bucket_name}' 已存在 ({description})")
                    existing_count += 1
                else:
                    # 创建存储桶
                    client.make_bucket(bucket_name)
                    print(f"  ✅ 创建存储桶 '{bucket_name}' ({description})")
                    created_count += 1
                    
            except S3Error as e:
                print(f"  ❌ 创建存储桶 '{bucket_name}' 失败: {e}")
                continue
            except Exception as e:
                print(f"  ❌ 存储桶 '{bucket_name}' 操作异常: {e}")
                continue
        
        # 显示结果统计
        print(f"\n📊 MinIO存储桶初始化结果:")
        print(f"  ✅ 新创建: {created_count} 个存储桶")
        print(f"  ✓ 已存在: {existing_count} 个存储桶")
        print(f"  📝 总计: {created_count + existing_count} 个存储桶")
        
        if created_count > 0 or existing_count > 0:
            print("✅ MinIO存储桶初始化完成")
            return True
        else:
            print("⚠️ 没有成功创建或找到任何存储桶")
            return False
            
    except ImportError as e:
        print(f"❌ MinIO模块导入失败: {e}")
        print("⚠️ 请确保已安装MinIO依赖: pip install minio")
        return False
    except Exception as e:
        print(f"❌ MinIO存储桶初始化失败: {e}")
        print("⚠️ 请确保MinIO服务正在运行")
        return False


def main():
    """
    主函数 - 执行完整的数据库初始化流程
    """
    print("🚀 克孜尔石窟壁画智慧修复全生命周期管理系统")
    print("📊 数据库初始化脚本")
    print("="*60)
    
    # 显示数据库配置信息
    show_database_info()
    
    # 步骤1: 创建数据库（如果不存在）
    print("\n🔧 步骤1: 检查并创建数据库...")
    if not create_database_if_not_exists():
        print("❌ 数据库创建失败，初始化终止")
        sys.exit(1)
    
    # 步骤2: 测试数据库连接
    print("\n🔧 步骤2: 测试数据库连接...")
    if not test_database_connection():
        print("❌ 数据库连接失败，初始化终止")
        sys.exit(1)
    
    # 步骤3: 创建所有数据表
    print("\n🔧 步骤3: 创建数据表...")
    if not create_all_tables():
        print("❌ 数据表创建失败，初始化终止")
        sys.exit(1)
    
    # 步骤4: 应用数据库迁移
    print("\n🔧 步骤4: 应用数据库迁移...")
    if not apply_database_migrations():
        print("❌ 数据库迁移失败，初始化终止")
        sys.exit(1)
    
    # 步骤5: 初始化基础数据
    print("\n🔧 步骤5: 初始化基础数据...")
    if not initialize_base_data():
        print("❌ 基础数据初始化失败，初始化终止")
        sys.exit(1)
    
    # 步骤6: 更新测试数据
    print("\n🔧 步骤6: 更新测试数据...")
    if not update_test_data():
        print("❌ 测试数据更新失败，初始化终止")
        sys.exit(1)
    
    # 步骤7: 初始化MinIO存储桶
    print("\n🔧 步骤7: 初始化MinIO存储桶...")
    if not initialize_minio_buckets():
        print("⚠️ MinIO存储桶初始化失败，但数据库初始化已完成")
        print("⚠️ 请手动启动MinIO服务并创建存储桶")
    

    # 显示结果信息
    show_created_tables()
    show_migration_info()
    show_default_accounts()
    
    print("\n" + "="*60)
    print("🎉 数据库初始化完成！")
    print("="*60)
    print("现在您可以启动应用程序:")
    print("  python main.py")
    print("\n或者使用uvicorn启动:")
    print(f"  uvicorn main:app --host 0.0.0.0 --port {settings.APP_PORT}")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 初始化过程中发生错误: {e}")
        sys.exit(1)

# -*- coding: utf-8 -*-
"""
克孜尔石窟壁画智慧修复全生命周期管理系统 - 数据库初始化脚本

本脚本用于：
1. 创建PostgreSQL数据库（如果不存在）
2. 创建所有数据表
3. 初始化基础数据（角色、用户、系统配置等）

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年

使用方法:
    python init_database.py

环境要求:
    - PostgreSQL 12+
    - Python 3.8+
    - 已安装项目依赖 (pip install -r requirements.txt)
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
        "users - 用户表", 
        "workflows - 工作流表",
        "forms - 表单表",
        "step_logs - 步骤日志表",
        "evaluations - 评估表",
        "rollback_requests - 回溯请求表",
        "system_configs - 系统配置表"
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
    
    # 步骤4: 初始化基础数据
    print("\n🔧 步骤4: 初始化基础数据...")
    if not initialize_base_data():
        print("❌ 基础数据初始化失败，初始化终止")
        sys.exit(1)
    
    # 显示结果信息
    show_created_tables()
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

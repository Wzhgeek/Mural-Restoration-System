# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加用户单位字段和评估表人员确认字段

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年

本脚本用于：
1. 在用户表添加unit字段（用户单位）
2. 在评估表添加personnel_confirmation字段（人员确认）
3. 更新现有测试用户数据，添加单位信息

使用方法:
    python migrate_database.py
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

def check_column_exists(cursor, table_name, column_name):
    """
    检查表中是否存在指定列
    
    Args:
        cursor: 数据库游标
        table_name: 表名
        column_name: 列名
    
    Returns:
        bool: 存在返回True，否则返回False
    """
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s AND column_name = %s
    """, (table_name, column_name))
    return cursor.fetchone() is not None

def add_user_unit_column(cursor):
    """
    在用户表添加unit字段
    
    Args:
        cursor: 数据库游标
    
    Returns:
        bool: 添加成功返回True，否则返回False
    """
    try:
        # 检查字段是否已存在
        if check_column_exists(cursor, 'users', 'unit'):
            print("✅ 用户表unit字段已存在")
            return True
        
        # 添加unit字段
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN unit VARCHAR(100)
        """)
        print("✅ 用户表unit字段添加成功")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ 添加用户表unit字段失败: {e}")
        return False

def add_evaluation_personnel_confirmation_column(cursor):
    """
    在评估表添加personnel_confirmation字段
    
    Args:
        cursor: 数据库游标
    
    Returns:
        bool: 添加成功返回True，否则返回False
    """
    try:
        # 检查字段是否已存在
        if check_column_exists(cursor, 'evaluations', 'personnel_confirmation'):
            print("✅ 评估表personnel_confirmation字段已存在")
            return True
        
        # 添加personnel_confirmation字段
        cursor.execute("""
            ALTER TABLE evaluations 
            ADD COLUMN personnel_confirmation VARCHAR(200)
        """)
        print("✅ 评估表personnel_confirmation字段添加成功")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ 添加评估表personnel_confirmation字段失败: {e}")
        return False

def update_test_users_data(cursor):
    """
    更新测试用户数据，添加单位信息
    
    Args:
        cursor: 数据库游标
    
    Returns:
        bool: 更新成功返回True，否则返回False
    """
    try:
        # 更新测试用户数据
        cursor.execute("""
            UPDATE users 
            SET unit = '克孜尔石窟研究院' 
            WHERE username = 'restorer1'
        """)
        
        cursor.execute("""
            UPDATE users 
            SET unit = '文物保护中心' 
            WHERE username = 'evaluator1'
        """)
        
        print("✅ 测试用户单位信息更新成功")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ 更新测试用户数据失败: {e}")
        return False

def main():
    """
    主函数 - 执行数据库迁移
    """
    print("🚀 克孜尔石窟壁画智慧修复全生命周期管理系统")
    print("📊 数据库迁移脚本")
    print("="*60)
    
    try:
        # 连接数据库
        db_host = settings.POSTGRES_HOST
        db_port = settings.POSTGRES_PORT
        db_user = settings.POSTGRES_USER
        db_password = settings.POSTGRES_PASSWORD
        db_name = settings.POSTGRES_DB
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print(f"✅ 已连接到数据库: {db_name}")
        
        # 步骤1: 添加用户表unit字段
        print("\n🔧 步骤1: 添加用户表unit字段...")
        if not add_user_unit_column(cursor):
            print("❌ 用户表unit字段添加失败，迁移终止")
            sys.exit(1)
        
        # 步骤2: 添加评估表personnel_confirmation字段
        print("\n🔧 步骤2: 添加评估表personnel_confirmation字段...")
        if not add_evaluation_personnel_confirmation_column(cursor):
            print("❌ 评估表personnel_confirmation字段添加失败，迁移终止")
            sys.exit(1)
        
        # 步骤3: 更新测试用户数据
        print("\n🔧 步骤3: 更新测试用户单位信息...")
        if not update_test_users_data(cursor):
            print("❌ 测试用户数据更新失败，迁移终止")
            sys.exit(1)
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("🎉 数据库迁移完成！")
        print("="*60)
        print("新增字段说明:")
        print("  ✓ users.unit - 用户单位字段")
        print("  ✓ evaluations.personnel_confirmation - 人员确认字段（用户名+单位）")
        print("="*60)
        
    except psycopg2.Error as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查数据库配置和连接状态")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 迁移过程中发生错误: {e}")
        sys.exit(1)

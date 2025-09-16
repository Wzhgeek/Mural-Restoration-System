# -*- coding: utf-8 -*-
"""
克孜尔石窟壁画智慧修复全生命周期管理系统 - 工作流表字段迁移脚本

本脚本用于：
1. 在workflows表中添加user_id和username字段
2. 从initiator_id关联的users表获取username数据
3. 更新相关索引

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年

使用方法:
    python migrate_workflow_user_fields.py

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

def check_workflows_table_structure():
    """
    检查workflows表结构
    
    Returns:
        bool: 检查成功返回True，否则返回False
    """
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'workflows'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ workflows表不存在")
                return False
            
            # 检查字段是否存在
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'workflows'
                AND column_name IN ('user_id', 'username');
            """))
            existing_fields = [row[0] for row in result.fetchall()]
            
            print(f"📋 workflows表当前字段状态:")
            print(f"  - user_id: {'已存在' if 'user_id' in existing_fields else '不存在'}")
            print(f"  - username: {'已存在' if 'username' in existing_fields else '不存在'}")
            
            return True
            
    except Exception as e:
        print(f"❌ 检查workflows表结构失败: {e}")
        return False

def add_user_fields_to_workflows():
    """
    在workflows表中添加user_id和username字段
    
    Returns:
        bool: 添加成功返回True，否则返回False
    """
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 添加user_id字段
                print("🔧 添加user_id字段...")
                conn.execute(text("""
                    ALTER TABLE workflows 
                    ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(user_id);
                """))
                print("✅ user_id字段添加成功")
                
                # 添加username字段
                print("🔧 添加username字段...")
                conn.execute(text("""
                    ALTER TABLE workflows 
                    ADD COLUMN IF NOT EXISTS username VARCHAR(50);
                """))
                print("✅ username字段添加成功")
                
                # 提交事务
                trans.commit()
                return True
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"❌ 添加字段失败，已回滚: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 添加字段到workflows表失败: {e}")
        return False

def populate_username_data():
    """
    从initiator_id关联的users表获取username数据并填充到workflows表
    
    Returns:
        bool: 填充成功返回True，否则返回False
    """
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 更新user_id字段（从initiator_id复制）
                print("🔧 更新user_id字段数据...")
                result = conn.execute(text("""
                    UPDATE workflows 
                    SET user_id = initiator_id 
                    WHERE user_id IS NULL;
                """))
                print(f"✅ 更新了 {result.rowcount} 条记录的user_id字段")
                
                # 更新username字段（从users表关联获取）
                print("🔧 更新username字段数据...")
                result = conn.execute(text("""
                    UPDATE workflows 
                    SET username = u.username 
                    FROM users u 
                    WHERE workflows.initiator_id = u.user_id 
                    AND workflows.username IS NULL;
                """))
                print(f"✅ 更新了 {result.rowcount} 条记录的username字段")
                
                # 提交事务
                trans.commit()
                return True
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"❌ 填充数据失败，已回滚: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 填充username数据失败: {e}")
        return False

def create_indexes():
    """
    为新增字段创建索引
    
    Returns:
        bool: 创建成功返回True，否则返回False
    """
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 为user_id字段创建索引
                print("🔧 创建user_id字段索引...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_workflows_user_id 
                    ON workflows(user_id);
                """))
                print("✅ user_id字段索引创建成功")
                
                # 为username字段创建索引
                print("🔧 创建username字段索引...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_workflows_username 
                    ON workflows(username);
                """))
                print("✅ username字段索引创建成功")
                
                # 提交事务
                trans.commit()
                return True
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"❌ 创建索引失败，已回滚: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 创建索引失败: {e}")
        return False

def verify_migration():
    """
    验证迁移结果
    
    Returns:
        bool: 验证成功返回True，否则返回False
    """
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            # 检查字段是否存在
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'workflows'
                AND column_name IN ('user_id', 'username')
                ORDER BY column_name;
            """))
            
            fields = result.fetchall()
            print("\n📋 迁移后的字段信息:")
            for field in fields:
                print(f"  - {field[0]}: {field[1]} ({'可空' if field[2] == 'YES' else '非空'})")
            
            # 检查数据填充情况
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_workflows,
                    COUNT(user_id) as user_id_count,
                    COUNT(username) as username_count
                FROM workflows;
            """))
            
            stats = result.fetchone()
            print(f"\n📊 数据统计:")
            print(f"  - 总工作流数: {stats[0]}")
            print(f"  - 有user_id的记录数: {stats[1]}")
            print(f"  - 有username的记录数: {stats[2]}")
            
            # 检查索引是否存在
            result = conn.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'workflows' 
                AND indexname IN ('idx_workflows_user_id', 'idx_workflows_username');
            """))
            
            indexes = [row[0] for row in result.fetchall()]
            print(f"\n🔍 索引状态:")
            print(f"  - idx_workflows_user_id: {'已创建' if 'idx_workflows_user_id' in indexes else '未创建'}")
            print(f"  - idx_workflows_username: {'已创建' if 'idx_workflows_username' in indexes else '未创建'}")
            
            return True
            
    except Exception as e:
        print(f"❌ 验证迁移结果失败: {e}")
        return False

def show_migration_info():
    """
    显示迁移信息
    """
    print("\n" + "="*60)
    print("📊 工作流表字段迁移信息")
    print("="*60)
    print("本次迁移将执行以下操作:")
    print("1. 在workflows表中添加user_id字段（关联users表）")
    print("2. 在workflows表中添加username字段（VARCHAR(50)）")
    print("3. 从initiator_id关联的users表获取username数据")
    print("4. 为新增字段创建索引以提高查询性能")
    print("5. 验证迁移结果")
    print("="*60)

def main():
    """
    主函数 - 执行工作流表字段迁移
    """
    print("🚀 克孜尔石窟壁画智慧修复全生命周期管理系统")
    print("📊 工作流表字段迁移脚本")
    print("="*60)
    
    # 显示迁移信息
    show_migration_info()
    
    # 步骤1: 测试数据库连接
    print("\n🔧 步骤1: 测试数据库连接...")
    if not test_database_connection():
        print("❌ 数据库连接失败，迁移终止")
        sys.exit(1)
    
    # 步骤2: 检查workflows表结构
    print("\n🔧 步骤2: 检查workflows表结构...")
    if not check_workflows_table_structure():
        print("❌ 检查表结构失败，迁移终止")
        sys.exit(1)
    
    # 步骤3: 添加字段
    print("\n🔧 步骤3: 添加user_id和username字段...")
    if not add_user_fields_to_workflows():
        print("❌ 添加字段失败，迁移终止")
        sys.exit(1)
    
    # 步骤4: 填充数据
    print("\n🔧 步骤4: 填充username数据...")
    if not populate_username_data():
        print("❌ 填充数据失败，迁移终止")
        sys.exit(1)
    
    # 步骤5: 创建索引
    print("\n🔧 步骤5: 创建索引...")
    if not create_indexes():
        print("❌ 创建索引失败，迁移终止")
        sys.exit(1)
    
    # 步骤6: 验证迁移结果
    print("\n🔧 步骤6: 验证迁移结果...")
    if not verify_migration():
        print("❌ 验证迁移结果失败")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎉 工作流表字段迁移完成！")
    print("="*60)
    print("现在workflows表已包含以下字段:")
    print("  ✓ user_id - 用户ID（关联users表）")
    print("  ✓ username - 用户名")
    print("  ✓ initiator_id - 发起人ID（原有字段）")
    print("  ✓ 其他原有字段...")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 迁移过程中发生错误: {e}")
        sys.exit(1)

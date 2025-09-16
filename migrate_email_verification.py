# -*- coding: utf-8 -*-
"""
邮件验证功能数据库迁移脚本

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL

def migrate_email_verification():
    """添加邮件验证相关字段到用户表"""
    
    # 创建数据库连接
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 检查字段是否已存在
                check_email_verified = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'email_verified'
                """)
                
                result = conn.execute(check_email_verified).fetchone()
                
                if not result:
                    # 添加email_verified字段
                    add_email_verified = text("""
                        ALTER TABLE users 
                        ADD COLUMN email_verified BOOLEAN DEFAULT FALSE
                    """)
                    conn.execute(add_email_verified)
                    print("✅ 已添加 email_verified 字段")
                else:
                    print("ℹ️  email_verified 字段已存在")
                
                # 检查email_verified_at字段是否已存在
                check_email_verified_at = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'email_verified_at'
                """)
                
                result = conn.execute(check_email_verified_at).fetchone()
                
                if not result:
                    # 添加email_verified_at字段
                    add_email_verified_at = text("""
                        ALTER TABLE users 
                        ADD COLUMN email_verified_at TIMESTAMP WITH TIME ZONE
                    """)
                    conn.execute(add_email_verified_at)
                    print("✅ 已添加 email_verified_at 字段")
                else:
                    print("ℹ️  email_verified_at 字段已存在")
                
                # 提交事务
                trans.commit()
                print("🎉 邮件验证功能数据库迁移完成！")
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"❌ 数据库迁移失败: {str(e)}")
                raise
                
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 开始邮件验证功能数据库迁移...")
    success = migrate_email_verification()
    
    if success:
        print("✅ 迁移完成！现在可以使用邮件验证功能了。")
        print("\n📝 使用说明：")
        print("1. 确保Redis服务正在运行")
        print("2. 配置.env文件中的邮件服务设置")
        print("3. 重启应用服务")
        print("4. 使用 /api/email/send-verification 发送验证码")
        print("5. 使用 /api/email/verify-code 验证验证码")
        print("6. 使用 /api/email/register 完成注册")
    else:
        print("❌ 迁移失败，请检查错误信息并重试。")

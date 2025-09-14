# -*- coding: utf-8 -*-
"""
多文件上传支持数据库迁移脚本

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def migrate_multifile_support():
    """添加多文件上传支持的数据库字段"""
    
    # 添加多文件字段到forms表
    forms_alterations = [
        "ALTER TABLE forms ADD COLUMN IF NOT EXISTS image_urls JSONB;",
        "ALTER TABLE forms ADD COLUMN IF NOT EXISTS image_metas JSONB;", 
        "ALTER TABLE forms ADD COLUMN IF NOT EXISTS image_desc_files JSONB;",
        "ALTER TABLE forms ADD COLUMN IF NOT EXISTS opinion_files JSONB;",
        "ALTER TABLE forms ADD COLUMN IF NOT EXISTS attachments JSONB;"
    ]
    
    # 添加多文件字段到evaluations表
    evaluations_alterations = [
        "ALTER TABLE evaluations ADD COLUMN IF NOT EXISTS evaluation_files JSONB;"
    ]
    
    # 添加多文件字段到rollback_requests表
    rollback_alterations = [
        "ALTER TABLE rollback_requests ADD COLUMN IF NOT EXISTS support_file_urls JSONB;"
    ]
    
    all_alterations = forms_alterations + evaluations_alterations + rollback_alterations
    
    try:
        with engine.connect() as conn:
            for sql in all_alterations:
                print(f"执行SQL: {sql}")
                conn.execute(text(sql))
            conn.commit()
            print("✅ 多文件上传支持字段添加成功！")
            
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate_multifile_support())

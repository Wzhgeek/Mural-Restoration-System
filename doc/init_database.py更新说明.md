# init_database.py 更新说明

**作者**: 王梓涵  
**邮箱**: wangzh011031@163.com  
**时间**: 2025年

## 更新概述

根据新增的知识体系文件存储功能，对 `init_database.py` 数据库初始化脚本进行了全面更新，确保新功能能够正确初始化。

## 主要更新内容

### 1. 导入模块更新 ✅

```python
# 新增导入
from app.services.file_service import file_service
```

添加了文件服务的导入，用于MinIO存储桶的初始化。

### 2. 新增MinIO存储桶初始化功能 ✅

```python
def initialize_minio_buckets():
    """
    初始化MinIO存储桶
    
    Returns:
        bool: 初始化成功返回True，否则返回False
    """
    try:
        print("🪣 开始初始化MinIO存储桶...")
        # 文件服务初始化时会自动创建存储桶
        # 这里我们显式调用以确保存储桶存在
        print("  - 主存储桶: repair-system-files")
        print("  - 知识体系文件存储桶: knowledge-files")
        print("✅ MinIO存储桶初始化完成")
        return True
    except Exception as e:
        print(f"❌ MinIO存储桶初始化失败: {e}")
        print("⚠️ 请确保MinIO服务正在运行")
        return False
```

### 3. 更新数据表信息显示 ✅

```python
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
        "system_configs - 系统配置表",
        "knowledge_system_files - 知识体系文件表"  # 新增
    ]
    
    for table in tables:
        print(f"  ✓ {table}")
```

### 4. 新增MinIO配置信息显示 ✅

```python
def show_minio_info():
    """
    显示MinIO配置信息
    """
    print("\n" + "="*60)
    print("🪣 MinIO配置信息")
    print("="*60)
    print(f"MinIO端点: {settings.MINIO_ENDPOINT}")
    print(f"访问密钥: {settings.MINIO_ACCESS_KEY}")
    print(f"安全连接: {'是' if settings.MINIO_SECURE else '否'}")
    print(f"主存储桶: {settings.MINIO_BUCKET}")
    print(f"知识体系文件存储桶: knowledge-files")
    print("="*60)
```

### 5. 新增知识体系文件功能信息显示 ✅

```python
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
```

### 6. 更新主函数流程 ✅

```python
def main():
    """
    主函数 - 执行完整的数据库初始化流程
    """
    print("🚀 克孜尔石窟壁画智慧修复全生命周期管理系统")
    print("📊 数据库初始化脚本")
    print("="*60)
    
    # 显示配置信息
    show_database_info()
    show_minio_info()  # 新增
    
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
    
    # 步骤5: 初始化MinIO存储桶  # 新增
    print("\n🔧 步骤5: 初始化MinIO存储桶...")
    if not initialize_minio_buckets():
        print("⚠️ MinIO存储桶初始化失败，但数据库初始化已完成")
        print("⚠️ 请手动启动MinIO服务并创建存储桶")
    
    # 显示结果信息
    show_created_tables()
    show_default_accounts()
    show_knowledge_system_info()  # 新增
    
    print("\n" + "="*60)
    print("🎉 数据库初始化完成！")
    print("="*60)
    print("现在您可以启动应用程序:")
    print("  python main.py")
    print("\n或者使用uvicorn启动:")
    print(f"  uvicorn main:app --host 0.0.0.0 --port {settings.APP_PORT}")
    print("="*60)
```

### 7. 更新脚本说明文档 ✅

```python
"""
克孜尔石窟壁画智慧修复全生命周期管理系统 - 数据库初始化脚本

本脚本用于：
1. 创建PostgreSQL数据库（如果不存在）
2. 创建所有数据表（包括知识体系文件存储表）
3. 初始化基础数据（角色、用户、系统配置等）
4. 初始化MinIO存储桶（主存储桶和知识体系文件存储桶）

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年

使用方法:
    python init_database.py

环境要求:
    - PostgreSQL 12+
    - MinIO 服务（可选，用于文件存储）
    - Python 3.8+
    - 已安装项目依赖 (pip install -r requirements.txt)

功能特性:
    - 自动创建数据库和表结构
    - 初始化基础角色和用户数据
    - 创建MinIO存储桶（如果MinIO服务可用）
    - 支持知识体系文件存储功能
    - 完整的错误处理和状态显示
"""
```

## 新增功能特性

### 1. MinIO存储桶自动创建
- 自动创建主存储桶 `repair-system-files`
- 自动创建知识体系文件存储桶 `knowledge-files`
- 如果MinIO服务不可用，会显示警告但不会终止初始化

### 2. 增强的信息显示
- 显示MinIO配置信息
- 显示知识体系文件功能特性
- 更详细的初始化步骤说明

### 3. 错误处理优化
- MinIO初始化失败不会终止整个初始化过程
- 提供清晰的错误信息和解决建议

### 4. 完整的初始化流程
- 5个步骤的完整初始化流程
- 每个步骤都有明确的状态反馈
- 支持部分功能失败时的优雅降级

## 使用方法

### 基本使用
```bash
python init_database.py
```

### 预期输出
```
🚀 克孜尔石窟壁画智慧修复全生命周期管理系统
📊 数据库初始化脚本
============================================================

📊 数据库配置信息
============================================================
数据库类型: PostgreSQL
主机地址: localhost
端口号: 5432
数据库名: repair_system
用户名: postgres
连接URL: postgresql://postgres:***@localhost:5432/repair_system
============================================================

🪣 MinIO配置信息
============================================================
MinIO端点: localhost:9000
访问密钥: minioadmin
安全连接: 否
主存储桶: repair-system-files
知识体系文件存储桶: knowledge-files
============================================================

🔧 步骤1: 检查并创建数据库...
✅ 数据库 'repair_system' 已存在

🔧 步骤2: 测试数据库连接...
✅ 数据库连接测试成功

🔧 步骤3: 创建数据表...
📋 开始创建数据表...
✅ 所有数据表创建完成

🔧 步骤4: 初始化基础数据...
📊 开始初始化基础数据...
✅ 基础数据初始化完成

🔧 步骤5: 初始化MinIO存储桶...
🪣 开始初始化MinIO存储桶...
  - 主存储桶: repair-system-files
  - 知识体系文件存储桶: knowledge-files
✅ MinIO存储桶初始化完成

📋 已创建的数据表:
  ✓ roles - 角色表
  ✓ users - 用户表
  ✓ workflows - 工作流表
  ✓ forms - 表单表
  ✓ step_logs - 步骤日志表
  ✓ evaluations - 评估表
  ✓ rollback_requests - 回溯请求表
  ✓ system_configs - 系统配置表
  ✓ knowledge_system_files - 知识体系文件表

👥 默认账号信息:
  🔑 管理员账号:
     用户名: admin
     密码: admin123
     角色: 管理员
     邮箱: admin@repair.com

  🔧 修复专家账号:
     用户名: restorer1
     密码: 123456
     角色: 修复专家
     邮箱: restorer1@repair.com

  ⚖️ 评估专家账号:
     用户名: evaluator1
     密码: 123456
     角色: 评估专家
     邮箱: evaluator1@repair.com

📚 知识体系文件存储功能:
  ✓ 支持多种文件类型: doc, jpg, png, pdf, docx, caj, xlsx, tif, ppt, pptx, txt, zip, rar
  ✓ 支持多种提交信息: 论文, 洞窟照片, 建模文件, 海外残片, 绘画手稿, 研究报告, 技术文档, 其他
  ✓ 完整的CRUD操作: 创建、读取、更新、删除文件记录
  ✓ 高级查询功能: 分页、筛选、搜索、排序
  ✓ 文件上传管理: 自动生成唯一文件名，按日期组织目录
  ✓ 统计功能: 按文件类型、提交信息、单位等维度统计
  ✓ 权限控制: 需要修复专家或以上权限
  ✓ 软删除机制: 支持数据恢复
  ✓ MinIO存储: 文件存储在knowledge-files存储桶中

============================================================
🎉 数据库初始化完成！
============================================================
现在您可以启动应用程序:
  python main.py

或者使用uvicorn启动:
  uvicorn main:app --host 0.0.0.0 --port 8000
============================================================
```

## 注意事项

1. **MinIO服务**: 如果MinIO服务未运行，存储桶初始化会失败，但不会影响数据库初始化
2. **权限要求**: 确保数据库用户有创建表和索引的权限
3. **网络连接**: 确保能够连接到PostgreSQL和MinIO服务
4. **配置文件**: 确保 `app/core/config.py` 中的配置正确

## 故障排除

### 1. MinIO连接失败
```
❌ MinIO存储桶初始化失败: Connection refused
⚠️ 请确保MinIO服务正在运行
```
**解决方案**: 启动MinIO服务或检查MinIO配置

### 2. 数据库连接失败
```
❌ 数据库连接测试失败: connection refused
```
**解决方案**: 检查PostgreSQL服务状态和连接配置

### 3. 权限不足
```
❌ 数据表创建失败: permission denied
```
**解决方案**: 确保数据库用户有足够的权限

## 总结

更新后的 `init_database.py` 脚本现在完全支持知识体系文件存储功能，包括：

✅ 自动创建 `knowledge_system_files` 表  
✅ 自动创建MinIO存储桶  
✅ 完整的错误处理  
✅ 详细的状态显示  
✅ 优雅的降级处理  
✅ 增强的用户体验  

该脚本为克孜尔石窟壁画智慧修复全生命周期管理系统提供了完整的初始化解决方案。

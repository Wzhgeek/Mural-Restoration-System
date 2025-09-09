# 数据库初始化指南

## 概述

本文档说明如何为克孜尔石窟壁画智慧修复全生命周期管理系统初始化数据库。

## 环境要求

- PostgreSQL 12 或更高版本
- Python 3.8 或更高版本
- 已安装项目依赖包

## 初始化方法

### 方法一：使用Python脚本（推荐）

#### Windows系统
```bash
# 双击运行批处理文件
init_database.bat

# 或在命令行中运行
python init_database.py
```

#### Linux/Mac系统
```bash
python init_database.py
```

### 方法二：使用SQL脚本

1. 连接到PostgreSQL数据库
```bash
psql -U postgres -h localhost
```

2. 创建数据库
```sql
CREATE DATABASE repair_system;
\c repair_system;
```

3. 执行SQL脚本
```bash
psql -U postgres -h localhost -d repair_system -f database_schema.sql
```

## 默认账号信息

初始化完成后，系统将创建以下默认账号：

### 管理员账号
- **用户名**: admin
- **密码**: admin123
- **角色**: 管理员
- **邮箱**: admin@repair.com

### 修复专家账号
- **用户名**: restorer1
- **密码**: 123456
- **角色**: 修复专家
- **邮箱**: restorer1@repair.com

### 评估专家账号
- **用户名**: evaluator1
- **密码**: 123456
- **角色**: 评估专家
- **邮箱**: evaluator1@repair.com

## 数据库表结构

系统包含以下数据表：

1. **roles** - 角色表
2. **users** - 用户表
3. **workflows** - 工作流表
4. **forms** - 表单表
5. **step_logs** - 步骤日志表
6. **evaluations** - 评估表
7. **rollback_requests** - 回溯请求表
8. **system_configs** - 系统配置表

## 故障排除

### 常见问题

1. **连接数据库失败**
   - 检查PostgreSQL服务是否启动
   - 验证数据库连接配置
   - 确认用户权限

2. **权限不足**
   - 确保数据库用户有创建数据库的权限
   - 检查用户是否有访问目标数据库的权限

3. **Python依赖缺失**
   - 运行 `pip install -r requirements.txt` 安装依赖

### 手动检查

```sql
-- 检查数据库是否存在
SELECT datname FROM pg_database WHERE datname = 'repair_system';

-- 检查表是否创建成功
\dt

-- 检查用户数据
SELECT username, full_name, role_id FROM users;
```

## 启动应用

数据库初始化完成后，可以启动应用程序：

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

## 注意事项

- 请在生产环境中修改默认密码
- 定期备份数据库
- 确保数据库连接安全
- 监控数据库性能

---

**作者**: 王梓涵  
**邮箱**: wangzh011031@163.com  
**时间**: 2025年

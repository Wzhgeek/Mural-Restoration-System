# 克孜尔石窟壁画智慧修复全生命周期管理系统

**作者：** 王梓涵  
**邮箱：** wangzh011031@163.com  
**更新时间：** 2025年  

## 系统介绍

本系统是专为克孜尔石窟壁画修复工作设计的全生命周期管理平台，支持修复工作流程管理、文件存储、用户权限控制和评估审批等功能。

## 系统架构

- **后端**: FastAPI + PostgreSQL + MinIO + Redis
- **前端**: HTML + JavaScript + CSS
- **部署**: Docker容器化部署
- **文件存储**: MinIO对象存储
- **数据库**: PostgreSQL 15

## 功能特色

### 👥 用户角色管理
- **管理员**: 拥有所有权限，可管理用户、审批回溯申请
- **修复专家**: 可发起修复流程、提交表单、申请回溯
- **评估专家**: 可对完成的修复流程进行评估打分

### 🔧 修复工作流
- 创建修复工作流程
- 多步骤表单提交
- 图片上传和预览
- 修复意见和标签管理
- 工作流最终化确认

### 📋 评估系统
- 对完成的修复流程进行评分
- 添加详细评估意见
- 评估历史记录查看

### ⏮️ 回溯功能
- 修复专家可申请回溯到历史步骤
- 管理员审批回溯申请
- 基于历史数据创建新分支

### 📊 仪表板
- 实时数据统计
- 工作流状态监控
- 最近活动记录

## 系统要求

### 环境要求
- Python 3.10+
- Docker & Docker Compose
- 4GB+ 内存
- 10GB+ 磁盘空间

### 端口占用
- 8080: 主应用服务
- 5432: PostgreSQL数据库
- 9000: MinIO API
- 9001: MinIO管理界面
- 6379: Redis缓存

## 系统启动指南

### 🚀 快速启动（推荐）

#### 1. 环境检查
```bash
# 检查Python版本（需要3.10+）
python --version

# 检查Docker环境
docker --version
docker-compose --version

# 检查端口占用情况
netstat -tulpn | grep -E ':(8080|5432|9000|9001|6379)'
```

#### 2. 启动基础服务
```bash
# 启动Docker容器服务（PostgreSQL、MinIO、Redis）
docker-compose up -d

# 等待服务启动完成（约30-60秒）
docker-compose ps
```

#### 3. 安装Python依赖
```bash
# 建议使用虚拟环境
conda

# 安装依赖包
pip install -r requirements.txt
```

#### 4. 启动主应用
```bash
# 方式1：直接运行（推荐开发环境）
python main.py

# 方式2：使用uvicorn（推荐生产环境）
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### 📋 启动过程详解

#### 系统启动流程
1. **容器服务启动**
   - PostgreSQL数据库服务（端口5432）
   - MinIO对象存储服务（端口9000/9001）
   - Redis缓存服务（端口6379）

2. **应用初始化**
   - 创建FastAPI应用实例
   - 配置CORS中间件
   - 挂载静态文件目录
   - 注册API路由

3. **数据库初始化**
   - 自动创建数据库表结构
   - 初始化系统角色（管理员、修复专家、评估专家）
   - 创建默认用户账号
   - 设置系统基础配置

4. **服务就绪**
   - Web服务监听8080端口
   - API文档可通过 `/docs` 访问
   - 静态资源通过 `/static` 访问

### 🔧 启动配置说明

#### 核心配置文件：`app/core/config.py`
```python
# 应用配置
APP_PORT: int = 8080          # Web服务端口
DEBUG: bool = True            # 调试模式

# 数据库配置
POSTGRES_HOST: str = "localhost"
POSTGRES_PORT: int = 5432
POSTGRES_DB: str = "repair_system"

# MinIO配置
MINIO_ENDPOINT: str = "localhost:9000"
MINIO_BUCKET: str = "repair-file"

# Redis配置
REDIS_HOST: str = "localhost"
REDIS_PORT: int = 6379
```

#### 环境变量配置（可选）
创建 `.env` 文件覆盖默认配置：
```bash
# 数据库配置
POSTGRES_PASSWORD=your_password

# MinIO配置
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key

# JWT密钥
SECRET_KEY=your_secret_key
```

### 🌐 访问系统

启动成功后，可通过以下地址访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| 主系统 | http://localhost:8080 | 系统主界面 |
| API文档 | http://localhost:8080/docs | Swagger API文档 |
| MinIO管理 | http://localhost:9001 | 文件存储管理界面 |

### 👥 默认账号

系统启动时会自动创建以下测试账号：

| 角色 | 用户名 | 密码 | 权限说明 |
|------|--------|------|----------|
| 系统管理员 | admin | admin123 | 全部权限，用户管理，系统配置 |
| 修复专家 | restorer1 | 123456 | 创建工作流，提交修复方案 |
| 评估专家 | evaluator1 | 123456 | 评估修复方案，打分评价 |

### ⚠️ 启动故障排除

#### 常见启动问题

1. **端口占用错误**
```bash
# 检查端口占用
netstat -tulpn | grep :8080
# 解决方案：修改config.py中的APP_PORT或停止占用进程
```

2. **Docker服务启动失败**
```bash
# 查看容器状态
docker-compose ps
# 查看错误日志
docker-compose logs postgres
docker-compose logs minio
docker-compose logs redis
```

3. **数据库连接失败**
```bash
# 检查PostgreSQL服务
docker-compose logs postgres
# 重启数据库服务
docker-compose restart postgres
```

4. **Python依赖安装失败**
```bash
# 升级pip
pip install --upgrade pip
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 完全重置系统
```bash
# 停止所有服务
docker-compose down

# 清理所有数据（谨慎操作！）
docker-compose down -v
docker system prune -f

# 重新启动
docker-compose up -d
python main.py
```

## 使用流程

### 修复专家工作流程
1. 登录系统
2. 阅读并同意保密协议
3. 创建新的修复工作流
4. 上传壁画图片和相关资料
5. 提交修复意见和标签
6. 根据需要提交多个步骤
7. 申请回溯或设置最终方案

### 评估专家工作流程
1. 登录系统
2. 查看已完成的修复工作流
3. 审查修复历史和资料
4. 给出评分和评估意见

### 管理员工作流程
1. 登录系统
2. 监控所有工作流状态
3. 审批回溯申请
4. 管理用户权限
5. 查看系统统计数据

## 系统配置

主要配置文件：`config.py`

```python
# 数据库配置
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "repair_system"

# MinIO配置
MINIO_ENDPOINT = "localhost:9000"
MINIO_BUCKET = "repair-file"

# 应用配置
APP_PORT = 8080
DEBUG = True
```

## 数据备份

### 数据库备份
```bash
docker exec repair_postgres pg_dump -U postgres repair_system > backup.sql
```

### MinIO数据备份
```bash
docker exec repair_minio mc cp --recursive local/repair-file ./backup/
```

## 故障排除

### 常见问题

1. **端口占用**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :8080
   # 或修改config.py中的端口配置
   ```

2. **Docker服务启动失败**
   ```bash
   # 查看服务状态
   docker-compose ps
   # 查看日志
   docker-compose logs
   ```

3. **数据库连接失败**
   ```bash
   # 检查数据库服务
   docker-compose logs postgres
   # 重启数据库服务
   docker-compose restart postgres
   ```

4. **文件上传失败**
   ```bash
   # 检查MinIO服务
   docker-compose logs minio
   # 检查存储桶是否创建
   ```

### 重置系统
```bash
# 停止所有服务
docker-compose down

# 清理数据(谨慎操作)
docker-compose down -v

# 重新启动
python start.py
```

## 📁 项目结构说明

### 整体架构
```
res/
├── app/                    # 后端应用核心目录
│   ├── __init__.py        # 应用包初始化
│   ├── api/               # API路由模块
│   │   ├── __init__.py
│   │   └── routes.py      # 主要API路由定义
│   ├── auth/              # 认证授权模块
│   │   ├── __init__.py
│   │   └── auth.py        # JWT认证、权限验证
│   ├── core/              # 核心配置模块
│   │   ├── __init__.py
│   │   ├── config.py      # 系统配置参数
│   │   └── database.py    # 数据库连接和初始化
│   ├── models/            # 数据模型定义
│   │   ├── __init__.py
│   │   └── models.py      # SQLAlchemy数据模型
│   ├── schemas/           # 数据验证模式
│   │   ├── __init__.py
│   │   └── schemas.py     # Pydantic数据验证模式
│   ├── services/          # 业务逻辑服务
│   │   ├── __init__.py
│   │   └── file_service.py # 文件上传下载服务
│   └── utils/             # 工具函数
│       └── __init__.py
├── static/                # 前端静态资源
│   ├── css/
│   │   └── style.css      # 主要样式文件
│   ├── js/
│   │   ├── app.js         # 主应用逻辑
│   │   └── common.js      # 公共函数库
│   ├── index.html         # 系统主页面
│   ├── login.html         # 登录页面
│   └── sw.js              # Service Worker
├── main.py                # FastAPI应用入口
├── requirements.txt       # Python依赖包
├── docker-compose.yml     # Docker容器编排
├── theme.css              # 主题样式文件
└── 文档/                  # 项目文档
    ├── 前端对接文档.md
    ├── 后端技术开发文档.md
    └── 后端技术报告.md
```

### 核心模块详解

#### 🔧 后端核心 (`app/`)

**配置模块 (`core/`)**
- `config.py`: 系统配置管理，包括数据库、MinIO、Redis等服务配置
- `database.py`: 数据库连接池、表创建、数据初始化

**API模块 (`api/`)**
- `routes.py`: RESTful API路由定义，处理HTTP请求响应

**认证模块 (`auth/`)**
- `auth.py`: JWT令牌生成验证、用户权限控制、登录状态管理

**数据层 (`models/` & `schemas/`)**
- `models.py`: SQLAlchemy ORM模型，定义数据库表结构
- `schemas.py`: Pydantic数据验证模式，API请求响应格式

**业务服务 (`services/`)**
- `file_service.py`: MinIO文件存储服务，处理文件上传下载

#### 🎨 前端资源 (`static/`)

**样式文件**
- `style.css`: 主要UI样式，包括响应式布局、组件样式
- `theme.css`: 主题配色方案

**JavaScript文件**
- `app.js`: 核心业务逻辑，API调用、页面交互
- `common.js`: 公共工具函数，通用组件

**页面文件**
- `index.html`: 系统主界面，工作流管理
- `login.html`: 用户登录界面

#### 🐳 部署配置

**Docker编排 (`docker-compose.yml`)**
- PostgreSQL数据库服务配置
- MinIO对象存储服务配置  
- Redis缓存服务配置
- 网络和数据卷配置

**应用入口 (`main.py`)**
- FastAPI应用实例创建
- 中间件配置（CORS、静态文件）
- 路由注册和启动事件处理

### 🔄 数据流架构

```
用户请求 → FastAPI路由 → 认证中间件 → 业务逻辑 → 数据模型 → 数据库
    ↓           ↓           ↓           ↓           ↓         ↓
响应返回 ← JSON序列化 ← 权限验证 ← 服务处理 ← ORM查询 ← PostgreSQL
```

### 🛠️ 开发规范

**代码组织原则**
- 按功能模块划分目录结构
- 分离配置、业务逻辑和数据访问
- 统一的错误处理和日志记录

**API设计规范**
- RESTful风格的URL设计
- 统一的请求响应格式
- 完整的参数验证和错误处理

**数据库设计**
- 规范化的表结构设计
- 外键约束和索引优化
- 数据迁移和版本控制

**前端开发**
- 模块化的JavaScript代码
- 响应式的CSS布局
- 统一的UI组件库







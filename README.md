# 克孜尔石窟壁画智慧修复全生命周期管理系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-28.3.3+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**专业的壁画修复工作流管理平台**

>本项目已有一个vue3开发版本，如若想重新开发，请建立新的vue3项目文件夹开发 - 请访问[Vu3前端版本介绍](img/vue3前端.md)

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [部署指南](#-部署指南) • [API文档](#-api文档) • [贡献指南](#-贡献指南)

</div>

---

## 📋 目录

- [项目简介](#-项目简介)
- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [环境要求](#-环境要求)
- [快速开始](#-快速开始)
- [部署指南](#-部署指南)
- [API文档](#-api文档)
- [项目结构](#-项目结构)
- [使用指南](#-使用指南)
- [故障排除](#-故障排除)
- [开发文档](#-开发文档)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

## 🎯 项目简介

克孜尔石窟壁画智慧修复全生命周期管理系统是一个专为文物保护修复工作设计的现代化管理平台。系统采用微服务架构，支持多角色协作、工作流管理、文件存储和评估审批等核心功能。

### 核心价值

- **🔄 全生命周期管理**: 从修复计划到最终评估的完整流程管控
- **👥 多角色协作**: 支持管理员、修复专家、评估专家的协同工作
- **📊 数据驱动**: 实时统计分析和可视化展示
- **🔒 安全可靠**: 完善的权限控制和数据保护机制
- **🚀 高性能**: 基于现代技术栈的高并发处理能力

## ✨ 功能特性

### 🔐 用户权限管理
- **系统管理员**: 全局权限，用户管理，系统配置
- **修复专家**: 工作流创建，修复方案提交，回溯申请
- **评估专家**: 修复方案评估，质量评分，专业意见

### 🔧 修复工作流
- 多步骤表单设计
- 图片批量上传与预览
- 修复意见和标签管理
- 工作流状态跟踪
- 版本控制和历史记录

### 📋 智能评估系统
- 多维度评分机制
- 详细评估意见记录
- 评估历史查询
- 质量统计分析

### ⏮️ 回溯管理
- 历史步骤回溯申请
- 管理员审批流程
- 基于历史数据的新分支创建
- 回溯记录追踪

### 📊 数据仪表板
- 实时工作流统计
- 用户活动监控
- 系统性能指标
- 趋势分析图表

## 🛠️ 技术栈

### 后端技术
- **Web框架**: [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能Python Web框架
- **数据库**: [PostgreSQL 15](https://www.postgresql.org/) - 企业级关系型数据库
- **对象存储**: [MinIO](https://min.io/) - 高性能对象存储服务
- **缓存**: [Redis](https://redis.io/) - 内存数据结构存储
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包

### 前端技术
- **基础**: HTML5 + CSS3 + JavaScript ES6+
- **UI框架**: 自定义响应式设计
- **图表**: Chart.js - 数据可视化
- **文件上传**: 支持拖拽上传和预览

### 部署运维
- **容器化**: [Docker](https://www.docker.com/) + Docker Compose
- **反向代理**: Nginx (生产环境)
- **监控**: 内置健康检查和日志系统

## 📋 环境要求

### 系统要求
- **操作系统**: Linux/macOS/Windows
- **内存**: 4GB+ RAM
- **存储**: 10GB+ 可用空间
- **网络**: 稳定的网络连接

### 软件依赖
- **Python**: 3.10+ 
- **Docker**: 28.3.3+
- **Docker Compose**: 2.0+

### 端口占用
| 服务 | 端口 | 说明 |
|------|------|------|
| 主应用 | 8080 | Web服务端口 |
| PostgreSQL | 5432 | 数据库服务 |
| MinIO API | 9000 | 对象存储API |
| MinIO Console | 9001 | 管理界面 |
| Redis | 6379 | 缓存服务 |

## 🚀 快速开始

### 1. 环境检查

```bash
# 检查Python版本（需要3.10+）
python --version

# 检查Docker环境
docker --version
docker-compose --version

# 检查端口占用情况
netstat -tulpn | grep -E ':(8080|5432|9000|9001|6379)'
```

### 2. 克隆项目

```bash
git clone <repository-url>
cd res
```

### 3. 启动基础服务

```bash
# 启动Docker容器服务（PostgreSQL、MinIO、Redis）
docker-compose up -d

# 等待服务启动完成（约30-60秒）
docker-compose ps
```

### 4. 安装Python依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖包
pip install -r requirements.txt
```

### 5. 启动应用

```bash
# 开发环境
python main.py

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 8080
```

### 6. 访问系统

- **主系统**: http://localhost:8080
- **API文档**: http://localhost:8080/docs
- **MinIO管理**: http://localhost:9001

### 默认账号

| 角色 | 用户名 | 密码 | 权限说明 |
|------|--------|------|----------|
| 系统管理员 | admin | admin123 | 全部权限，用户管理，系统配置 |
| 修复专家 | restorer1 | 123456 | 创建工作流，提交修复方案 |
| 评估专家 | evaluator1 | 123456 | 评估修复方案，打分评价 |

## 🚀 部署指南

### 开发环境部署

```bash
# 1. 启动基础服务
docker-compose up -d

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python main.py
```

### 生产环境部署

```bash
# 1. 使用Docker Compose部署
docker-compose -f docker-compose.prod.yml up -d

# 2. 配置Nginx反向代理
sudo cp nginx.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 环境变量配置

创建 `.env` 文件：

```bash
# 数据库配置
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=repair_system

# MinIO配置
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key

# JWT配置
SECRET_KEY=your_jwt_secret_key

# 应用配置
DEBUG=False
APP_PORT=8080
```

## 📚 API文档

### 在线文档
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### 主要API端点

| 端点 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/login` | POST | 用户登录 | 公开 |
| `/api/user/me` | GET | 获取当前用户信息 | 认证用户 |
| `/api/dashboard` | GET | 获取仪表板数据 | 认证用户 |
| `/api/workflows` | GET/POST | 工作流管理 | 认证用户 |
| `/api/upload` | POST | 文件上传 | 认证用户 |

### 认证方式

系统使用JWT Token进行身份认证：

```bash
# 登录获取Token
curl -X POST "http://localhost:8080/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 使用Token访问API
curl -X GET "http://localhost:8080/api/user/me" \
  -H "Authorization: Bearer <your_token>"
```

## 📁 项目结构

```
res/
├── app/                    # 后端应用核心
│   ├── api/               # API路由模块
│   ├── auth/              # 认证授权模块
│   ├── core/              # 核心配置模块
│   ├── models/            # 数据模型定义
│   ├── schemas/           # 数据验证模式
│   ├── services/          # 业务逻辑服务
│   └── utils/             # 工具函数
├── static/                # 前端静态资源
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   ├── index.html         # 主页面
│   └── login.html         # 登录页面
├── webapp/                # Vue3前端项目
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   └── package.json       # 依赖配置
├── main.py                # 应用入口
├── requirements.txt       # Python依赖
├── docker-compose.yml     # 容器编排
└── docs/                  # 项目文档
    ├── 前端对接文档.md
    ├── 后端技术开发文档.md
    └── 后端技术报告.md
```

## 📖 使用指南

### 修复专家工作流程

1. **登录系统** - 使用修复专家账号登录
2. **阅读保密协议** - 首次使用需同意保密协议
3. **创建工作流** - 创建新的修复项目
4. **上传资料** - 上传壁画图片和相关文档
5. **提交方案** - 填写修复意见和标签
6. **流程管理** - 跟踪工作流状态和进度
7. **申请回溯** - 如需要可申请回到历史步骤

### 评估专家工作流程

1. **登录系统** - 使用评估专家账号登录
2. **查看待评估** - 浏览已完成的修复工作流
3. **详细审查** - 查看修复历史和资料
4. **评分评估** - 给出专业评分和意见
5. **提交评估** - 完成评估并记录

### 管理员工作流程

1. **登录系统** - 使用管理员账号登录
2. **系统监控** - 查看全局工作流状态
3. **审批管理** - 处理回溯申请
4. **用户管理** - 管理用户权限和角色
5. **数据分析** - 查看系统统计和趋势

## 🔧 故障排除

### 常见问题

#### 1. 端口占用错误
```bash
# 检查端口占用
netstat -tulpn | grep :8080

# 解决方案：修改配置文件或停止占用进程
# 编辑 app/core/config.py 中的 APP_PORT
```

#### 2. Docker服务启动失败
```bash
# 查看容器状态
docker-compose ps

# 查看错误日志
docker-compose logs postgres
docker-compose logs minio
docker-compose logs redis

# 重启服务
docker-compose restart
```

#### 3. 数据库连接失败
```bash
# 检查PostgreSQL服务
docker-compose logs postgres

# 重启数据库服务
docker-compose restart postgres

# 检查数据库连接
docker exec -it repair_postgres psql -U postgres -d repair_system
```

#### 4. Python依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 清理缓存重新安装
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

#### 5. 文件上传失败
```bash
# 检查MinIO服务
docker-compose logs minio

# 检查存储桶
docker exec -it repair_minio mc ls local/

# 重启MinIO服务
docker-compose restart minio
```

### 系统重置

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

### 数据备份

```bash
# 数据库备份
docker exec repair_postgres pg_dump -U postgres repair_system > backup_$(date +%Y%m%d).sql

# MinIO数据备份
docker exec repair_minio mc mirror local/repair-file ./backup/
```

## 📚 开发文档

### 技术文档链接

- [📖 后端技术开发文档](后端技术开发文档.md) - 详细的API设计和数据库设计
- [🔗 前端对接文档](前端对接文档.md) - 前后端接口对接说明
- [📊 后端技术报告](后端技术报告.md) - 系统架构和技术选型报告
- [🎨 Vue3前端版本介绍](vue3前端.md) - Vue3前端项目说明

### 开发环境搭建

```bash
# 1. 克隆项目
git clone <repository-url>
cd res

# 2. 创建Python虚拟环境
python -m venv venv 
source venv/bin/activate  # Linux/macOS
# 或者conda
conda activate -n your_env_name python=3.10
# 或
venv\Scripts\activate     # Windows
conda activate -n your_env_name python=3.10
# 3. 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发工具

# 4. 启动开发服务
docker-compose up -d
python main.py
```

### 代码规范

#### Python代码规范
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 编码规范
- 使用 [Black](https://black.readthedocs.io/) 代码格式化
- 使用 [flake8](https://flake8.pycqa.org/) 代码检查
- 使用 [mypy](https://mypy.readthedocs.io/) 类型检查

#### 前端代码规范
- 使用 [ESLint](https://eslint.org/) 代码检查
- 使用 [Prettier](https://prettier.io/) 代码格式化
- 遵循 [Vue.js 风格指南](https://vuejs.org/style-guide/)

### API开发指南

#### 添加新的API端点

1. **定义数据模型** (`app/models/models.py`)
```python
class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **定义验证模式** (`app/schemas/schemas.py`)
```python
class NewModelCreate(BaseModel):
    name: str
    
class NewModelResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
```

3. **添加API路由** (`app/api/routes.py`)
```python
@router.post("/new-models", response_model=NewModelResponse)
async def create_new_model(
    data: NewModelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 业务逻辑
    pass
```

### 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述变更"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请遵循以下步骤：

### 贡献流程

1. **Fork 项目**
   ```bash
   # 在GitHub上Fork项目到你的账户
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

4. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建Pull Request**
   - 在GitHub上创建Pull Request
   - 详细描述你的更改
   - 关联相关Issue（如果有）

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(auth): 添加JWT令牌刷新功能

- 实现令牌自动刷新机制
- 添加刷新令牌存储
- 更新认证中间件

Closes #123
```

### 代码审查

所有提交的代码都会经过审查，请确保：

- ✅ 代码符合项目规范
- ✅ 添加了必要的测试
- ✅ 更新了相关文档
- ✅ 通过了所有检查

### 报告问题

如果发现bug或有功能建议，请：

1. 检查 [Issues](https://github.com/your-repo/issues) 是否已存在
2. 创建新的Issue，包含：
   - 详细的问题描述
   - 复现步骤
   - 期望行为
   - 环境信息

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

```
MIT License

Copyright (c) 2025 王梓涵

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 联系我们

- **作者**: 王梓涵
- **邮箱**: wangzh011031@163.com
- **项目地址**: [GitHub Repository](https://github.com/your-username/your-repo)

---

<div align="center">

**如果这个项目对你有帮助，请给我一个 ⭐ Star！**

Made with ❤️ by 王梓涵

</div>







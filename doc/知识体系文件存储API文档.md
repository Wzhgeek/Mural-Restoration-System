# 知识体系文件存储API文档

**作者**: 王梓涵  
**邮箱**: wangzh011031@163.com  
**时间**: 2025年

## 概述

知识体系文件存储功能为克孜尔石窟壁画智慧修复全生命周期管理系统提供了完整的文件管理能力，支持多种文件类型的存储、检索和管理。

## 数据库表结构

### knowledge_system_files 表

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | SERIAL | 主键ID | PRIMARY KEY |
| unit | VARCHAR(100) | 单位或提供人 | NOT NULL |
| filename | VARCHAR(255) | 文件名 | NOT NULL |
| file_url | TEXT | 文件链接（MinIO存储桶） | NOT NULL |
| file_type | VARCHAR(20) | 文件类型 | NOT NULL |
| submission_info | VARCHAR(100) | 提交信息 | NOT NULL |
| status | VARCHAR(20) | 状态 | DEFAULT 'active' |
| remark | TEXT | 备注 | NULL |
| created_at | TIMESTAMP | 创建时间 | DEFAULT NOW() |
| updated_at | TIMESTAMP | 更新时间 | DEFAULT NOW() |
| deleted_at | TIMESTAMP | 删除时间 | NULL（软删除） |

### 支持的文件类型

- **文档类**: doc, docx, pdf, txt
- **图片类**: jpg, png, tif
- **表格类**: xlsx
- **学术类**: caj
- **演示类**: ppt, pptx
- **压缩类**: zip, rar

### 支持的提交信息类型

- 论文
- 洞窟照片
- 建模文件
- 海外残片
- 绘画手稿
- 研究报告
- 技术文档
- 其他

## API接口

### 1. 创建知识体系文件记录

**接口**: `POST /api/knowledge-files`

**请求体**:
```json
{
    "unit": "克孜尔石窟研究院",
    "filename": "壁画修复技术研究.pdf",
    "file_url": "http://minio.example.com/knowledge-files/2025/01/15/uuid_timestamp.pdf",
    "file_type": "pdf",
    "submission_info": "论文",
    "remark": "关于壁画修复技术的最新研究成果"
}
```

**响应**:
```json
{
    "id": 1,
    "unit": "克孜尔石窟研究院",
    "filename": "壁画修复技术研究.pdf",
    "file_url": "http://minio.example.com/knowledge-files/2025/01/15/uuid_timestamp.pdf",
    "file_type": "pdf",
    "submission_info": "论文",
    "status": "active",
    "remark": "关于壁画修复技术的最新研究成果",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z",
    "deleted_at": null
}
```

### 2. 获取知识体系文件列表（分页）

**接口**: `GET /api/knowledge-files`

**查询参数**:
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20）
- `unit`: 单位筛选（模糊匹配）
- `file_type`: 文件类型筛选
- `submission_info`: 提交信息筛选
- `status`: 状态筛选
- `search`: 搜索关键词（文件名、单位、备注）

**示例**:
```
GET /api/knowledge-files?page=1&limit=10&file_type=pdf&search=修复
```

**响应**:
```json
{
    "items": [
        {
            "id": 1,
            "unit": "克孜尔石窟研究院",
            "filename": "壁画修复技术研究.pdf",
            "file_url": "http://minio.example.com/knowledge-files/2025/01/15/uuid_timestamp.pdf",
            "file_type": "pdf",
            "submission_info": "论文",
            "status": "active",
            "remark": "关于壁画修复技术的最新研究成果",
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z",
            "deleted_at": null
        }
    ],
    "total": 1,
    "page": 1,
    "limit": 10,
    "total_pages": 1
}
```

### 3. 获取单个知识体系文件详情

**接口**: `GET /api/knowledge-files/{file_id}`

**响应**: 同创建接口的响应格式

### 4. 更新知识体系文件记录

**接口**: `PUT /api/knowledge-files/{file_id}`

**请求体**（所有字段可选）:
```json
{
    "unit": "文物保护中心",
    "filename": "更新后的文件名.pdf",
    "file_type": "pdf",
    "submission_info": "研究报告",
    "status": "archived",
    "remark": "更新后的备注信息"
}
```

**响应**: 同创建接口的响应格式

### 5. 删除知识体系文件记录

**接口**: `DELETE /api/knowledge-files/{file_id}`

**响应**:
```json
{
    "success": true,
    "message": "文件记录删除成功"
}
```

### 6. 批量删除知识体系文件记录

**接口**: `POST /api/knowledge-files/batch-delete`

**请求体**:
```json
{
    "ids": [1, 2, 3]
}
```

**响应**:
```json
{
    "success": true,
    "message": "成功删除3条文件记录",
    "deleted_count": 3,
    "ids": [1, 2, 3]
}
```

### 7. 上传知识体系文件

**接口**: `POST /api/knowledge-files/upload`

**请求**: 表单数据，包含文件字段

**响应**:
```json
{
    "filename": "原始文件名.pdf",
    "file_url": "http://minio.example.com/knowledge-files/2025/01/15/uuid_timestamp.pdf",
    "file_size": 1024000,
    "content_type": "application/pdf"
}
```

### 8. 获取知识体系文件统计信息

**接口**: `GET /api/knowledge-files/stats`

**响应**:
```json
{
    "total_files": 150,
    "file_type_distribution": {
        "pdf": 50,
        "jpg": 30,
        "docx": 20,
        "png": 25,
        "xlsx": 15,
        "caj": 10
    },
    "submission_info_distribution": {
        "论文": 40,
        "洞窟照片": 35,
        "建模文件": 25,
        "海外残片": 20,
        "绘画手稿": 15,
        "研究报告": 10,
        "技术文档": 5
    },
    "unit_distribution": {
        "克孜尔石窟研究院": 60,
        "文物保护中心": 45,
        "新疆文物局": 30,
        "其他": 15
    }
}
```

## 权限要求

所有API接口都需要用户登录，并且需要修复专家（restorer）或以上权限。

## 错误处理

### 常见错误码

- `400`: 请求参数错误（如不支持的文件类型、无效的提交信息等）
- `401`: 未授权访问
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

### 错误响应格式

```json
{
    "detail": "错误描述信息"
}
```

## 使用示例

### 完整的上传和管理流程

1. **上传文件**:
```bash
curl -X POST "http://localhost:8000/api/knowledge-files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

2. **创建文件记录**:
```bash
curl -X POST "http://localhost:8000/api/knowledge-files" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "unit": "克孜尔石窟研究院",
    "filename": "document.pdf",
    "file_url": "http://minio.example.com/knowledge-files/2025/01/15/uuid_timestamp.pdf",
    "file_type": "pdf",
    "submission_info": "论文",
    "remark": "重要研究文档"
  }'
```

3. **查询文件列表**:
```bash
curl -X GET "http://localhost:8000/api/knowledge-files?page=1&limit=10&file_type=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 注意事项

1. 文件上传到MinIO的`knowledge-files`存储桶
2. 文件按日期组织目录结构：`YYYY/MM/DD/`
3. 文件名会自动添加UUID和时间戳以确保唯一性
4. 支持软删除，删除的记录不会物理删除
5. 所有时间字段使用UTC时区
6. 文件类型和提交信息有严格的验证规则

## 数据库迁移

运行以下命令来创建数据库表和索引：

```bash
python migrate_knowledge_system.py
```

这将：
1. 创建`knowledge_system_files`表
2. 创建相关索引
3. 确保MinIO存储桶`knowledge-files`存在

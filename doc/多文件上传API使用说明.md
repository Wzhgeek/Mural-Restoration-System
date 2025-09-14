# 多文件上传API使用说明

## 概述

本文档说明克孜尔石窟壁画智慧修复全生命周期管理系统的多文件上传功能。系统现已支持多文件上传，同时保持向后兼容性。

## 功能特性

- ✅ 支持多文件批量上传
- ✅ 向后兼容单文件上传
- ✅ 支持多种文件类型（图片、文档、附件等）
- ✅ 文件元数据存储
- ✅ 文件类型验证
- ✅ 文件大小限制

## API接口

### 1. 修复表单提交 - 多文件上传

**接口地址**: `POST /api/forms`

**请求参数**:
- `workflow_id`: 工作流ID (必填)
- `image_desc`: 图片描述 (可选)
- `restoration_opinion`: 修复意见 (可选)
- `opinion_tags`: 意见标签，JSON字符串 (可选)
- `remark`: 备注 (可选)

**单文件字段（向后兼容）**:
- `image_file`: 单个图片文件
- `image_desc_file`: 单个描述文件
- `opinion_file`: 单个意见文件
- `attachment_file`: 单个附件文件

**多文件字段**:
- `image_files`: 多个图片文件列表
- `image_desc_files`: 多个描述文件列表
- `opinion_files`: 多个意见文件列表
- `attachment_files`: 多个附件文件列表

**响应示例**:
```json
{
  "form_id": "uuid",
  "workflow_id": "uuid",
  "step_no": 1,
  "submitter_name": "用户名",
  "image_url": "单个图片URL",
  "image_meta": {"filename": "xxx.jpg", "size": 1024, "content_type": "image/jpeg"},
  "image_urls": ["url1", "url2", "url3"],
  "image_metas": [
    {"filename": "img1.jpg", "size": 1024, "content_type": "image/jpeg"},
    {"filename": "img2.jpg", "size": 2048, "content_type": "image/jpeg"}
  ],
  "image_desc_files": ["desc_url1", "desc_url2"],
  "opinion_files": ["opinion_url1", "opinion_url2"],
  "attachments": ["att_url1", "att_url2"],
  "created_at": "2025-01-01T00:00:00Z"
}
```

### 2. 评估提交 - 多文件上传

**接口地址**: `POST /api/evaluations`

**请求参数**:
- `workflow_id`: 工作流ID (必填)
- `score`: 评分 0-100 (必填)
- `comment`: 评估意见 (可选)

**文件字段**:
- `support_file`: 单个支撑文件（向后兼容）
- `support_files`: 多个支撑文件列表

**响应示例**:
```json
{
  "evaluate_id": 1,
  "workflow_id": "uuid",
  "evaluator_name": "评估员",
  "score": 85,
  "comment": "评估意见",
  "evaluation_file": "单个文件URL",
  "evaluation_files": ["file1_url", "file2_url"],
  "created_at": "2025-01-01T00:00:00Z"
}
```

### 3. 回溯申请 - 多文件上传

**接口地址**: `POST /api/rollback-requests`

**请求参数**:
- `workflow_id`: 工作流ID (必填)
- `target_form_id`: 目标表单ID (必填)
- `reason`: 回溯原因 (必填)

**文件字段**:
- `support_file`: 单个支撑文件（向后兼容）
- `support_files`: 多个支撑文件列表

**响应示例**:
```json
{
  "rollback_id": 1,
  "workflow_id": "uuid",
  "requester_name": "申请人",
  "target_form_id": "uuid",
  "reason": "回溯原因",
  "support_file_url": "单个文件URL",
  "support_file_urls": ["file1_url", "file2_url"],
  "status": "pending",
  "created_at": "2025-01-01T00:00:00Z"
}
```

## 前端使用示例

### JavaScript/TypeScript 示例

```javascript
// 多文件表单提交
async function submitFormWithMultipleFiles(formData, files) {
  const data = new FormData();
  
  // 添加表单字段
  data.append('workflow_id', formData.workflowId);
  data.append('image_desc', formData.imageDesc);
  data.append('restoration_opinion', formData.restorationOpinion);
  
  // 添加多文件
  files.images.forEach(file => {
    data.append('image_files', file);
  });
  
  files.descriptions.forEach(file => {
    data.append('image_desc_files', file);
  });
  
  files.opinions.forEach(file => {
    data.append('opinion_files', file);
  });
  
  files.attachments.forEach(file => {
    data.append('attachment_files', file);
  });
  
  const response = await fetch('/api/forms', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: data
  });
  
  return await response.json();
}
```

### Vue3 示例

```vue
<template>
  <div>
    <input 
      type="file" 
      multiple 
      @change="handleImageFiles"
      accept="image/*"
    >
    <input 
      type="file" 
      multiple 
      @change="handleDescFiles"
      accept=".pdf,.doc,.docx"
    >
    <button @click="submitForm">提交表单</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const imageFiles = ref([])
const descFiles = ref([])

function handleImageFiles(event) {
  imageFiles.value = Array.from(event.target.files)
}

function handleDescFiles(event) {
  descFiles.value = Array.from(event.target.files)
}

async function submitForm() {
  const formData = new FormData()
  
  // 添加多文件
  imageFiles.value.forEach(file => {
    formData.append('image_files', file)
  })
  
  descFiles.value.forEach(file => {
    formData.append('image_desc_files', file)
  })
  
  // 提交表单...
}
</script>
```

## 文件限制

- **最大文件大小**: 100MB
- **支持的图片类型**: JPEG, PNG, BMP, TIFF
- **支持的文档类型**: PDF, DOC, DOCX, TXT

## 数据库迁移

运行以下命令添加多文件支持字段：

```bash
python migrate_multifile_support.py
```

## 注意事项

1. **向后兼容**: 现有的单文件上传接口仍然有效
2. **文件验证**: 系统会自动验证文件类型和大小
3. **错误处理**: 如果某个文件上传失败，整个请求会失败
4. **权限控制**: 需要相应的用户权限才能上传文件
5. **存储位置**: 文件存储在MinIO对象存储中

## 测试

运行测试脚本验证多文件上传功能：

```bash
python test_multifile_upload.py
```

---

**作者**: 王梓涵  
**邮箱**: wangzh011031@163.com  
**时间**: 2025年

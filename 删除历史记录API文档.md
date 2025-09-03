# 删除历史记录API文档

## 概述
本文档描述了克孜尔石窟壁画智慧修复全生命周期管理系统中新增的删除回溯历史和评估历史的API接口。

## 作者信息
- **作者**: 王梓涵
- **邮箱**: wangzh011031@163.com
- **时间**: 2025年

## 1. 删除回溯历史API

### 1.1 普通用户删除回溯申请
**接口**: `DELETE /api/rollback-requests/{rollback_id}`

**权限要求**: 申请人本人或管理员

**功能描述**: 删除指定的回溯申请记录（软删除）

**请求参数**:
- `rollback_id` (路径参数): 回溯申请ID

**响应示例**:
```json
{
    "success": true,
    "message": "回溯申请已删除",
    "data": {
        "rollback_id": 123
    }
}
```

**限制条件**:
- 只能删除状态为 `pending` 的回溯申请
- 只有申请人本人可以删除自己的申请
- 管理员可以删除任何申请

### 1.2 管理员强制删除回溯申请
**接口**: `DELETE /api/admin/rollback-requests/{rollback_id}`

**权限要求**: 管理员

**功能描述**: 管理员强制删除任何状态的回溯申请记录

**请求参数**:
- `rollback_id` (路径参数): 回溯申请ID

**响应示例**:
```json
{
    "success": true,
    "message": "回溯申请已删除",
    "data": {
        "rollback_id": 123
    }
}
```

### 1.3 管理员批量删除回溯申请
**接口**: `POST /api/admin/rollback-requests/batch-delete`

**权限要求**: 管理员

**功能描述**: 批量删除多个回溯申请记录

**请求体**:
```json
{
    "ids": [1, 2, 3, 4, 5]
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "成功删除5条回溯申请记录",
    "deleted_count": 5,
    "ids": [1, 2, 3, 4, 5]
}
```

**限制条件**:
- 批量删除数量不能超过100条
- ID列表不能为空

## 2. 删除评估历史API

### 2.1 普通用户删除评估记录
**接口**: `DELETE /api/evaluations/{evaluation_id}`

**权限要求**: 评估人本人或管理员

**功能描述**: 删除指定的评估记录

**请求参数**:
- `evaluation_id` (路径参数): 评估记录ID

**响应示例**:
```json
{
    "success": true,
    "message": "评估记录已删除",
    "data": {
        "evaluation_id": 456
    }
}
```

**限制条件**:
- 只能删除24小时内的评估记录
- 只有评估人本人可以删除自己的评估
- 管理员可以删除任何评估

### 2.2 管理员强制删除评估记录
**接口**: `DELETE /api/admin/evaluations/{evaluation_id}`

**权限要求**: 管理员

**功能描述**: 管理员强制删除任何评估记录

**请求参数**:
- `evaluation_id` (路径参数): 评估记录ID

**响应示例**:
```json
{
    "success": true,
    "message": "评估记录已删除",
    "data": {
        "evaluation_id": 456
    }
}
```

### 2.3 管理员批量删除评估记录
**接口**: `POST /api/admin/evaluations/batch-delete`

**权限要求**: 管理员

**功能描述**: 批量删除多个评估记录

**请求体**:
```json
{
    "ids": [10, 11, 12, 13, 14]
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "成功删除5条评估记录",
    "deleted_count": 5,
    "ids": [10, 11, 12, 13, 14]
}
```

**限制条件**:
- 批量删除数量不能超过100条
- ID列表不能为空

## 3. 数据模式定义

### 3.1 批量删除请求模型
```python
class BatchDeleteRequest(BaseModel):
    ids: List[int]
    
    @validator('ids')
    def validate_ids(cls, v):
        if not v:
            raise ValueError('ID列表不能为空')
        if len(v) > 100:
            raise ValueError('批量删除数量不能超过100条')
        return v
```

### 3.2 批量删除响应模型
```python
class BatchDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_count: int
    ids: List[int]
```

## 4. 安全特性

### 4.1 权限控制
- 普通用户只能删除自己的记录
- 管理员可以删除任何记录
- 所有删除操作都需要身份验证

### 4.2 软删除机制
- 回溯申请使用软删除（设置 `deleted_at` 字段）
- 评估记录使用硬删除（直接从数据库删除）
- 查询时自动过滤已删除的记录

### 4.3 时间限制
- 评估记录只能删除24小时内的记录（普通用户）
- 管理员不受时间限制

### 4.4 状态检查
- 回溯申请只能删除 `pending` 状态的记录（普通用户）
- 管理员可以删除任何状态的记录

## 5. 错误处理

### 5.1 常见错误码
- `404`: 记录不存在
- `403`: 无权限操作
- `400`: 请求参数错误或业务规则限制

### 5.2 错误响应示例
```json
{
    "detail": "回溯申请不存在"
}
```

```json
{
    "detail": "无权限删除此回溯申请"
}
```

```json
{
    "detail": "只能删除待审批的回溯申请"
}
```

## 6. 使用示例

### 6.1 删除单个回溯申请
```bash
curl -X DELETE "http://localhost:8000/api/rollback-requests/123" \
  -H "Authorization: Bearer <token>"
```

### 6.2 批量删除评估记录
```bash
curl -X POST "http://localhost:8000/api/admin/evaluations/batch-delete" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"ids": [1, 2, 3, 4, 5]}'
```

## 7. 注意事项

1. **数据安全**: 删除操作不可逆，请谨慎操作
2. **权限管理**: 确保只有授权用户才能执行删除操作
3. **批量限制**: 批量删除建议分批进行，避免一次性删除过多记录
4. **审计日志**: 所有删除操作都会在系统日志中记录
5. **软删除**: 回溯申请使用软删除，可以通过数据库直接恢复

## 8. 更新说明

本次更新新增了以下功能：
- 普通用户删除回溯申请接口
- 管理员强制删除回溯申请接口
- 管理员批量删除回溯申请接口
- 普通用户删除评估记录接口
- 管理员强制删除评估记录接口
- 管理员批量删除评估记录接口
- 相关的数据模式定义和验证
- 完善的权限控制和错误处理

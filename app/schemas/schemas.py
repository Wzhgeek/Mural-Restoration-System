# -*- coding: utf-8 -*-
"""
Pydantic数据模型

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

# 基础响应模型
class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# 用户相关模型
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role_key: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    unit: Optional[str] = None  # 用户单位字段

class UserResponse(BaseModel):
    user_id: int
    username: str
    full_name: str
    role_id: int  # 角色ID字段
    role_name: str
    role_key: str
    email: Optional[str]
    phone: Optional[str]
    unit: Optional[str]  # 用户单位字段
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# 工作流相关模型
class WorkflowCreate(BaseModel):
    title: str
    description: Optional[str] = None

class WorkflowUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class WorkflowResponse(BaseModel):
    workflow_id: UUID
    title: str
    description: Optional[str]
    initiator_name: str
    current_step: int
    status: str
    is_finalized: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None  # 软删除字段
    
    class Config:
        from_attributes = True

# 修复表单相关模型
class FormCreate(BaseModel):
    workflow_id: UUID
    image_desc: Optional[str] = None
    restoration_opinion: Optional[str] = None
    opinion_tags: Optional[List[str]] = None
    remark: Optional[str] = None

class FormResponse(BaseModel):
    form_id: UUID
    workflow_id: UUID
    step_no: int
    submitter_name: str
    # 单个文件字段（向后兼容）
    image_url: Optional[str]
    image_meta: Optional[dict]
    image_desc_file: Optional[str]
    opinion_file: Optional[str]
    attachment: Optional[str]
    # 多文件字段
    image_urls: Optional[List[str]] = None
    image_metas: Optional[List[dict]] = None
    image_desc_files: Optional[List[str]] = None
    opinion_files: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    # 其他字段
    image_desc: Optional[str]
    restoration_opinion: Optional[str]
    opinion_tags: Optional[List[str]]
    remark: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# 评估相关模型
class EvaluationCreate(BaseModel):
    workflow_id: UUID
    score: int
    comment: Optional[str] = None
    evaluation_file: Optional[str] = None  # 统一字段名
    personnel_confirmation: Optional[str] = None  # 人员确认字段（用户名+单位）
    
    @validator('score')
    def validate_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError('评分必须在0-100之间')
        return v

class EvaluationResponse(BaseModel):
    evaluate_id: int
    workflow_id: UUID
    evaluator_name: str
    score: int
    comment: Optional[str]
    # 单个文件字段（向后兼容）
    evaluation_file: Optional[str]  # 统一字段名
    # 多文件字段
    evaluation_files: Optional[List[str]] = None
    personnel_confirmation: Optional[str]  # 人员确认字段（用户名+单位）
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 回溯申请相关模型
class RollbackRequestCreate(BaseModel):
    workflow_id: UUID
    target_form_id: UUID
    reason: str

class RollbackRequestApprove(BaseModel):
    approve: bool
    comment: Optional[str] = None

class RollbackRequestResponse(BaseModel):
    rollback_id: int
    workflow_id: UUID
    requester_name: str
    target_form_id: UUID
    reason: str
    # 单个文件字段（向后兼容）
    support_file_url: Optional[str]
    # 多文件字段
    support_file_urls: Optional[List[str]] = None
    status: str
    approver_name: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# 流转记录模型
class StepLogResponse(BaseModel):
    step_log_id: int
    form_id: UUID
    action: str
    operator_name: str
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# 仪表板数据模型
class DashboardStats(BaseModel):
    total_workflows: int
    running_workflows: int
    finished_workflows: int
    pending_evaluations: int
    pending_rollbacks: int
    my_workflows: Optional[int] = None
    recent_activities: List[dict]
    completion_rate: Optional[float] = None
    
    # 管理员专用字段
    workflow_trend: Optional[float] = None
    workflow_trend_data: Optional[dict] = None
    
    # 修复专家专用字段
    my_running_workflows: Optional[int] = None
    my_finished_workflows: Optional[int] = None
    my_rollback_requests: Optional[int] = None
    monthly_submissions: Optional[int] = None
    average_score: Optional[float] = None
    personal_progress: Optional[dict] = None
    
    # 评估专家专用字段
    completed_evaluations: Optional[int] = None
    monthly_evaluations: Optional[int] = None
    average_given_score: Optional[float] = None
    high_score_rate: Optional[float] = None
    evaluation_efficiency: Optional[float] = None
    
    # 通用图表数据
    score_distribution: Optional[dict] = None

# 文件上传响应
class FileUploadResponse(BaseModel):
    filename: str
    file_url: str
    file_size: int
    content_type: str

# 多文件上传响应
class MultiFileUploadResponse(BaseModel):
    files: List[FileUploadResponse]
    total_count: int
    success_count: int
    failed_count: int
    failed_files: Optional[List[dict]] = None  # 失败的文件信息

# 批量删除请求模型
class BatchDeleteRequest(BaseModel):
    ids: List[int]
    
    @validator('ids')
    def validate_ids(cls, v):
        if not v:
            raise ValueError('ID列表不能为空')
        if len(v) > 100:
            raise ValueError('批量删除数量不能超过100条')
        return v

# 批量删除响应模型
class BatchDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_count: int
    ids: List[int]

# 分页响应模型
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    total_pages: int

# 回溯申请分页响应模型
class RollbackRequestPaginatedResponse(BaseModel):
    items: List[RollbackRequestResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# 工作流分页响应模型
class WorkflowPaginatedResponse(BaseModel):
    items: List[WorkflowResponse]
    total: int
    page: int
    limit: int
    total_pages: int



# -*- coding: utf-8 -*-
"""
数据库模型定义

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, SmallInteger, CheckConstraint, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"
    
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_key = Column(String(20), unique=True, nullable=False)
    role_name = Column(String(50), nullable=False)
    
    # 关系
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    unit = Column(String(100))  # 用户单位字段
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)  # 软删除字段
    
    # 关系
    role = relationship("Role", back_populates="users")
    initiated_workflows = relationship("Workflow", back_populates="initiator")
    submitted_forms = relationship("Form", back_populates="submitter")
    step_logs = relationship("StepLog", back_populates="operator")
    evaluations = relationship("Evaluation", back_populates="evaluator")
    rollback_requests = relationship("RollbackRequest", foreign_keys="RollbackRequest.requester_id", back_populates="requester")
    rollback_approvals = relationship("RollbackRequest", foreign_keys="RollbackRequest.approver_id", back_populates="approver")

class Workflow(Base):
    __tablename__ = "workflows"
    
    workflow_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    initiator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    current_step = Column(Integer, default=1)
    status = Column(String(20), default='draft')  # draft, running, paused, finished, revoked
    is_finalized = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)  # 软删除字段
    
    # 关系
    initiator = relationship("User", back_populates="initiated_workflows")
    forms = relationship("Form", back_populates="workflow")
    evaluations = relationship("Evaluation", back_populates="workflow")
    rollback_requests = relationship("RollbackRequest", back_populates="workflow")

class Form(Base):
    __tablename__ = "forms"
    
    form_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.workflow_id"), nullable=False)
    step_no = Column(Integer, nullable=False)
    submitter_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    image_url = Column(Text)
    image_meta = Column(JSONB)
    image_desc = Column(Text)
    image_desc_file = Column(Text)
    restoration_opinion = Column(Text)
    opinion_tags = Column(ARRAY(String))
    opinion_file = Column(Text)
    remark = Column(Text)
    attachment = Column(Text)
    is_rollback_from = Column(UUID(as_uuid=True), ForeignKey("forms.form_id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())  # 添加更新时间字段
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)  # 软删除字段
    
    # 关系
    workflow = relationship("Workflow", back_populates="forms")
    submitter = relationship("User", back_populates="submitted_forms")
    step_logs = relationship("StepLog", back_populates="form")
    rollback_requests = relationship("RollbackRequest", back_populates="target_form")

class StepLog(Base):
    __tablename__ = "step_logs"
    
    step_log_id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(UUID(as_uuid=True), ForeignKey("forms.form_id"), nullable=False)
    action = Column(String(20), nullable=False)  # submit, rollback, finalize, revoke
    operator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    comment = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # 关系
    form = relationship("Form", back_populates="step_logs")
    operator = relationship("User", back_populates="step_logs")

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    evaluate_id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.workflow_id"), nullable=False)
    evaluator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    score = Column(SmallInteger, CheckConstraint('score >= 0 AND score <= 100'))
    comment = Column(Text)
    evaluation_file = Column(Text, nullable=True)  # 评估意见支撑文件URL（统一字段名）
    personnel_confirmation = Column(String(200))  # 人员确认字段（用户名+单位）
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    workflow = relationship("Workflow", back_populates="evaluations")
    evaluator = relationship("User", back_populates="evaluations")

class RollbackRequest(Base):
    __tablename__ = "rollback_requests"
    
    rollback_id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.workflow_id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    target_form_id = Column(UUID(as_uuid=True), ForeignKey("forms.form_id"), nullable=False)
    reason = Column(Text, nullable=False)
    support_file_url = Column(Text)  # 支撑材料文件URL
    status = Column(String(20), default='pending')  # pending, approved, rejected
    approver_id = Column(Integer, ForeignKey("users.user_id"))
    approved_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)  # 软删除字段
    
    # 关系
    workflow = relationship("Workflow", back_populates="rollback_requests")
    requester = relationship("User", foreign_keys=[requester_id], back_populates="rollback_requests")
    approver = relationship("User", foreign_keys=[approver_id], back_populates="rollback_approvals")
    target_form = relationship("Form", back_populates="rollback_requests")

class SystemConfig(Base):
    __tablename__ = "system_configs"
    
    config_key = Column(String(50), primary_key=True)
    config_value = Column(Text)
    description = Column(String(255))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())



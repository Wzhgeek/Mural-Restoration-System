# -*- coding: utf-8 -*-
"""
邮件验证相关API路由

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import re

from ..core.database import get_db
from ..models import User, Role
from ..schemas import (
    EmailVerificationRequest, 
    EmailVerificationCode, 
    EmailVerificationResponse,
    UserRegistrationWithEmail,
    UserResponse,
    ResponseModel
)
from ..auth import get_password_hash
from ..services.email_service import email_service

router = APIRouter(prefix="/api/email", tags=["邮件验证"])

@router.post("/send-verification", response_model=EmailVerificationResponse)
async def send_verification_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """发送邮箱验证码"""
    email = request.email.lower().strip()
    
    # 验证邮箱格式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱格式不正确"
        )
    
    # 检查邮箱是否已被使用
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    try:
        # 发送验证码邮件
        verification_code = email_service.send_verification_email(email, "用户")
        
        return EmailVerificationResponse(
            success=True,
            message=f"验证码已发送到 {email}，请查收邮件",
            email=email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"邮件发送失败: {str(e)}"
        )

@router.post("/verify-code", response_model=EmailVerificationResponse)
async def verify_email_code(
    request: EmailVerificationCode,
    db: Session = Depends(get_db)
):
    """验证邮箱验证码"""
    email = request.email.lower().strip()
    code = request.code.strip()
    
    # 验证邮箱格式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱格式不正确"
        )
    
    # 验证验证码格式
    if not code.isdigit() or len(code) != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码格式不正确"
        )
    
    # 验证验证码
    if email_service.verify_email_code(email, code):
        return EmailVerificationResponse(
            success=True,
            message="邮箱验证成功",
            email=email
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

@router.post("/register", response_model=UserResponse)
async def register_user_with_email(
    request: UserRegistrationWithEmail,
    db: Session = Depends(get_db)
):
    """使用邮箱验证注册用户"""
    # 验证邮箱验证码
    if not email_service.verify_email_code(request.email.lower().strip(), request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱验证码错误或已过期"
        )
    
    # 检查用户名是否已存在
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已被使用
    existing_email = db.query(User).filter(User.email == request.email.lower().strip()).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 获取角色
    role = db.query(Role).filter(Role.role_key == request.role_key).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的角色"
        )
    
    # 创建用户
    user = User(
        username=request.username,
        password_hash=get_password_hash(request.password),
        full_name=request.full_name,
        role_id=role.role_id,
        email=request.email.lower().strip(),
        phone=request.phone,
        unit=request.unit,
        email_verified=True,  # 邮箱已验证
        email_verified_at=func.now()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 发送欢迎邮件
    try:
        email_service.send_welcome_email(user.email, user.full_name)
    except Exception as e:
        # 欢迎邮件发送失败不影响注册流程
        print(f"欢迎邮件发送失败: {str(e)}")
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        full_name=user.full_name,
        role_id=user.role_id,
        role_name=user.role.role_name,
        role_key=user.role.role_key,
        email=user.email,
        phone=user.phone,
        unit=user.unit,
        is_active=user.is_active,
        email_verified=user.email_verified,
        email_verified_at=user.email_verified_at,
        created_at=user.created_at
    )

@router.post("/resend-verification", response_model=EmailVerificationResponse)
async def resend_verification_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """重新发送邮箱验证码"""
    email = request.email.lower().strip()
    
    # 验证邮箱格式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱格式不正确"
        )
    
    # 检查邮箱是否已被使用
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    try:
        # 发送验证码邮件
        verification_code = email_service.send_verification_email(email, "用户")
        
        return EmailVerificationResponse(
            success=True,
            message=f"验证码已重新发送到 {email}，请查收邮件",
            email=email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"邮件发送失败: {str(e)}"
        )

@router.get("/check-email/{email}")
async def check_email_availability(email: str, db: Session = Depends(get_db)):
    """检查邮箱是否可用"""
    email = email.lower().strip()
    
    # 验证邮箱格式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱格式不正确"
        )
    
    # 检查邮箱是否已被使用
    existing_user = db.query(User).filter(User.email == email).first()
    
    return {
        "email": email,
        "available": existing_user is None,
        "message": "邮箱可用" if existing_user is None else "邮箱已被注册"
    }

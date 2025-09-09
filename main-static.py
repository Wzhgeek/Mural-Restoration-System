# -*- coding: utf-8 -*-
"""
克孜尔石窟壁画智慧修复全生命周期管理系统 - 主应用程序

本模块是系统的核心入口，负责：
- FastAPI应用实例的创建和配置
- 中间件的注册和配置
- 静态文件服务的挂载
- API路由的注册
- 系统启动时的初始化操作

作者: 王梓涵
邮箱: wangzh011031@163.com
创建时间: 2025年9月2日
版本: 1.0.0
"""

# ============================================================================
# 第三方库导入
# ============================================================================
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form as FormField, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import os
import shutil
from datetime import datetime, timedelta

# ============================================================================
# 本地模块导入
# ============================================================================
from app.core.config import settings
from app.core.database import get_db, create_tables, init_data
from app.models import *
from app.schemas import *
from app.auth import *
from app.services import file_service
from app.api import router as api_router

# ============================================================================
# FastAPI应用实例创建和配置
# ============================================================================

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="克孜尔石窟壁画智慧修复全生命周期管理系统",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建静态文件目录并挂载静态文件服务
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(api_router)

# ============================================================================
# 基础路由和认证接口
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    根路径路由 - 返回系统登录页面
    
    Returns:
        FileResponse: 登录页面的HTML文件响应
    """
    return FileResponse("static/login.html")


@app.post("/api/login", response_model=LoginResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录认证接口
    
    Args:
        user_data (UserLogin): 用户登录信息，包含用户名和密码
        db (Session): 数据库会话依赖注入
        
    Returns:
        LoginResponse: 登录成功响应，包含访问令牌和用户信息
        
    Raises:
        HTTPException: 当用户名或密码错误时抛出401未授权异常
    """
    # 验证用户凭据
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成访问令牌
    access_token = create_access_token(data={"sub": user.username})
    
    # 构建用户响应对象
    user_response = UserResponse(
        user_id=user.user_id,
        username=user.username,
        full_name=user.full_name,
        role_name=user.role.role_name,
        role_key=user.role.role_key,
        email=user.email,
        phone=user.phone,
        is_active=user.is_active,
        created_at=user.created_at
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

# ============================================================================
# 用户管理接口
# ============================================================================

@app.get("/api/user/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息
    
    Args:
        current_user (User): 当前登录用户对象，通过依赖注入获取
        
    Returns:
        UserResponse: 当前用户的详细信息响应
    """
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        full_name=current_user.full_name,
        role_name=current_user.role.role_name,
        role_key=current_user.role.role_key,
        email=current_user.email,
        phone=current_user.phone,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@app.put("/api/user/profile", response_model=UserResponse)
async def update_user_profile(
    full_name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户的个人信息
    
    Args:
        full_name (str): 用户真实姓名
        email (Optional[str]): 用户邮箱地址
        phone (Optional[str]): 用户手机号码
        current_user (User): 当前登录用户对象
        db (Session): 数据库会话依赖注入
        
    Returns:
        UserResponse: 更新后的用户信息响应
    """
    # 更新用户信息字段
    current_user.full_name = full_name
    current_user.email = email
    current_user.phone = phone
    
    # 提交数据库事务并刷新对象
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        full_name=current_user.full_name,
        role_name=current_user.role.role_name,
        role_key=current_user.role.role_key,
        email=current_user.email,
        phone=current_user.phone,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@app.put("/api/user/password")
async def change_user_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户的登录密码
    
    Args:
        current_password (str): 当前密码
        new_password (str): 新密码
        current_user (User): 当前登录用户对象
        db (Session): 数据库会话依赖注入
        
    Returns:
        dict: 包含成功消息的响应字典
        
    Raises:
        HTTPException: 当当前密码验证失败时抛出400错误
    """
    from app.auth.auth import verify_password, get_password_hash
    
    # 验证当前密码是否正确
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 更新为新密码的哈希值
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "密码修改成功"}

# ============================================================================
# 系统配置接口
# ============================================================================

@app.get("/api/privacy-agreement")
async def get_privacy_agreement(db: Session = Depends(get_db)):
    """
    获取系统保密协议内容
    
    Args:
        db (Session): 数据库会话依赖注入
        
    Returns:
        ResponseModel: 包含保密协议内容的响应模型
    """
    # 查询保密协议配置
    config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "privacy_agreement"
    ).first()
    
    if not config:
        return ResponseModel(
            success=False,
            message="未找到保密协议",
            data=None
        )
    
    return ResponseModel(
        success=True,
        message="获取成功",
        data={"content": config.config_value}
    )


# ============================================================================
# 仪表板数据接口
# ============================================================================

@app.get("/api/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    获取仪表板统计数据
    
    根据用户角色返回不同的统计数据：
    - 管理员：全局统计数据和趋势分析
    - 修复专家：个人工作流统计和进度数据
    - 评估专家：评估工作统计和评分分布
    
    Args:
        current_user (User): 当前登录用户对象
        db (Session): 数据库会话依赖注入
        
    Returns:
        DashboardStats: 仪表板统计数据响应模型
    """
    from datetime import datetime, timedelta
    import random
    
    # 获取当前用户角色
    user_role = current_user.role.role_key
    
    # ========================================================================
    # 基础统计数据计算
    # ========================================================================
    
    # 工作流基础统计（排除已删除的工作流）
    total_workflows = db.query(Workflow).filter(Workflow.deleted_at.is_(None)).count()
    running_workflows = db.query(Workflow).filter(
        Workflow.status == 'running',
        Workflow.deleted_at.is_(None)
    ).count()
    finished_workflows = db.query(Workflow).filter(
        Workflow.status == 'finished',
        Workflow.deleted_at.is_(None)
    ).count()
    
    # 待评估工作流数量（仅管理员和评估专家可见）
    pending_evaluations = db.query(Workflow).filter(
        Workflow.status == 'finished',
        Workflow.deleted_at.is_(None),
        ~Workflow.evaluations.any()
    ).count() if user_role in ['admin', 'evaluator'] else 0
    
    # 待处理回溯请求数量（仅管理员可见）
    pending_rollbacks = db.query(RollbackRequest).filter(
        RollbackRequest.status == 'pending'
    ).count() if user_role == 'admin' else 0
    
    # 计算工作流完成率
    completion_rate = round((finished_workflows / total_workflows * 100) if total_workflows > 0 else 0, 1)
    
    # ========================================================================
    # 角色特定统计数据初始化
    # ========================================================================
    
    # 修复专家个人统计数据
    my_workflows = None
    my_running_workflows = None
    my_finished_workflows = None
    my_rollback_requests = None
    monthly_submissions = None
    average_score = None
    
    # 评估专家统计数据
    completed_evaluations = None
    monthly_evaluations = None
    average_given_score = None
    high_score_rate = None
    evaluation_efficiency = None
    
    # ========================================================================
    # 修复专家角色统计计算
    # ========================================================================
    
    if user_role == 'restorer':
        # 个人工作流统计（排除已删除的工作流）
        my_workflows = db.query(Workflow).filter(
            Workflow.initiator_id == current_user.user_id,
            Workflow.deleted_at.is_(None)
        ).count()
        
        my_running_workflows = db.query(Workflow).filter(
            Workflow.initiator_id == current_user.user_id,
            Workflow.status == 'running',
            Workflow.deleted_at.is_(None)
        ).count()
        
        my_finished_workflows = db.query(Workflow).filter(
            Workflow.initiator_id == current_user.user_id,
            Workflow.status == 'finished',
            Workflow.deleted_at.is_(None)
        ).count()
        
        # 个人回溯请求统计
        my_rollback_requests = db.query(RollbackRequest).filter(
            RollbackRequest.requester_id == current_user.user_id
        ).count()
        
        # 计算本月提交的工作流数量
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_submissions = db.query(Workflow).filter(
            Workflow.initiator_id == current_user.user_id,
            Workflow.created_at >= current_month,
            Workflow.deleted_at.is_(None)
        ).count()
        
        # 平均评分（模拟数据，实际应从评估记录计算）
        average_score = round(random.uniform(7.5, 9.5), 1)
    
    # ========================================================================
    # 评估专家角色统计计算
    # ========================================================================
    
    if user_role == 'evaluator':
        # 个人评估工作统计
        completed_evaluations = db.query(Evaluation).filter(
            Evaluation.evaluator_id == current_user.user_id
        ).count()
        
        # 计算本月完成的评估数量
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_evaluations = db.query(Evaluation).filter(
            Evaluation.evaluator_id == current_user.user_id,
            Evaluation.created_at >= current_month
        ).count()
        
        # 评估质量指标（模拟数据，实际应从评估记录计算）
        average_given_score = round(random.uniform(7.0, 9.0), 1)
        high_score_rate = round(random.uniform(60, 85), 1)
        evaluation_efficiency = round(random.uniform(2, 5), 1)
    
    # ========================================================================
    # 最近活动数据获取
    # ========================================================================
    
    recent_activities = []
    recent_logs = db.query(StepLog).order_by(desc(StepLog.created_at)).limit(10).all()
    
    # 处理最近活动日志数据
    for log in recent_logs:
        # 获取关联的工作流标题
        workflow_title = None
        if log.form and log.form.workflow:
            workflow_title = log.form.workflow.title
        
        recent_activities.append({
            "action": log.action,
            "operator": log.operator.full_name,
            "time": log.created_at.strftime("%Y-%m-%d %H:%M"),
            "form_id": str(log.form_id),
            "workflow_title": workflow_title,
            "comment": log.comment
        })
    
    # ========================================================================
    # 基础响应数据构建
    # ========================================================================
    
    dashboard_data = {
        "total_workflows": total_workflows,
        "running_workflows": running_workflows,
        "finished_workflows": finished_workflows,
        "pending_evaluations": pending_evaluations,
        "pending_rollbacks": pending_rollbacks,
        "my_workflows": my_workflows,
        "recent_activities": recent_activities,
        "completion_rate": completion_rate
    }
    
    # ========================================================================
    # 角色特定数据添加
    # ========================================================================
    
    if user_role == 'admin':
        # ====================================================================
        # 管理员角色：全局趋势分析数据
        # ====================================================================
        
        # 计算最近7天的工作流创建趋势
        today = datetime.now().date()
        week_ago = today - timedelta(days=6)
        
        # 获取最近7天每天的工作流创建数量
        daily_workflows = []
        labels = []
        
        for i in range(7):
            current_date = week_ago + timedelta(days=i)
            count = db.query(Workflow).filter(
                func.date(Workflow.created_at) == current_date,
                Workflow.deleted_at.is_(None)
            ).count()
            daily_workflows.append(count)
            
            # 生成中文日期标签
            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            labels.append(weekdays[current_date.weekday()])
        
        # 计算本周与上周的趋势对比
        this_week_total = sum(daily_workflows)
        last_week_start = week_ago - timedelta(days=7)
        last_week_total = db.query(Workflow).filter(
            func.date(Workflow.created_at) >= last_week_start,
            func.date(Workflow.created_at) < week_ago,
            Workflow.deleted_at.is_(None)
        ).count()
        
        # 计算趋势百分比
        if last_week_total > 0:
            workflow_trend = round(((this_week_total - last_week_total) / last_week_total) * 100, 1)
        else:
            workflow_trend = 0.0 if this_week_total == 0 else 100.0
        
        dashboard_data["workflow_trend"] = workflow_trend
        
        # 工作流趋势图表数据（最近7天真实数据）
        dashboard_data["workflow_trend_data"] = {
            "labels": labels,
            "values": daily_workflows
        }
        
        # ====================================================================
        # 管理员角色：全局评分分布统计
        # ====================================================================
        
        # 初始化评分分布统计
        score_ranges = {
            "0-6": 0,   # 0-60分
            "6-7": 0,   # 60-70分
            "7-8": 0,   # 70-80分
            "8-9": 0,   # 80-90分
            "9-10": 0   # 90-100分
        }
        
        # 统计所有评估记录的评分分布
        evaluations = db.query(Evaluation).all()
        for evaluation in evaluations:
            score = evaluation.score
            if score < 60:
                score_ranges["0-6"] += 1
            elif score < 70:
                score_ranges["6-7"] += 1
            elif score < 80:
                score_ranges["7-8"] += 1
            elif score < 90:
                score_ranges["8-9"] += 1
            else:
                score_ranges["9-10"] += 1
        
        dashboard_data["score_distribution"] = score_ranges
    
    elif user_role == 'restorer':
        # ====================================================================
        # 修复专家角色：个人工作数据
        # ====================================================================
        
        # 添加个人工作流统计数据
        dashboard_data.update({
            "my_running_workflows": my_running_workflows,
            "my_finished_workflows": my_finished_workflows,
            "my_rollback_requests": my_rollback_requests,
            "monthly_submissions": monthly_submissions,
            "average_score": average_score
        })
        
        # 个人工作进度和质量指标（模拟数据）
        dashboard_data["personal_progress"] = {
            "monthly_completion": round(random.uniform(60, 95), 1),
            "quality_score": round(random.uniform(75, 95), 1)
        }
    
    elif user_role == 'evaluator':
        # ====================================================================
        # 评估专家角色：评估工作数据
        # ====================================================================
        
        # 添加评估工作统计数据
        dashboard_data.update({
            "completed_evaluations": completed_evaluations,
            "monthly_evaluations": monthly_evaluations,
            "average_given_score": average_given_score,
            "high_score_rate": high_score_rate,
            "evaluation_efficiency": evaluation_efficiency
        })
        
        # ====================================================================
        # 评估专家个人评分分布统计
        # ====================================================================
        
        # 初始化个人评分分布统计
        score_ranges = {
            "0-6": 0,   # 0-60分
            "6-7": 0,   # 60-70分
            "7-8": 0,   # 70-80分
            "8-9": 0,   # 80-90分
            "9-10": 0   # 90-100分
        }
        
        # 统计当前评估专家的评估记录评分分布
        my_evaluations = db.query(Evaluation).filter(
            Evaluation.evaluator_id == current_user.user_id
        ).all()
        
        for evaluation in my_evaluations:
            score = evaluation.score
            if score < 60:
                score_ranges["0-6"] += 1
            elif score < 70:
                score_ranges["6-7"] += 1
            elif score < 80:
                score_ranges["7-8"] += 1
            elif score < 90:
                score_ranges["8-9"] += 1
            else:
                score_ranges["9-10"] += 1
        
        dashboard_data["score_distribution"] = score_ranges
    
    return DashboardStats(**dashboard_data)


# ============================================================================
# 文件管理接口
# ============================================================================

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    文件上传接口
    
    支持上传图片和文档文件到MinIO对象存储服务
    
    Args:
        file (UploadFile): 上传的文件对象
        current_user (User): 当前登录用户对象
        
    Returns:
        FileUploadResponse: 文件上传成功响应，包含文件信息
        
    Raises:
        HTTPException: 当文件大小超限或类型不支持时抛出相应错误
    """
    # 验证文件大小限制
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="文件大小超过限制"
        )
    
    # 验证文件类型是否支持
    allowed_types = settings.ALLOWED_IMAGE_TYPES + settings.ALLOWED_FILE_TYPES
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型"
        )
    
    try:
        # 读取文件内容到内存
        file_content = await file.read()
        
        # 调用文件服务上传到MinIO存储
        file_url = file_service.upload_file(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        return FileUploadResponse(
            filename=file.filename,
            file_url=file_url,
            file_size=len(file_content),
            content_type=file.content_type
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

# ============================================================================
# 工作流管理接口
# ============================================================================

@app.post("/api/workflows", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(require_restorer),
    db: Session = Depends(get_db)
):
    """
    创建新的修复工作流
    
    仅修复专家可以创建新的工作流
    
    Args:
        workflow_data (WorkflowCreate): 工作流创建数据
        current_user (User): 当前登录用户（必须是修复专家）
        db (Session): 数据库会话依赖注入
        
    Returns:
        WorkflowResponse: 创建成功的工作流响应
    """
    # 创建新的工作流实例
    workflow = Workflow(
        title=workflow_data.title,
        description=workflow_data.description,
        initiator_id=current_user.user_id,
        status='draft'
    )
    
    # 保存到数据库
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return WorkflowResponse(
        workflow_id=workflow.workflow_id,
        title=workflow.title,
        description=workflow.description,
        initiator_name=workflow.initiator.full_name,
        current_step=workflow.current_step,
        status=workflow.status,
        is_finalized=workflow.is_finalized,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at
    )


@app.get("/api/workflows", response_model=List[WorkflowResponse])
async def get_workflows(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取工作流列表
    
    根据用户角色返回相应的工作流列表：
    - 修复专家：只能看到自己创建的工作流
    - 管理员和评估专家：可以看到所有工作流
    
    Args:
        status (Optional[str]): 工作流状态过滤条件
        current_user (User): 当前登录用户对象
        db (Session): 数据库会话依赖注入
        
    Returns:
        List[WorkflowResponse]: 工作流列表响应
    """
    # 构建基础查询（排除已删除的工作流）
    query = db.query(Workflow).filter(Workflow.deleted_at.is_(None))
    
    # 根据用户角色进行数据过滤
    if current_user.role.role_key == 'restorer':
        query = query.filter(Workflow.initiator_id == current_user.user_id)
    
    # 根据状态过滤
    if status:
        query = query.filter(Workflow.status == status)
    
    # 使用LEFT JOIN确保即使用户不存在也能获取工作流数据
    workflows = query.join(User, Workflow.initiator_id == User.user_id, isouter=True)\
                    .order_by(desc(Workflow.updated_at))\
                    .all()
    
    return [
        WorkflowResponse(
            workflow_id=w.workflow_id,
            title=w.title,
            description=w.description,
            initiator_name=w.initiator.full_name if w.initiator else '未知用户',
            current_step=w.current_step,
            status=w.status,
            is_finalized=w.is_finalized,
            created_at=w.created_at,
            updated_at=w.updated_at
        ) for w in workflows
    ]

# ============================================================================
# 管理员工作流管理接口
# ============================================================================

@app.get("/api/admin/workflows", response_model=List[WorkflowResponse])
async def admin_get_all_workflows(
    status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员获取所有工作流列表（不分页）
    
    仅管理员可以访问此接口，获取系统中所有工作流
    
    Args:
        status (Optional[str]): 工作流状态过滤条件
        current_user (User): 当前登录用户（必须是管理员）
        db (Session): 数据库会话依赖注入
        
    Returns:
        List[WorkflowResponse]: 所有工作流列表响应
    """
    # 构建查询（排除已删除的工作流）
    query = db.query(Workflow).filter(Workflow.deleted_at.is_(None))
    
    # 根据状态过滤
    if status:
        query = query.filter(Workflow.status == status)
    
    # 使用LEFT JOIN确保即使用户不存在也能获取工作流数据
    workflows = query.join(User, Workflow.initiator_id == User.user_id, isouter=True)\
                    .order_by(desc(Workflow.updated_at))\
                    .all()
    
    return [
        WorkflowResponse(
            workflow_id=w.workflow_id,
            title=w.title,
            description=w.description,
            initiator_name=w.initiator.full_name if w.initiator else '未知用户',
            current_step=w.current_step,
            status=w.status,
            is_finalized=w.is_finalized,
            created_at=w.created_at,
            updated_at=w.updated_at
        ) for w in workflows
    ]


@app.get("/api/workflows/paginated", response_model=WorkflowPaginatedResponse)
async def get_workflows_paginated(
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取工作流列表（带分页功能）
    
    仅管理员可以访问此接口，支持搜索、状态筛选和分页
    
    Args:
        search (Optional[str]): 搜索关键词（搜索标题和描述）
        status (Optional[str]): 工作流状态过滤条件
        page (int): 页码，从1开始
        limit (int): 每页数量，默认10条
        current_user (User): 当前登录用户（必须是管理员）
        db (Session): 数据库会话依赖注入
        
    Returns:
        WorkflowPaginatedResponse: 分页工作流列表响应
    """
    # 构建基础查询（排除已删除的工作流）
    query = db.query(Workflow).filter(Workflow.deleted_at.is_(None))
    
    # 搜索功能：搜索标题和描述
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Workflow.title.ilike(search_pattern),
                Workflow.description.ilike(search_pattern)
            )
        )
    
    # 根据状态过滤
    if status:
        query = query.filter(Workflow.status == status)
    
    # 计算总数
    total = query.count()
    
    # 计算总页数
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    
    # 确保页码有效
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # 计算偏移量
    offset = (page - 1) * limit
    
    # 使用LEFT JOIN确保即使用户不存在也能获取工作流数据
    workflows = query.join(User, Workflow.initiator_id == User.user_id, isouter=True)\
                    .order_by(desc(Workflow.updated_at))\
                    .offset(offset)\
                    .limit(limit)\
                    .all()
    
    # 构建响应数据
    items = [
        WorkflowResponse(
            workflow_id=w.workflow_id,
            title=w.title,
            description=w.description,
            initiator_name=w.initiator.full_name if w.initiator else '未知用户',
            current_step=w.current_step,
            status=w.status,
            is_finalized=w.is_finalized,
            created_at=w.created_at,
            updated_at=w.updated_at
        ) for w in workflows
    ]
    
    return WorkflowPaginatedResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@app.put("/api/admin/workflows/{workflow_id}", response_model=WorkflowResponse)
async def admin_update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员更新工作流信息
    
    仅管理员可以更新工作流的基本信息
    
    Args:
        workflow_id (UUID): 工作流唯一标识符
        workflow_data (WorkflowUpdate): 工作流更新数据
        current_user (User): 当前登录用户（必须是管理员）
        db (Session): 数据库会话依赖注入
        
    Returns:
        WorkflowResponse: 更新后的工作流响应
        
    Raises:
        HTTPException: 当工作流不存在时抛出404错误
    """
    # 查找目标工作流（排除已删除的）
    workflow = db.query(Workflow).filter(
        Workflow.workflow_id == workflow_id,
        Workflow.deleted_at.is_(None)
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 更新工作流字段
    if workflow_data.title is not None:
        workflow.title = workflow_data.title
    if workflow_data.description is not None:
        workflow.description = workflow_data.description
    if workflow_data.status is not None:
        workflow.status = workflow_data.status
    
    # 更新修改时间
    workflow.updated_at = func.now()
    
    # 提交更改
    db.commit()
    db.refresh(workflow)
    
    return WorkflowResponse(
        workflow_id=workflow.workflow_id,
        title=workflow.title,
        description=workflow.description,
        initiator_name=workflow.initiator.full_name,
        current_step=workflow.current_step,
        status=workflow.status,
        is_finalized=workflow.is_finalized,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at
    )


@app.delete("/api/admin/workflows/{workflow_id}")
async def admin_delete_workflow(
    workflow_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员软删除工作流
    
    仅管理员可以删除工作流，采用软删除方式，设置deleted_at字段
    
    Args:
        workflow_id (UUID): 工作流唯一标识符
        current_user (User): 当前登录用户（必须是管理员）
        db (Session): 数据库会话依赖注入
        
    Returns:
        ResponseModel: 删除成功响应
        
    Raises:
        HTTPException: 当工作流不存在时抛出相应错误
    """
    # 查找目标工作流（排除已删除的）
    workflow = db.query(Workflow).filter(
        Workflow.workflow_id == workflow_id,
        Workflow.deleted_at.is_(None)
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 执行软删除操作
    workflow.deleted_at = func.now()
    db.commit()
    
    return ResponseModel(
        success=True,
        message="工作流已删除",
        data={"workflow_id": str(workflow_id)}
    )


@app.post("/api/admin/workflows/batch-delete")
async def admin_batch_delete_workflows(
    workflow_ids: List[UUID],
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员批量软删除工作流
    
    仅管理员可以批量删除工作流，采用软删除方式
    
    Args:
        workflow_ids (List[UUID]): 工作流ID列表
        current_user (User): 当前登录用户（必须是管理员）
        db (Session): 数据库会话依赖注入
        
    Returns:
        ResponseModel: 批量删除结果响应
    """
    if not workflow_ids:
        raise HTTPException(status_code=400, detail="工作流ID列表不能为空")
    
    # 查找所有目标工作流（排除已删除的）
    workflows = db.query(Workflow).filter(
        Workflow.workflow_id.in_(workflow_ids),
        Workflow.deleted_at.is_(None)
    ).all()
    
    if not workflows:
        raise HTTPException(status_code=404, detail="未找到可删除的工作流")
    
    # 执行批量软删除操作
    deleted_count = 0
    for workflow in workflows:
        workflow.deleted_at = func.now()
        deleted_count += 1
    
    db.commit()
    
    return ResponseModel(
        success=True,
        message=f"成功删除 {deleted_count} 个工作流",
        data={
            "deleted_count": deleted_count,
            "total_requested": len(workflow_ids)
        }
    )

# ============================================================================
# 应用生命周期事件
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    应用启动事件处理器
    
    在FastAPI应用启动时执行以下操作：
    1. 创建数据库表结构
    2. 初始化基础数据
    3. 输出启动信息和默认账号信息
    """
    try:
        # 创建数据库表结构
        create_tables()
        
        # 初始化系统基础数据
        init_data()
        
        # 输出启动成功信息
        print(f"🚀 {settings.APP_NAME} 启动成功")
        print(f"📊 管理端口: {settings.ADMIN_PORT}")
        print(f"🌐 服务端口: {settings.APP_PORT}")
        print("📝 默认管理员账号: admin / admin123")
        print("👨‍🔧 修复专家账号: restorer1 / 123456")
        print("👨‍⚖️ 评估专家账号: evaluator1 / 123456")
        
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")


# ============================================================================
# 主程序入口
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # 启动FastAPI应用服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
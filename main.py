"""
克孜尔石窟壁画智慧修复全生命周期管理系统
主应用程序
"""
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

from app.core.config import settings
from app.core.database import get_db, create_tables, init_data
from app.models import *
from app.schemas import *
from app.auth import *
from app.services import file_service
from app.api import router as api_router
from app.schemas import *

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="克孜尔石窟壁画智慧修复全生命周期管理系统"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含API路由
app.include_router(api_router)

# 根路径返回前端页面
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回登录页面"""
    return FileResponse("static/login.html")

# 登录认证API
@app.post("/api/login", response_model=LoginResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
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

# 获取当前用户信息
@app.get("/api/user/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
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

# 更新用户个人信息
@app.put("/api/user/profile", response_model=UserResponse)
async def update_user_profile(
    full_name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户个人信息"""
    # 更新用户信息
    current_user.full_name = full_name
    current_user.email = email
    current_user.phone = phone
    
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

# 修改用户密码
@app.put("/api/user/password")
async def change_user_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改用户密码"""
    from app.auth.auth import verify_password, get_password_hash
    
    # 验证当前密码
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "密码修改成功"}

# 获取保密协议
@app.get("/api/privacy-agreement")
async def get_privacy_agreement(db: Session = Depends(get_db)):
    """获取保密协议内容"""
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

# 仪表板数据
@app.get("/api/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取仪表板统计数据"""
    from datetime import datetime, timedelta
    import random
    
    user_role = current_user.role.role_key
    
    # 基础统计
    total_workflows = db.query(Workflow).count()
    running_workflows = db.query(Workflow).filter(Workflow.status == 'running').count()
    finished_workflows = db.query(Workflow).filter(Workflow.status == 'finished').count()
    pending_evaluations = db.query(Workflow).filter(
        Workflow.status == 'finished',
        ~Workflow.evaluations.any()
    ).count() if user_role in ['admin', 'evaluator'] else 0
    
    pending_rollbacks = db.query(RollbackRequest).filter(
        RollbackRequest.status == 'pending'
    ).count() if user_role == 'admin' else 0
    
    # 计算完成率
    completion_rate = round((finished_workflows / total_workflows * 100) if total_workflows > 0 else 0, 1)
    
    # 个人统计（修复专家）
    my_workflows = None
    my_running_workflows = None
    my_finished_workflows = None
    my_rollback_requests = None
    monthly_submissions = None
    average_score = None
    
    if user_role == 'restorer':
        my_workflows = db.query(Workflow).filter(
            Workflow.initiator_id == current_user.user_id
        ).count()
        my_running_workflows = db.query(Workflow).filter(
            Workflow.initiator_id == current_user.user_id,
            Workflow.status == 'running'
        ).count()
        my_finished_workflows = db.query(Workflow).filter(
            Workflow.initiator_id == current_user.user_id,
            Workflow.status == 'finished'
        ).count()
        my_rollback_requests = db.query(RollbackRequest).filter(
            RollbackRequest.requester_id == current_user.user_id
        ).count()
        
        # 本月提交数量
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_submissions = db.query(Workflow).filter(
            Workflow.initiator_id == current_user.user_id,
            Workflow.created_at >= current_month
        ).count()
        
        # 平均评分（模拟数据）
        average_score = round(random.uniform(7.5, 9.5), 1)
    
    # 评估专家统计
    completed_evaluations = None
    monthly_evaluations = None
    average_given_score = None
    high_score_rate = None
    evaluation_efficiency = None
    
    if user_role == 'evaluator':
        completed_evaluations = db.query(Evaluation).filter(
            Evaluation.evaluator_id == current_user.user_id
        ).count()
        
        # 本月评估数量
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_evaluations = db.query(Evaluation).filter(
            Evaluation.evaluator_id == current_user.user_id,
            Evaluation.created_at >= current_month
        ).count()
        
        # 平均给分和高分率（模拟数据）
        average_given_score = round(random.uniform(7.0, 9.0), 1)
        high_score_rate = round(random.uniform(60, 85), 1)
        evaluation_efficiency = round(random.uniform(2, 5), 1)
    
    # 最近活动
    recent_activities = []
    recent_logs = db.query(StepLog).order_by(desc(StepLog.created_at)).limit(10).all()
    
    for log in recent_logs:
        # 获取工作流标题
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
    
    # 构建响应数据
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
    
    # 添加角色特定数据
    if user_role == 'admin':
        # 管理员看到趋势数据
        dashboard_data["workflow_trend"] = round(random.uniform(-5, 15), 1)  # 模拟趋势
        
        # 工作流趋势数据（最近7天）
        dashboard_data["workflow_trend_data"] = {
            "labels": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "values": [random.randint(1, 8) for _ in range(7)]
        }
        
        # 评分分布数据
        dashboard_data["score_distribution"] = {
            "0-6": random.randint(0, 3),
            "6-7": random.randint(2, 8),
            "7-8": random.randint(5, 15),
            "8-9": random.randint(8, 20),
            "9-10": random.randint(3, 12)
        }
    
    elif user_role == 'restorer':
        # 修复专家个人数据
        dashboard_data.update({
            "my_running_workflows": my_running_workflows,
            "my_finished_workflows": my_finished_workflows,
            "my_rollback_requests": my_rollback_requests,
            "monthly_submissions": monthly_submissions,
            "average_score": average_score
        })
        
        # 个人进度数据
        dashboard_data["personal_progress"] = {
            "monthly_completion": round(random.uniform(60, 95), 1),
            "quality_score": round(random.uniform(75, 95), 1)
        }
    
    elif user_role == 'evaluator':
        # 评估专家数据
        dashboard_data.update({
            "completed_evaluations": completed_evaluations,
            "monthly_evaluations": monthly_evaluations,
            "average_given_score": average_given_score,
            "high_score_rate": high_score_rate,
            "evaluation_efficiency": evaluation_efficiency
        })
        
        # 评分分布数据
        dashboard_data["score_distribution"] = {
            "0-6": random.randint(0, 2),
            "6-7": random.randint(1, 5),
            "7-8": random.randint(3, 10),
            "8-9": random.randint(5, 15),
            "9-10": random.randint(2, 8)
        }
    
    return DashboardStats(**dashboard_data)

# 文件上传
@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传文件"""
    # 检查文件大小
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="文件大小超过限制"
        )
    
    # 检查文件类型
    allowed_types = settings.ALLOWED_IMAGE_TYPES + settings.ALLOWED_FILE_TYPES
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型"
        )
    
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 上传到MinIO
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

# 工作流管理API
@app.post("/api/workflows", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(require_restorer),
    db: Session = Depends(get_db)
):
    """创建新的修复工作流"""
    workflow = Workflow(
        title=workflow_data.title,
        description=workflow_data.description,
        initiator_id=current_user.user_id,
        status='draft'
    )
    
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
    """获取工作流列表"""
    query = db.query(Workflow)
    
    # 根据角色过滤
    if current_user.role.role_key == 'restorer':
        query = query.filter(Workflow.initiator_id == current_user.user_id)
    
    if status:
        query = query.filter(Workflow.status == status)
    
    workflows = query.order_by(desc(Workflow.updated_at)).all()
    
    return [
        WorkflowResponse(
            workflow_id=w.workflow_id,
            title=w.title,
            description=w.description,
            initiator_name=w.initiator.full_name,
            current_step=w.current_step,
            status=w.status,
            is_finalized=w.is_finalized,
            created_at=w.created_at,
            updated_at=w.updated_at
        ) for w in workflows
    ]

# 管理员工作流管理API
@app.get("/api/admin/workflows", response_model=List[WorkflowResponse])
async def admin_get_all_workflows(
    status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员获取所有工作流列表"""
    query = db.query(Workflow)
    
    if status:
        query = query.filter(Workflow.status == status)
    
    workflows = query.order_by(desc(Workflow.updated_at)).all()
    
    return [
        WorkflowResponse(
            workflow_id=w.workflow_id,
            title=w.title,
            description=w.description,
            initiator_name=w.initiator.full_name,
            current_step=w.current_step,
            status=w.status,
            is_finalized=w.is_finalized,
            created_at=w.created_at,
            updated_at=w.updated_at
        ) for w in workflows
    ]

@app.put("/api/admin/workflows/{workflow_id}", response_model=WorkflowResponse)
async def admin_update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员更新工作流"""
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 更新字段
    if workflow_data.title is not None:
        workflow.title = workflow_data.title
    if workflow_data.description is not None:
        workflow.description = workflow_data.description
    if workflow_data.status is not None:
        workflow.status = workflow_data.status
    
    workflow.updated_at = func.now()
    
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
    """管理员删除工作流"""
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 检查是否有关联的表单
    form_count = db.query(Form).filter(Form.workflow_id == workflow_id).count()
    if form_count > 0:
        raise HTTPException(status_code=400, detail="无法删除包含表单的工作流")
    
    db.delete(workflow)
    db.commit()
    
    return ResponseModel(
        success=True,
        message="工作流已删除",
        data={"workflow_id": str(workflow_id)}
    )

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    try:
        create_tables()
        init_data()
        print(f"🚀 {settings.APP_NAME} 启动成功")
        print(f"📊 管理端口: {settings.ADMIN_PORT}")
        print(f"🌐 服务端口: {settings.APP_PORT}")
        print("📝 默认管理员账号: admin / admin123")
        print("👨‍🔧 修复专家账号: restorer1 / 123456")
        print("👨‍⚖️ 评估专家账号: evaluator1 / 123456")
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )

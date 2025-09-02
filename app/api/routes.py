# -*- coding: utf-8 -*-
"""
API路由扩展

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form as FormField, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from uuid import UUID
import json

from ..core.database import get_db
from ..models import *
from ..schemas import *
from ..auth import *
from ..services import file_service

router = APIRouter(prefix="/api")

# 修复表单API
@router.post("/forms", response_model=FormResponse)
async def create_form(
    workflow_id: UUID = FormField(...),
    image_desc: Optional[str] = FormField(None),
    restoration_opinion: Optional[str] = FormField(None),
    opinion_tags: Optional[str] = FormField(None),  # JSON字符串
    remark: Optional[str] = FormField(None),
    image_file: Optional[UploadFile] = File(None),
    image_desc_file: Optional[UploadFile] = File(None),
    opinion_file: Optional[UploadFile] = File(None),
    attachment_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_restorer),
    db: Session = Depends(get_db)
):
    """创建修复表单"""
    
    # 检查工作流是否存在
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 检查权限（只有工作流发起人或管理员可以提交表单）
    if current_user.role.role_key != 'admin' and workflow.initiator_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权限操作此工作流")
    
    # 获取下一个步骤号
    max_step = db.query(func.max(Form.step_no)).filter(Form.workflow_id == workflow_id).scalar()
    next_step = (max_step or 0) + 1
    
    # 处理文件上传
    image_url = None
    image_desc_file_url = None
    opinion_file_url = None
    attachment_url = None
    image_meta = None
    
    try:
        if image_file:
            image_content = await image_file.read()
            image_url = file_service.upload_file(
                file_content=image_content,
                filename=image_file.filename,
                content_type=image_file.content_type
            )
            # 简单的图片元数据
            image_meta = {
                "filename": image_file.filename,
                "size": len(image_content),
                "content_type": image_file.content_type
            }
        
        if image_desc_file:
            desc_content = await image_desc_file.read()
            image_desc_file_url = file_service.upload_file(
                file_content=desc_content,
                filename=image_desc_file.filename,
                content_type=image_desc_file.content_type
            )
        
        if opinion_file:
            opinion_content = await opinion_file.read()
            opinion_file_url = file_service.upload_file(
                file_content=opinion_content,
                filename=opinion_file.filename,
                content_type=opinion_file.content_type
            )
        
        if attachment_file:
            attachment_content = await attachment_file.read()
            attachment_url = file_service.upload_file(
                file_content=attachment_content,
                filename=attachment_file.filename,
                content_type=attachment_file.content_type
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    
    # 处理标签
    tags_list = None
    if opinion_tags:
        try:
            tags_list = json.loads(opinion_tags)
        except:
            tags_list = [tag.strip() for tag in opinion_tags.split(',') if tag.strip()]
    
    # 创建表单
    form = Form(
        workflow_id=workflow_id,
        step_no=next_step,
        submitter_id=current_user.user_id,
        image_url=image_url,
        image_meta=image_meta,
        image_desc=image_desc,
        image_desc_file=image_desc_file_url,
        restoration_opinion=restoration_opinion,
        opinion_tags=tags_list,
        opinion_file=opinion_file_url,
        remark=remark,
        attachment=attachment_url
    )
    
    db.add(form)
    
    # 更新工作流状态和当前步骤
    workflow.current_step = next_step
    if workflow.status == 'draft':
        workflow.status = 'running'
    workflow.updated_at = func.now()
    
    db.add(form)
    db.commit()
    db.refresh(form)
    
    # 记录操作日志
    log = StepLog(
        form_id=form.form_id,
        action='submit',
        operator_id=current_user.user_id,
        comment=f"提交第{next_step}步修复表单"
    )
    db.add(log)
    db.commit()
    
    return FormResponse(
        form_id=form.form_id,
        workflow_id=form.workflow_id,
        step_no=form.step_no,
        submitter_name=form.submitter.full_name,
        image_url=form.image_url,
        image_meta=form.image_meta,
        image_desc=form.image_desc,
        image_desc_file=form.image_desc_file,
        restoration_opinion=form.restoration_opinion,
        opinion_tags=form.opinion_tags,
        opinion_file=form.opinion_file,
        remark=form.remark,
        attachment=form.attachment,
        created_at=form.created_at
    )

@router.get("/workflows/{workflow_id}/forms", response_model=List[FormResponse])
async def get_workflow_forms(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作流的所有表单"""
    
    # 检查工作流权限
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 权限检查
    if (current_user.role.role_key == 'restorer' and 
        workflow.initiator_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="无权限查看此工作流")
    
    forms = db.query(Form).filter(
        Form.workflow_id == workflow_id
    ).order_by(Form.step_no).all()
    
    return [
        FormResponse(
            form_id=f.form_id,
            workflow_id=f.workflow_id,
            step_no=f.step_no,
            submitter_name=f.submitter.full_name,
            image_url=f.image_url,
            image_meta=f.image_meta,
            image_desc=f.image_desc,
            image_desc_file=f.image_desc_file,
            restoration_opinion=f.restoration_opinion,
            opinion_tags=f.opinion_tags,
            opinion_file=f.opinion_file,
            remark=f.remark,
            attachment=f.attachment,
            created_at=f.created_at
        ) for f in forms
    ]

# 工作流最终化
@router.post("/workflows/{workflow_id}/finalize")
async def finalize_workflow(
    workflow_id: UUID,
    final_form_id: UUID = FormField(...),
    current_user: User = Depends(require_restorer),
    db: Session = Depends(get_db)
):
    """设置工作流的最终方案"""
    
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 权限检查
    if (current_user.role.role_key != 'admin' and 
        workflow.initiator_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="无权限操作此工作流")
    
    # 检查表单是否属于此工作流
    form = db.query(Form).filter(
        Form.form_id == final_form_id,
        Form.workflow_id == workflow_id
    ).first()
    if not form:
        raise HTTPException(status_code=404, detail="表单不存在或不属于此工作流")
    
    # 更新工作流状态
    workflow.is_finalized = True
    workflow.status = 'finished'
    workflow.updated_at = func.now()
    
    # 记录操作日志
    log = StepLog(
        form_id=final_form_id,
        action='finalize',
        operator_id=current_user.user_id,
        comment=f"设置为最终方案"
    )
    db.add(log)
    
    db.commit()
    
    return ResponseModel(
        success=True,
        message="工作流已设置为最终方案",
        data={"workflow_id": str(workflow_id), "final_form_id": str(final_form_id)}
    )

# 评估API
@router.post("/evaluations", response_model=EvaluationResponse)
async def create_evaluation(
    workflow_id: str = FormField(...),
    score: int = FormField(...),
    comment: str = FormField(None),
    support_file: UploadFile = File(None),
    current_user: User = Depends(require_evaluator),
    db: Session = Depends(get_db)
):
    """创建评估意见"""
    
    # 验证UUID格式
    try:
        workflow_uuid = UUID(workflow_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的工作流ID格式")
    
    # 验证评分范围
    if score < 0 or score > 100:
        raise HTTPException(status_code=400, detail="评分必须在0-100之间")
    
    # 处理文件上传
    support_file_url = None
    if support_file and support_file.filename:
        try:
            support_file_url = await file_service.upload_file(support_file, "evaluation-files")
        except Exception as e:
            raise HTTPException(status_code=500, detail="文件上传失败")
    
    # 检查工作流是否存在且已完成
    workflow = db.query(Workflow).filter(
        Workflow.workflow_id == workflow_uuid,
        Workflow.status == 'finished'
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在或未完成")
    
    # 检查是否已经评估过
    existing = db.query(Evaluation).filter(
        Evaluation.workflow_id == workflow_uuid,
        Evaluation.evaluator_id == current_user.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已对此工作流进行过评估")
    
    evaluation = Evaluation(
        workflow_id=workflow_uuid,
        evaluator_id=current_user.user_id,
        score=score,
        comment=comment,
        evaluation_file=support_file_url  # 使用统一的字段名
    )
    
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    return EvaluationResponse(
        evaluate_id=evaluation.evaluate_id,
        workflow_id=evaluation.workflow_id,
        evaluator_name=evaluation.evaluator.full_name,
        score=evaluation.score,
        comment=evaluation.comment,
        evaluation_file=evaluation.evaluation_file,  # 使用统一的字段名
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at
    )

@router.get("/workflows/{workflow_id}/evaluations", response_model=List[EvaluationResponse])
async def get_workflow_evaluations(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作流的评估意见"""
    
    evaluations = db.query(Evaluation).filter(
        Evaluation.workflow_id == workflow_id
    ).order_by(desc(Evaluation.created_at)).all()
    
    return [
        EvaluationResponse(
            evaluate_id=e.evaluate_id,
            workflow_id=e.workflow_id,
            evaluator_name=e.evaluator.full_name,
            score=e.score,
            comment=e.comment,
            evaluation_file=e.evaluation_file,  # 使用统一的字段名
            created_at=e.created_at,
            updated_at=e.updated_at
        ) for e in evaluations
    ]

@router.get("/evaluations", response_model=List[EvaluationResponse])
async def get_user_evaluations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的评估历史"""
    
    # 根据用户角色返回不同的评估记录
    if current_user.role.role_key == 'evaluator':
        # 评估专家看到自己的评估记录
        evaluations = db.query(Evaluation).filter(
            Evaluation.evaluator_id == current_user.user_id
        ).order_by(desc(Evaluation.created_at)).all()
    elif current_user.role.role_key == 'admin':
        # 管理员看到所有评估记录
        evaluations = db.query(Evaluation).order_by(desc(Evaluation.created_at)).all()
    else:
        # 修复专家看到自己工作流的评估记录
        evaluations = db.query(Evaluation).join(Workflow).filter(
            Workflow.initiator_id == current_user.user_id
        ).order_by(desc(Evaluation.created_at)).all()
    
    return [
        EvaluationResponse(
            evaluate_id=e.evaluate_id,
            workflow_id=e.workflow_id,
            evaluator_name=e.evaluator.full_name,
            score=e.score,
            comment=e.comment,
            evaluation_file=e.evaluation_file,
            created_at=e.created_at,
            updated_at=e.updated_at
        ) for e in evaluations
    ]

@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation_detail(
    evaluation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取评估详情"""
    
    evaluation = db.query(Evaluation).filter(
        Evaluation.evaluate_id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="评估记录不存在")
    
    # 权限检查：只有评估人、工作流发起人或管理员可以查看详情
    workflow = db.query(Workflow).filter(
        Workflow.workflow_id == evaluation.workflow_id
    ).first()
    
    if (current_user.role.role_key != 'admin' and 
        evaluation.evaluator_id != current_user.user_id and
        (not workflow or workflow.initiator_id != current_user.user_id)):
        raise HTTPException(status_code=403, detail="无权限查看此评估详情")
    
    return EvaluationResponse(
        evaluate_id=evaluation.evaluate_id,
        workflow_id=evaluation.workflow_id,
        evaluator_name=evaluation.evaluator.full_name,
        score=evaluation.score,
        comment=evaluation.comment,
        evaluation_file=evaluation.evaluation_file,
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at
    )

# 回溯申请API
@router.post("/rollback-requests", response_model=RollbackRequestResponse)
async def create_rollback_request(
    workflow_id: str = FormField(...),
    target_form_id: str = FormField(...),
    reason: str = FormField(...),
    support_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_restorer),
    db: Session = Depends(get_db)
):
    """创建回溯申请"""
    
    # 转换UUID
    try:
        workflow_uuid = UUID(workflow_id)
        target_form_uuid = UUID(target_form_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的ID格式")
    
    # 处理支撑文件上传
    support_file_url = None
    if support_file:
        try:
            file_content = await support_file.read()
            support_file_url = file_service.upload_file(
                file_content=file_content,
                filename=support_file.filename,
                content_type=support_file.content_type
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    
    # 检查工作流权限
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_uuid).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    if (current_user.role.role_key != 'admin' and 
        workflow.initiator_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="无权限申请回溯此工作流")
    
    # 检查目标表单
    target_form = db.query(Form).filter(
        Form.form_id == target_form_uuid,
        Form.workflow_id == workflow_uuid
    ).first()
    if not target_form:
        raise HTTPException(status_code=404, detail="目标表单不存在")
    
    rollback_request = RollbackRequest(
        workflow_id=workflow_uuid,
        requester_id=current_user.user_id,
        target_form_id=target_form_uuid,
        reason=reason,
        support_file_url=support_file_url,
        status='pending'
    )
    
    db.add(rollback_request)
    db.commit()
    db.refresh(rollback_request)
    
    return RollbackRequestResponse(
        rollback_id=rollback_request.rollback_id,
        workflow_id=rollback_request.workflow_id,
        requester_name=rollback_request.requester.full_name,
        target_form_id=rollback_request.target_form_id,
        reason=rollback_request.reason,
        support_file_url=rollback_request.support_file_url,
        status=rollback_request.status,
        approver_name=None,
        approved_at=rollback_request.approved_at,
        created_at=rollback_request.created_at
    )

@router.post("/rollback-requests/{rollback_id}/approve")
async def approve_rollback_request(
    rollback_id: int,
    approve: bool = FormField(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """审批回溯申请"""
    
    rollback_request = db.query(RollbackRequest).filter(
        RollbackRequest.rollback_id == rollback_id,
        RollbackRequest.status == 'pending'
    ).first()
    if not rollback_request:
        raise HTTPException(status_code=404, detail="回溯申请不存在或已处理")
    
    if approve:
        rollback_request.status = 'approved'
        
        # 如果批准，创建回溯表单的副本
        original_form = db.query(Form).filter(
            Form.form_id == rollback_request.target_form_id
        ).first()
        
        if original_form:
            # 获取新的步骤号
            max_step = db.query(func.max(Form.step_no)).filter(
                Form.workflow_id == rollback_request.workflow_id
            ).scalar()
            new_step = (max_step or 0) + 1
            
            # 创建回溯表单
            new_form = Form(
                workflow_id=rollback_request.workflow_id,
                step_no=new_step,
                submitter_id=rollback_request.requester_id,
                image_url=original_form.image_url,
                image_meta=original_form.image_meta,
                image_desc=original_form.image_desc,
                image_desc_file=original_form.image_desc_file,
                restoration_opinion=original_form.restoration_opinion,
                opinion_tags=original_form.opinion_tags,
                opinion_file=original_form.opinion_file,
                remark=original_form.remark,
                attachment=original_form.attachment,
                is_rollback_from=original_form.form_id
            )
            db.add(new_form)
            
            # 更新工作流状态
            workflow = db.query(Workflow).filter(
                Workflow.workflow_id == rollback_request.workflow_id
            ).first()
            if workflow:
                workflow.current_step = new_step
                workflow.status = 'running'
                workflow.is_finalized = False
                workflow.updated_at = func.now()
            
            # 先提交新表单以获取form_id
            db.commit()
            db.refresh(new_form)
            
            # 记录操作日志
            log = StepLog(
                form_id=new_form.form_id,
                action='rollback',
                operator_id=current_user.user_id,
                comment=f"回溯到表单{rollback_request.target_form_id}"
            )
            db.add(log)
    else:
        rollback_request.status = 'rejected'
    
    rollback_request.approver_id = current_user.user_id
    rollback_request.approved_at = func.now()
    
    db.commit()
    
    return ResponseModel(
        success=True,
        message="回溯申请已处理",
        data={"rollback_id": rollback_id, "approved": approve}
    )

@router.get("/rollback-requests", response_model=List[RollbackRequestResponse])
async def get_rollback_requests(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取回溯申请列表"""
    
    query = db.query(RollbackRequest)
    
    # 根据角色过滤
    if current_user.role.role_key == 'restorer':
        query = query.filter(RollbackRequest.requester_id == current_user.user_id)
    
    if status:
        query = query.filter(RollbackRequest.status == status)
    
    requests = query.order_by(desc(RollbackRequest.created_at)).all()
    
    return [
        RollbackRequestResponse(
            rollback_id=r.rollback_id,
            workflow_id=r.workflow_id,
            requester_name=r.requester.full_name,
            target_form_id=r.target_form_id,
            reason=r.reason,
            support_file_url=r.support_file_url,
            status=r.status,
            approver_name=r.approver.full_name if r.approver else None,
            approved_at=r.approved_at,
            created_at=r.created_at
        ) for r in requests
    ]

@router.get("/rollback-requests/{rollback_id}", response_model=RollbackRequestResponse)
async def get_rollback_request_detail(
    rollback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取回溯申请详情"""
    
    rollback_request = db.query(RollbackRequest).filter(
        RollbackRequest.rollback_id == rollback_id
    ).first()
    
    if not rollback_request:
        raise HTTPException(status_code=404, detail="回溯申请不存在")
    
    # 权限检查：只有申请人、审批人或管理员可以查看详情
    if (current_user.role.role_key != 'admin' and 
        rollback_request.requester_id != current_user.user_id and
        rollback_request.approver_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="无权限查看此申请详情")
    
    return RollbackRequestResponse(
        rollback_id=rollback_request.rollback_id,
        workflow_id=rollback_request.workflow_id,
        requester_name=rollback_request.requester.full_name,
        target_form_id=rollback_request.target_form_id,
        reason=rollback_request.reason,
        support_file_url=rollback_request.support_file_url,
        status=rollback_request.status,
        approver_name=rollback_request.approver.full_name if rollback_request.approver else None,
        approved_at=rollback_request.approved_at,
        created_at=rollback_request.created_at
    )

# 管理员表单管理API
@router.get("/admin/forms", response_model=List[FormResponse])
async def admin_get_all_forms(
    workflow_id: Optional[UUID] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员获取所有表单列表"""
    query = db.query(Form)
    
    if workflow_id:
        query = query.filter(Form.workflow_id == workflow_id)
    
    forms = query.order_by(desc(Form.created_at)).all()
    
    return [
        FormResponse(
            form_id=f.form_id,
            workflow_id=f.workflow_id,
            step_no=f.step_no,
            submitter_name=f.submitter.full_name,
            image_url=f.image_url,
            image_meta=f.image_meta,
            image_desc=f.image_desc,
            image_desc_file=f.image_desc_file,
            restoration_opinion=f.restoration_opinion,
            opinion_tags=f.opinion_tags,
            opinion_file=f.opinion_file,
            remark=f.remark,
            attachment=f.attachment,
            created_at=f.created_at
        ) for f in forms
    ]

@router.put("/admin/forms/{form_id}", response_model=FormResponse)
async def admin_update_form(
    form_id: UUID,
    image_desc: Optional[str] = FormField(None),
    restoration_opinion: Optional[str] = FormField(None),
    opinion_tags: Optional[str] = FormField(None),
    remark: Optional[str] = FormField(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员更新表单"""
    form = db.query(Form).filter(Form.form_id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="表单不存在")
    
    # 更新字段
    if image_desc is not None:
        form.image_desc = image_desc
    if restoration_opinion is not None:
        form.restoration_opinion = restoration_opinion
    if opinion_tags is not None:
        form.opinion_tags = opinion_tags
    if remark is not None:
        form.remark = remark
    
    form.updated_at = func.now()
    
    # 记录操作日志
    log = StepLog(
        form_id=form_id,
        action='admin_update',
        operator_id=current_user.user_id,
        comment="管理员更新表单"
    )
    db.add(log)
    
    db.commit()
    db.refresh(form)
    
    return FormResponse(
        form_id=form.form_id,
        workflow_id=form.workflow_id,
        step_no=form.step_no,
        submitter_name=form.submitter.full_name,
        image_url=form.image_url,
        image_meta=form.image_meta,
        image_desc=form.image_desc,
        image_desc_file=form.image_desc_file,
        restoration_opinion=form.restoration_opinion,
        opinion_tags=form.opinion_tags,
        opinion_file=form.opinion_file,
        remark=form.remark,
        attachment=form.attachment,
        created_at=form.created_at
    )

@router.delete("/admin/forms/{form_id}")
async def admin_delete_form(
    form_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员删除表单"""
    form = db.query(Form).filter(Form.form_id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="表单不存在")
    
    # 检查是否是工作流的最后一个表单
    form_count = db.query(Form).filter(Form.workflow_id == form.workflow_id).count()
    if form_count == 1:
        raise HTTPException(status_code=400, detail="无法删除工作流的唯一表单")
    
    # 删除相关的操作日志
    db.query(StepLog).filter(StepLog.form_id == form_id).delete()
    
    # 记录删除操作日志（在删除表单之前）
    log = StepLog(
        form_id=form_id,
        action='admin_delete',
        operator_id=current_user.user_id,
        comment="管理员删除表单"
    )
    db.add(log)
    db.commit()  # 先提交日志
    
    # 删除表单
    db.delete(form)
    db.commit()
    
    return ResponseModel(
        success=True,
        message="表单已删除",
        data={"form_id": str(form_id)}
    )

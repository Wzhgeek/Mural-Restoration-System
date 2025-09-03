/**
 * 修复提交相关API
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import request from './request'

// 获取工作流列表
export const getWorkflows = () => {
  return request.get('/api/workflows')
}

// 创建工作流
export const createWorkflow = (data) => {
  return request.post('/api/workflows', data)
}

// 获取工作流表单
export const getWorkflowForms = (workflowId) => {
  return request.get(`/api/workflows/${workflowId}/forms`)
}

// 获取工作流评估
export const getWorkflowEvaluations = (workflowId) => {
  return request.get(`/api/workflows/${workflowId}/evaluations`)
}

// 提交修复表单
export const submitForm = (formData) => {
  return request.post('/api/forms', formData)
}

// 申请回溯
export const requestRollback = (data) => {
  return request.post('/api/rollback-requests', data)
}

// 设为最终方案
export const finalizeWorkflow = (workflowId, data) => {
  return request.post(`/api/workflows/${workflowId}/finalize`, data)
}

// 提交评估
export const submitEvaluation = (data) => {
  return request.post('/api/evaluations', data)
}

// 获取保密协议
export const getPrivacyAgreement = () => {
  return request.get('/api/privacy-agreement')
}

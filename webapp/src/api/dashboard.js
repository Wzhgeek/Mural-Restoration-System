/**
 * 仪表盘API服务
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import request from './request.js'

/**
 * 获取仪表盘数据
 * @returns {Promise<Object>} 仪表盘数据
 */
export const getDashboardData = async () => {
  return request('/dashboard')
}

/**
 * 获取工作流列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Array>} 工作流列表
 */
export const getWorkflows = async (params = {}) => {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `/workflows?${queryString}` : '/workflows'
  return request(url)
}

/**
 * 获取评估列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Array>} 评估列表
 */
export const getEvaluations = async (params = {}) => {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `/evaluations?${queryString}` : '/evaluations'
  return request(url)
}

/**
 * 获取回溯申请列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Array>} 回溯申请列表
 */
export const getRollbackRequests = async (params = {}) => {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `/rollback-requests?${queryString}` : '/rollback-requests'
  return request(url)
}

/**
 * 获取用户信息
 * @returns {Promise<Object>} 用户信息
 */
export const getUserInfo = async () => {
  return request('/user/me')
}

/**
 * 创建工作流
 * @param {Object} data - 工作流数据
 * @returns {Promise<Object>} 创建结果
 */
export const createWorkflow = async (data) => {
  return request('/workflows', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

/**
 * 提交表单
 * @param {FormData} formData - 表单数据
 * @returns {Promise<Object>} 提交结果
 */
export const submitForm = async (formData) => {
  return request({
    url: '/forms',
    method: 'POST',
    data: formData
  })
}

/**
 * 提交评估
 * @param {FormData} formData - 评估数据
 * @returns {Promise<Object>} 提交结果
 */
export const submitEvaluation = async (formData) => {
  return request({
    url: '/evaluations',
    method: 'POST',
    data: formData
  })
}

/**
 * 提交回溯申请
 * @param {FormData} formData - 回溯申请数据
 * @returns {Promise<Object>} 提交结果
 */
export const submitRollbackRequest = async (formData) => {
  return request({
    url: '/rollback-requests',
    method: 'POST',
    data: formData
  })
}

/**
 * 审批回溯申请
 * @param {number} rollbackId - 回溯申请ID
 * @param {boolean} approve - 是否批准
 * @returns {Promise<Object>} 审批结果
 */
export const approveRollbackRequest = async (rollbackId, approve) => {
  return request({
    url: `/rollback-requests/${rollbackId}/approve`,
    method: 'POST',
    data: { approve }
  })
}

/**
 * 设为最终方案
 * @param {number} workflowId - 工作流ID
 * @param {number} formId - 表单ID
 * @returns {Promise<Object>} 操作结果
 */
export const finalizeWorkflow = async (workflowId, formId) => {
  return request({
    url: `/workflows/${workflowId}/finalize`,
    method: 'POST',
    data: { final_form_id: formId }
  })
}

/**
 * 获取工作流详情
 * @param {number} workflowId - 工作流ID
 * @returns {Promise<Object>} 工作流详情
 */
export const getWorkflowDetails = async (workflowId) => {
  const [forms, evaluations] = await Promise.all([
    request(`/workflows/${workflowId}/forms`),
    request(`/workflows/${workflowId}/evaluations`)
  ])
  
  return {
    forms,
    evaluations
  }
}

/**
 * 更新用户信息
 * @param {Object} data - 用户数据
 * @returns {Promise<Object>} 更新结果
 */
export const updateUserProfile = async (data) => {
  return request('/user/profile', {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

/**
 * 修改密码
 * @param {Object} data - 密码数据
 * @returns {Promise<Object>} 修改结果
 */
export const changePassword = async (data) => {
  return request('/user/password', {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

/**
 * 删除工作流（仅管理员）
 * @param {number} workflowId - 工作流ID
 * @returns {Promise<Object>} 删除结果
 */
export const deleteWorkflow = async (workflowId) => {
  return request(`/admin/workflows/${workflowId}`, {
    method: 'DELETE'
  })
}

/**
 * 删除评估记录（仅管理员）
 * @param {number} evaluationId - 评估ID
 * @returns {Promise<Object>} 删除结果
 */
export const deleteEvaluation = async (evaluationId) => {
  return request(`/admin/evaluations/${evaluationId}`, {
    method: 'DELETE'
  })
}

/**
 * 删除回溯申请（仅管理员）
 * @param {number} rollbackId - 回溯申请ID
 * @returns {Promise<Object>} 删除结果
 */
export const deleteRollbackRequest = async (rollbackId) => {
  return request(`/admin/rollback-requests/${rollbackId}`, {
    method: 'DELETE'
  })
}

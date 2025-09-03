/**
 * 评估历史相关API接口
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import request from './request.js'

/**
 * 获取待评估的工作流列表
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 工作流状态筛选
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise} 待评估工作流数据
 */
export const getEvaluationWorkflows = (params = {}) => {
  return request({
    url: '/api/evaluation/workflows',
    method: 'GET',
    params: {
      search: params.search || '',
      status: params.status || '',
      page: params.page || 1,
      limit: params.limit || 20
    }
  })
}

/**
 * 获取评估历史列表
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 评估状态筛选
 * @param {string} params.score_range - 分数范围筛选
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise} 评估历史数据
 */
export const getEvaluationHistory = (params = {}) => {
  return request({
    url: '/api/evaluation/history',
    method: 'GET',
    params: {
      search: params.search || '',
      status: params.status || '',
      score_range: params.score_range || '',
      page: params.page || 1,
      limit: params.limit || 20
    }
  })
}

/**
 * 获取评估历史详情
 * @param {number} evaluationId - 评估ID
 * @returns {Promise} 评估详情数据
 */
export const getEvaluationDetail = (evaluationId) => {
  return request({
    url: `/api/evaluation/${evaluationId}`,
    method: 'GET'
  })
}

/**
 * 删除评估记录（仅管理员）
 * @param {number} evaluationId - 评估ID
 * @returns {Promise} 删除结果
 */
export const deleteEvaluation = (evaluationId) => {
  return request({
    url: `/api/admin/evaluation/${evaluationId}`,
    method: 'DELETE'
  })
}

/**
 * 批量删除评估记录（仅管理员）
 * @param {Array} evaluationIds - 评估ID数组
 * @returns {Promise} 删除结果
 */
export const batchDeleteEvaluations = (evaluationIds) => {
  return request({
    url: '/api/admin/evaluation/batch-delete',
    method: 'POST',
    data: { evaluation_ids: evaluationIds }
  })
}

/**
 * 获取工作流详情（包含表单和评估记录）
 * @param {number} workflowId - 工作流ID
 * @returns {Promise} 工作流详情数据
 */
export const getWorkflowDetail = (workflowId) => {
  return request({
    url: `/api/workflows/${workflowId}/detail`,
    method: 'GET'
  })
}

/**
 * 提交评估
 * @param {Object} evaluationData - 评估数据
 * @param {number} evaluationData.workflow_id - 工作流ID
 * @param {number} evaluationData.score - 评分
 * @param {string} evaluationData.content - 评估内容
 * @param {string} evaluationData.comment - 专家意见
 * @returns {Promise} 提交结果
 */
export const submitEvaluation = (evaluationData) => {
  return request({
    url: '/api/evaluation/submit',
    method: 'POST',
    data: evaluationData
  })
}

/**
 * 删除工作流（仅管理员）
 * @param {number} workflowId - 工作流ID
 * @returns {Promise} 删除结果
 */
export const deleteWorkflow = (workflowId) => {
  return request({
    url: `/api/admin/workflows/${workflowId}`,
    method: 'DELETE'
  })
}

/**
 * 批量删除工作流（仅管理员）
 * @param {Array} workflowIds - 工作流ID数组
 * @returns {Promise} 删除结果
 */
export const batchDeleteWorkflows = (workflowIds) => {
  return request({
    url: '/api/admin/workflows/batch-delete',
    method: 'POST',
    data: { workflow_ids: workflowIds }
  })
}

/**
 * 获取评估统计数据
 * @returns {Promise} 统计数据
 */
export const getEvaluationStats = () => {
  return request({
    url: '/api/evaluation/stats',
    method: 'GET'
  })
}

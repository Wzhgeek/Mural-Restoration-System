/**
 * 历史记录相关API接口
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import request from './request.js'

/**
 * 获取评估历史列表
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词
 * @param {string} params.score_range - 分数范围筛选
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise} 评估历史数据
 */
export const getEvaluationHistory = (params = {}) => {
  return request({
    url: '/evaluations',
    method: 'GET',
    params: {
      search: params.search || '',
      score_range: params.score_range || '',
      page: params.page || 1,
      limit: params.limit || 20
    }
  })
}

/**
 * 获取回溯历史列表
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 状态筛选
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise} 回溯历史数据
 */
export const getRollbackHistory = (params = {}) => {
  return request({
    url: '/rollback-requests',
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
 * 获取评估历史详情
 * @param {number} evaluationId - 评估ID
 * @returns {Promise} 评估详情数据
 */
export const getEvaluationDetail = (evaluationId) => {
  return request({
    url: `/evaluations/${evaluationId}`,
    method: 'GET'
  })
}

/**
 * 获取回溯申请详情
 * @param {number} rollbackId - 回溯申请ID
 * @returns {Promise} 回溯申请详情数据
 */
export const getRollbackDetail = (rollbackId) => {
  return request({
    url: `/rollback-requests/${rollbackId}`,
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
    url: `/admin/evaluations/${evaluationId}`,
    method: 'DELETE'
  })
}

/**
 * 删除回溯申请（仅管理员）
 * @param {number} rollbackId - 回溯申请ID
 * @returns {Promise} 删除结果
 */
export const deleteRollbackRequest = (rollbackId) => {
  return request({
    url: `/admin/rollback-requests/${rollbackId}`,
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
    url: '/admin/evaluations/batch-delete',
    method: 'POST',
    data: { evaluation_ids: evaluationIds }
  })
}

/**
 * 批量删除回溯申请（仅管理员）
 * @param {Array} rollbackIds - 回溯申请ID数组
 * @returns {Promise} 删除结果
 */
export const batchDeleteRollbackRequests = (rollbackIds) => {
  return request({
    url: '/admin/rollback-requests/batch-delete',
    method: 'POST',
    data: { rollback_ids: rollbackIds }
  })
}

/**
 * 回溯历史相关API接口
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import request from './request.js'

/**
 * 获取回溯历史列表
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 回溯状态筛选
 * @param {string} params.date_range - 时间范围筛选
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
      date_range: params.date_range || '',
      page: params.page || 1,
      limit: params.limit || 20
    }
  })
}

/**
 * 获取回溯历史详情
 * @param {number} rollbackId - 回溯ID
 * @returns {Promise} 回溯详情数据
 */
export const getRollbackDetail = (rollbackId) => {
  return request({
    url: `/rollback-requests/${rollbackId}`,
    method: 'GET'
  })
}

/**
 * 删除回溯记录（普通用户）
 * @param {number} rollbackId - 回溯ID
 * @returns {Promise} 删除结果
 */
export const deleteRollback = (rollbackId) => {
  return request({
    url: `/rollback-requests/${rollbackId}`,
    method: 'DELETE'
  })
}

/**
 * 管理员强制删除回溯记录
 * @param {number} rollbackId - 回溯ID
 * @returns {Promise} 删除结果
 */
export const adminDeleteRollback = (rollbackId) => {
  return request({
    url: `/admin/rollback-requests/${rollbackId}`,
    method: 'DELETE'
  })
}

/**
 * 批量删除回溯记录（仅管理员）
 * @param {Array} rollbackIds - 回溯ID数组
 * @returns {Promise} 删除结果
 */
export const batchDeleteRollbacks = (rollbackIds) => {
  return request({
    url: '/admin/rollback-requests/batch-delete',
    method: 'POST',
    data: { ids: rollbackIds }
  })
}

/**
 * 审批回溯申请（仅管理员）
 * @param {number} rollbackId - 回溯ID
 * @param {string} action - 审批动作 ('approved' | 'rejected')
 * @param {string} comment - 审批意见
 * @returns {Promise} 审批结果
 */
export const approveRollback = (rollbackId, action, comment = '') => {
  return request({
    url: `/rollback-requests/${rollbackId}/approve`,
    method: 'POST',
    data: {
      approve: action === 'approved',
      comment: comment
    }
  })
}

/**
 * 获取回溯统计数据
 * @returns {Promise} 统计数据
 * 返回格式: {
 *   total_requests: number,      // 总申请数
 *   pending_requests: number,    // 待审批数
 *   approved_requests: number,   // 已批准数
 *   rejected_requests: number,   // 已拒绝数
 *   approval_rate: number        // 批准率（已批准/已处理*100）
 * }
 */
export const getRollbackStats = () => {
  return request({
    url: '/rollback-requests/stats',
    method: 'GET'
  })
}

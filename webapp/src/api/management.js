/**
 * 修复管理相关API接口
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import request from './request.js'

/**
 * 获取所有工作流列表
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 工作流状态筛选
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise} 工作流数据
 */
export const getAllWorkflows = (params = {}) => {
  return request({
    url: '/api/workflows/paginated',
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
 * 获取回溯申请列表
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 申请状态筛选
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise} 回溯申请数据
 */
export const getRollbackRequests = (params = {}) => {
  return request({
    url: '/api/rollback-requests',
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
 * 删除工作流（仅管理员）
 * @param {string} workflowId - 工作流ID
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
    data: { ids: workflowIds }
  })
}

/**
 * 审批回溯申请（仅管理员）
 * @param {number} rollbackId - 回溯申请ID
 * @param {string} action - 审批动作 ('approved' | 'rejected')
 * @param {string} comment - 审批意见
 * @returns {Promise} 审批结果
 */
export const approveRollback = (rollbackId, action, comment = '') => {
  return request({
    url: `/api/rollback-requests/${rollbackId}/approve`,
    method: 'POST',
    data: {
      approve: action === 'approved',
      comment: comment
    }
  })
}

/**
 * 删除回溯申请（仅管理员）
 * @param {number} rollbackId - 回溯申请ID
 * @returns {Promise} 删除结果
 */
export const deleteRollback = (rollbackId) => {
  return request({
    url: `/api/admin/rollback-requests/${rollbackId}`,
    method: 'DELETE'
  })
}

/**
 * 批量删除回溯申请（仅管理员）
 * @param {Array} rollbackIds - 回溯申请ID数组
 * @returns {Promise} 删除结果
 */
export const batchDeleteRollbacks = (rollbackIds) => {
  return request({
    url: '/api/admin/rollback-requests/batch-delete',
    method: 'POST',
    data: { ids: rollbackIds }
  })
}

/**
 * 获取管理统计数据（仅管理员）
 * @returns {Promise} 统计数据
 */
export const getManagementStats = () => {
  return request({
    url: '/api/dashboard',
    method: 'GET'
  })
}

/**
 * 获取用户列表（仅管理员）
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词
 * @param {string} params.role - 角色筛选
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise} 用户列表数据
 */
export const getUsers = (params = {}) => {
  return request({
    url: '/api/admin/users',
    method: 'GET',
    params: {
      search: params.search || '',
      role: params.role || '',
      page: params.page || 1,
      limit: params.limit || 20
    }
  })
}

/**
 * 更新用户角色（仅管理员）
 * @param {number} userId - 用户ID
 * @param {string} role - 新角色
 * @returns {Promise} 更新结果
 */
export const updateUserRole = (userId, role) => {
  return request({
    url: `/api/admin/users/${userId}/role`,
    method: 'PUT',
    data: { role: role }
  })
}

/**
 * 删除用户（仅管理员）
 * @param {number} userId - 用户ID
 * @returns {Promise} 删除结果
 */
export const deleteUser = (userId) => {
  return request({
    url: `/api/admin/users/${userId}`,
    method: 'DELETE'
  })
}

/**
 * 获取系统日志（仅管理员）
 * @param {Object} params - 查询参数
 * @param {string} params.level - 日志级别
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise} 系统日志数据
 */
export const getSystemLogs = (params = {}) => {
  return request({
    url: '/api/admin/logs',
    method: 'GET',
    params: {
      level: params.level || '',
      start_date: params.start_date || '',
      end_date: params.end_date || '',
      page: params.page || 1,
      limit: params.limit || 50
    }
  })
}

/**
 * 导出数据（仅管理员）
 * @param {string} dataType - 数据类型 ('workflows' | 'users' | 'logs')
 * @param {Object} filters - 筛选条件
 * @returns {Promise} 导出结果
 */
export const exportData = (dataType, filters = {}) => {
  return request({
    url: '/api/admin/export',
    method: 'POST',
    data: {
      data_type: dataType,
      filters: filters
    }
  })
}

/**
 * 获取系统配置（仅管理员）
 * @returns {Promise} 系统配置数据
 */
export const getSystemConfig = () => {
  return request({
    url: '/api/admin/config',
    method: 'GET'
  })
}

/**
 * 更新系统配置（仅管理员）
 * @param {Object} config - 配置数据
 * @returns {Promise} 更新结果
 */
export const updateSystemConfig = (config) => {
  return request({
    url: '/api/admin/config',
    method: 'PUT',
    data: config
  })
}

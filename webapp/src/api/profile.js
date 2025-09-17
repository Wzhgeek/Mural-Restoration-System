/**
 * 个人信息相关API接口
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import request from './request.js'

/**
 * 获取当前用户信息
 * @returns {Promise} 用户信息数据
 */
export const getUserProfile = () => {
  return request({
    url: '/user/me',
    method: 'GET'
  })
}

/**
 * 更新用户信息
 * @param {Object} userData - 用户更新数据
 * @param {string} userData.full_name - 姓名
 * @param {string} userData.email - 邮箱
 * @param {string} userData.phone - 联系电话
 * @returns {Promise} 更新结果
 */
export const updateUserProfile = (userData) => {
  return request({
    url: '/user/profile',
    method: 'PUT',
    params: userData  // 使用params而不是data，因为后端期望查询参数
  })
}

/**
 * 修改密码
 * @param {Object} passwordData - 密码数据
 * @param {string} passwordData.current_password - 当前密码
 * @param {string} passwordData.new_password - 新密码
 * @returns {Promise} 修改结果
 */
export const changePassword = (passwordData) => {
  return request({
    url: '/user/password',
    method: 'PUT',
    params: {
      current_password: passwordData.current_password,
      new_password: passwordData.new_password
    }
  })
}

/**
 * 获取账户统计信息（通过仪表板接口获取）
 * @returns {Promise} 统计数据
 */
export const getAccountStats = () => {
  return request({
    url: '/dashboard',
    method: 'GET'
  })
}

/**
 * 上传用户头像
 * @param {FormData} formData - 包含头像文件的表单数据
 * @returns {Promise} 上传结果
 */
export const uploadAvatar = (formData) => {
  return request({
    url: '/user/avatar',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取用户偏好设置
 * @returns {Promise} 用户偏好设置
 */
export const getUserPreferences = () => {
  return request({
    url: '/user/preferences',
    method: 'GET'
  })
}

/**
 * 更新用户偏好设置
 * @param {Object} preferences - 偏好设置数据
 * @returns {Promise} 更新结果
 */
export const updateUserPreferences = (preferences) => {
  return request({
    url: '/user/preferences',
    method: 'PUT',
    data: preferences
  })
}

/**
 * 获取用户活动日志
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @returns {Promise} 活动日志数据
 */
export const getUserActivityLog = (params = {}) => {
  return request({
    url: '/user/activity-log',
    method: 'GET',
    params: {
      page: params.page || 1,
      limit: params.limit || 20,
      start_date: params.start_date || '',
      end_date: params.end_date || ''
    }
  })
}

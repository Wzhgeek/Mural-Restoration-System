/**
 * HTTP请求工具
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import axios from 'axios'
import { MessagePlugin } from 'tdesign-vue-next'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 如果是FormData，不设置Content-Type，让浏览器自动设置
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response.data || response
  },
  (error) => {
    console.error('响应错误:', error)
    
    // 处理HTTP错误状态码
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          MessagePlugin.error('登录已过期，请重新登录')
          localStorage.removeItem('authToken')
          localStorage.removeItem('currentUser')
          window.location.href = '/login'
          break
        case 403:
          MessagePlugin.error('没有权限访问此资源')
          break
        case 404:
          MessagePlugin.error('请求的资源不存在')
          break
        case 422:
          // 422错误由具体组件处理，这里不显示通用错误消息
          break
        case 500:
          MessagePlugin.error('服务器内部错误')
          break
        default:
          MessagePlugin.error(data?.detail || data?.message || '请求失败')
      }
    } else if (error.request) {
      MessagePlugin.error('网络连接失败，请检查网络设置')
    } else {
      MessagePlugin.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default request

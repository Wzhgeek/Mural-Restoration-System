/**
 * 本地存储管理工具
 * 用于管理localStorage的配额和清理
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import { MessagePlugin } from 'tdesign-vue-next'

class StorageManager {
  constructor() {
    this.maxSize = 2 * 1024 * 1024 // 2MB 单个数据项最大大小
    this.maxAge = 24 * 60 * 60 * 1000 // 24小时 数据最大保存时间
    this.cleanupThreshold = 0.8 // 当存储使用率达到80%时开始清理
  }

  /**
   * 安全地保存数据到localStorage
   * @param {string} key 存储键
   * @param {any} data 要存储的数据
   * @param {boolean} showWarning 是否显示警告信息
   * @returns {boolean} 是否保存成功
   */
  setItem(key, data, showWarning = true) {
    try {
      // 检查数据大小
      const dataString = JSON.stringify(data)
      const dataSize = new Blob([dataString]).size
      
      if (dataSize > this.maxSize) {
        console.warn(`数据过大 (${(dataSize / 1024).toFixed(2)}KB)，跳过保存:`, key)
        if (showWarning) {
          MessagePlugin.warning('数据过大，无法保存到本地存储')
        }
        return false
      }

      // 检查存储空间
      if (!this.checkStorageSpace()) {
        console.warn('存储空间不足，开始清理...')
        this.cleanupStorage()
      }

      // 尝试保存
      localStorage.setItem(key, dataString)
      console.log(`数据已保存: ${key}, 大小: ${(dataSize / 1024).toFixed(2)}KB`)
      return true

    } catch (error) {
      if (error.name === 'QuotaExceededError') {
        console.warn('localStorage配额超限，开始清理...')
        this.forceCleanup()
        
        try {
          // 重试保存
          localStorage.setItem(key, JSON.stringify(data))
          console.log('重试保存成功:', key)
          return true
        } catch (retryError) {
          console.error('重试保存失败:', retryError)
          if (showWarning) {
            MessagePlugin.warning('数据保存失败，但不会影响当前操作')
          }
          return false
        }
      } else {
        console.error('保存到localStorage失败:', error)
        if (showWarning) {
          MessagePlugin.warning('数据保存失败，但不会影响当前操作')
        }
        return false
      }
    }
  }

  /**
   * 从localStorage获取数据
   * @param {string} key 存储键
   * @returns {any|null} 存储的数据或null
   */
  getItem(key) {
    try {
      const data = localStorage.getItem(key)
      if (data) {
        const parsed = JSON.parse(data)
        
        // 检查数据是否过期
        if (parsed.timestamp && (Date.now() - parsed.timestamp) > this.maxAge) {
          localStorage.removeItem(key)
          console.log('数据已过期，已清理:', key)
          return null
        }
        
        return parsed
      }
      return null
    } catch (error) {
      console.error('从localStorage获取数据失败:', error)
      localStorage.removeItem(key) // 清理损坏的数据
      return null
    }
  }

  /**
   * 从localStorage删除数据
   * @param {string} key 存储键
   */
  removeItem(key) {
    try {
      localStorage.removeItem(key)
      console.log('数据已删除:', key)
    } catch (error) {
      console.error('删除localStorage数据失败:', error)
    }
  }

  /**
   * 检查存储空间是否可用
   * @returns {boolean} 是否有可用空间
   */
  checkStorageSpace() {
    try {
      const testKey = 'storage_test_' + Date.now()
      const testData = 'test'
      localStorage.setItem(testKey, testData)
      localStorage.removeItem(testKey)
      return true
    } catch (error) {
      return false
    }
  }

  /**
   * 获取存储使用情况
   * @returns {object} 存储使用统计
   */
  getStorageUsage() {
    let totalSize = 0
    let itemCount = 0
    const appItems = []
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key) {
        const value = localStorage.getItem(key)
        const itemSize = key.length + value.length
        totalSize += itemSize
        itemCount++
        
        // 统计应用相关的数据项
        if (key.startsWith('restoration_flow_') || 
            key.startsWith('workflow_submitted_') ||
            key.startsWith('currentUser') ||
            key.startsWith('auth_')) {
          appItems.push({
            key,
            size: itemSize,
            sizeKB: (itemSize / 1024).toFixed(2)
          })
        }
      }
    }
    
    return {
      totalSize,
      itemCount,
      totalSizeKB: (totalSize / 1024).toFixed(2),
      totalSizeMB: (totalSize / (1024 * 1024)).toFixed(2),
      appItems,
      appItemsCount: appItems.length,
      appItemsSize: appItems.reduce((sum, item) => sum + item.size, 0),
      appItemsSizeKB: (appItems.reduce((sum, item) => sum + item.size, 0) / 1024).toFixed(2)
    }
  }

  /**
   * 清理过期的存储数据
   */
  cleanupStorage() {
    const now = Date.now()
    let cleanedCount = 0
    
    console.log('开始清理过期的localStorage数据...')
    
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i)
      if (key && (key.startsWith('restoration_flow_') || key.startsWith('workflow_submitted_'))) {
        try {
          const data = JSON.parse(localStorage.getItem(key))
          if (data.timestamp && (now - data.timestamp) > this.maxAge) {
            localStorage.removeItem(key)
            cleanedCount++
            console.log('清理过期数据:', key)
          }
        } catch (error) {
          // 如果解析失败，直接删除
          localStorage.removeItem(key)
          cleanedCount++
          console.log('清理无效数据:', key)
        }
      }
    }
    
    console.log(`清理完成，共清理 ${cleanedCount} 个数据项`)
  }

  /**
   * 强制清理所有应用相关数据
   */
  forceCleanup() {
    console.log('开始强制清理localStorage...')
    
    const keysToRemove = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && (key.startsWith('restoration_flow_') || 
                  key.startsWith('workflow_submitted_') ||
                  key.startsWith('auth_'))) {
        keysToRemove.push(key)
      }
    }
    
    keysToRemove.forEach(key => {
      localStorage.removeItem(key)
      console.log('清理数据:', key)
    })
    
    console.log(`强制清理完成，共清理 ${keysToRemove.length} 个数据项`)
  }

  /**
   * 清理指定前缀的数据
   * @param {string} prefix 数据前缀
   */
  cleanupByPrefix(prefix) {
    const keysToRemove = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith(prefix)) {
        keysToRemove.push(key)
      }
    }
    
    keysToRemove.forEach(key => {
      localStorage.removeItem(key)
      console.log('清理数据:', key)
    })
    
    console.log(`清理前缀 ${prefix} 的数据完成，共清理 ${keysToRemove.length} 个数据项`)
  }

  /**
   * 检查存储使用率
   * @returns {number} 存储使用率 (0-1)
   */
  getStorageUsageRatio() {
    const usage = this.getStorageUsage()
    // 假设localStorage总容量为5MB
    const totalCapacity = 5 * 1024 * 1024
    return usage.totalSize / totalCapacity
  }

  /**
   * 是否需要清理存储
   * @returns {boolean} 是否需要清理
   */
  shouldCleanup() {
    return this.getStorageUsageRatio() > this.cleanupThreshold
  }
}

// 创建单例实例
const storageManager = new StorageManager()

export default storageManager

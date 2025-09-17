/**
 * 修复提交流程状态管理
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

import { defineStore } from 'pinia'
import { MessagePlugin } from 'tdesign-vue-next'
import storageManager from '@/utils/storageManager'

export const useRestorationFlowStore = defineStore('restorationFlow', {
  state: () => ({
    // 当前工作流ID
    workflowId: null,
    
    // 当前步骤 (0: 保密协议, 1: 表单填写, 2: 图片编辑, 3: 质量监督, 4: 信息确认, 5: 提交成功)
    currentStep: 0,
    
    // 步骤配置
    steps: [
      { label: '保密协议', value: 'privacy' },
      { label: '表单填写', value: 'form' },
      { label: '图片编辑', value: 'image-edit' },
      { label: '质量监督', value: 'quality-supervision' },
      { label: '信息确认', value: 'confirm' },
      { label: '提交成功', value: 'success' }
    ],
    
    // 表单数据
    formData: {
      image_file: [], // 存储多个文件对象数组
      image_desc: '',
      image_desc_file: null,
      restoration_opinion: '',
      opinion_tags: '',
      opinion_file: null,
      remark: '',
      attachment_file: null,
      quality_check: [], // 质量检测项目
      quality_statement: '', // 质量保证声明
      submitter_unit: '', // 提交者单位
      operator_unit: '' // 操作人员单位
    },
    
    // 保密协议状态
    privacyAccepted: false,
    
    // 图片编辑数据
    imageEditData: {
      originalImage: null,
      editedImage: null,
      fabricData: null // fabric.js 画布数据
    },
    
    // 提交状态
    isSubmitting: false,
    
    // 数据是否有更改
    hasChanges: false
  }),
  
  getters: {
    // 获取当前步骤信息
    getCurrentStep: (state) => state.steps[state.currentStep],
    
    // 是否可以返回上一步
    canGoBack: (state) => state.currentStep > 0,
    
    // 是否可以进行下一步
    canGoNext: (state) => {
      switch (state.currentStep) {
        case 0: // 保密协议
          return state.privacyAccepted
        case 1: // 表单填写
          // 至少需要填写图片描述、视频描述或修复意见中的一项
          return !!(state.formData.image_desc || state.formData.video_desc || state.formData.restoration_opinion)
        case 2: // 图片编辑
          // 必须上传图片并完成编辑才能进行下一步
          return !!(state.formData.image_file && 
                   Array.isArray(state.formData.image_file) && 
                   state.formData.image_file.length > 0 &&
                   state.imageEditData.editedImage)
        case 3: // 质量监督
          // 质量监督步骤暂时总是可以通过
          return true
        case 4: // 信息确认
          return !state.isSubmitting
        default:
          return false
      }
    },
    
    // 下一步按钮文本
    getNextButtonText: (state) => {
      switch (state.currentStep) {
        case 0: return '同意并继续'
        case 1: return '继续编辑'
        case 2: return '质量监督'
        case 3: return '确认信息'
        case 4: return '提交修复'
        default: return '下一步'
      }
    },
    
    // 检查表单是否填写完整
    isFormComplete: (state) => {
      // 至少需要填写图片描述、视频描述或修复意见中的一项
      return !!(state.formData.image_desc || state.formData.video_desc || state.formData.restoration_opinion)
    }
  },
  
  actions: {
    // 初始化流程
    initFlow(workflowId) {
      this.workflowId = workflowId
      this.currentStep = 0
      this.privacyAccepted = false
      this.hasChanges = false
      
      // 尝试从 localStorage 恢复数据
      const existingData = this.loadFromStorage()
      
      // 如果是新流程或者数据已过期，清空所有表单数据
      if (!existingData || this.isDataExpired()) {
        this.clearFormData()
        console.log('新流程或数据过期，清空所有表单数据')
      } else {
        console.log('恢复已保存的流程数据')
      }
      
      console.log('初始化修复提交流程，工作流ID:', workflowId)
    },
    
    // 更新表单数据
    updateFormData(data) {
      Object.assign(this.formData, data)
      this.hasChanges = true
      this.saveToStorage()
    },
    
    // 接受保密协议
    acceptPrivacy() {
      this.privacyAccepted = true
      this.saveToStorage()
    },
    
    // 保存图片编辑数据
    saveImageEdit(data) {
      Object.assign(this.imageEditData, data)
      this.hasChanges = true
      this.saveToStorage()
    },
    
    // 下一步
    nextStep() {
      if (this.canGoNext && this.currentStep < this.steps.length - 1) {
        this.currentStep++
        this.saveToStorage()
        return true
      }
      return false
    },
    
    // 上一步
    prevStep() {
      if (this.canGoBack) {
        this.currentStep--
        this.saveToStorage()
        return true
      }
      return false
    },
    
    // 跳转到指定步骤
    goToStep(step) {
      if (step >= 0 && step < this.steps.length) {
        this.currentStep = step
        this.saveToStorage()
      }
    },
    
    // 提交表单
    async submitFlow() {
      try {
        this.isSubmitting = true
        
        // 构建提交数据
        const submitData = new FormData()
        submitData.append('workflow_id', this.workflowId)
        submitData.append('image_desc', this.formData.image_desc || '')
        submitData.append('restoration_opinion', this.formData.restoration_opinion || '')
        submitData.append('remark', this.formData.remark || '')
        
        // 处理标签数据
        if (this.formData.opinion_tags) {
          const tags = this.formData.opinion_tags.split(',').map(tag => tag.trim()).filter(tag => tag)
          submitData.append('opinion_tags', JSON.stringify(tags))
        }
        
        // 添加文件
        if (this.formData.image_file && Array.isArray(this.formData.image_file)) {
          this.formData.image_file.forEach((file, index) => {
            submitData.append(`image_file_${index}`, file)
          })
        }
        
        if (this.formData.image_desc_file) {
          submitData.append('image_desc_file', this.formData.image_desc_file)
        }
        
        if (this.formData.opinion_file) {
          submitData.append('opinion_file', this.formData.opinion_file)
        }
        
        if (this.formData.attachment_file) {
          submitData.append('attachment_file', this.formData.attachment_file)
        }
        
        // 如果有编辑后的图片，替换原图片
        if (this.imageEditData.editedImage) {
          // 将编辑后的图片转换为 Blob
          const response = await fetch(this.imageEditData.editedImage)
          const blob = await response.blob()
          submitData.set('image_file', blob, 'edited_image.png')
        }
        
        // 调用 API 提交
        const { submitForm } = await import('@/api/restoration')
        await submitForm(submitData)
        
        // 标记工作流已提交
        this.markWorkflowSubmitted(this.workflowId)
        
        this.currentStep = 5 // 跳转到成功页面
        this.hasChanges = false
        
        MessagePlugin.success('修复表单提交成功')
        
        // 注意：数据清空将在成功页面延迟执行，确保用户能看到成功信息
        
        return true
      } catch (error) {
        console.error('提交修复表单失败:', error)
        MessagePlugin.error('提交失败: ' + (error.response?.data?.detail || error.message))
        return false
      } finally {
        this.isSubmitting = false
      }
    },
    
    // 清理流程数据
    clearFlow() {
      // 重置所有数据到初始状态
      this.workflowId = null
      this.currentStep = 0
      this.privacyAccepted = false
      this.hasChanges = false
      this.isSubmitting = false
      
      // 清空表单数据
      this.formData = {
        image_file: [],
        image_desc: '',
        image_desc_file: null,
        restoration_opinion: '',
        opinion_tags: '',
        opinion_file: null,
        remark: '',
        attachment_file: null
      }
      
      // 清空图片编辑数据
      this.imageEditData = {
        originalImage: null,
        editedImage: null,
        fabricData: null
      }
      
      // 移除本地存储
      this.removeFromStorage()
      
      // 清除所有相关的本地存储
      this.clearAllFlowStorage()
      
      console.log('已清除所有修复流程数据')
    },
    
    // 清除所有流程相关的本地存储
    clearAllFlowStorage() {
      try {
        // 清除所有修复流程相关的存储
        const keysToRemove = []
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i)
          if (key && (key.startsWith('restoration_flow_') || key.startsWith('workflow_submitted_'))) {
            keysToRemove.push(key)
          }
        }
        
        keysToRemove.forEach(key => {
          localStorage.removeItem(key)
        })
        
        // 清除sessionStorage中的相关数据
        const sessionKeysToRemove = []
        for (let i = 0; i < sessionStorage.length; i++) {
          const key = sessionStorage.key(i)
          if (key && (key.startsWith('restoration_flow_') || key.startsWith('workflow_submitted_'))) {
            sessionKeysToRemove.push(key)
          }
        }
        
        sessionKeysToRemove.forEach(key => {
          sessionStorage.removeItem(key)
        })
        
        console.log('已清除所有修复流程相关的本地存储和会话存储')
      } catch (error) {
        console.error('清除存储失败:', error)
      }
    },
    
    // 标记工作流已提交（用于后续清空数据）
    markWorkflowSubmitted(workflowId) {
      const key = `workflow_submitted_${workflowId}`
      storageManager.setItem(key, {
        submitted: true,
        timestamp: Date.now()
      }, false)
    },
    
    // 检查工作流是否已提交
    isWorkflowSubmitted(workflowId) {
      const key = `workflow_submitted_${workflowId}`
      const data = storageManager.getItem(key)
      
      if (data) {
        // 检查是否在24小时内提交过
        const isRecent = Date.now() - data.timestamp < 24 * 60 * 60 * 1000
        return data.submitted && isRecent
      }
      return false
    },
    
    // 保存到本地存储
    saveToStorage() {
      if (!this.workflowId) return
      
      // 检查是否需要清理存储
      if (storageManager.shouldCleanup()) {
        storageManager.cleanupStorage()
      }
      
      const data = {
        workflowId: this.workflowId,
        currentStep: this.currentStep,
        formData: this.sanitizeFormData(this.formData), // 清理文件对象
        privacyAccepted: this.privacyAccepted,
        imageEditData: {
          originalImage: this.imageEditData.originalImage, // 只保存URL，不保存文件对象
          editedImage: this.imageEditData.editedImage, // 只保存URL，不保存文件对象
          fabricData: this.imageEditData.fabricData // 保存 fabric 数据
        },
        hasChanges: this.hasChanges,
        timestamp: Date.now()
      }
      
      const key = `restoration_flow_${this.workflowId}`
      storageManager.setItem(key, data, false) // 不显示警告，避免频繁提示
    },
    
    // 从本地存储加载
    loadFromStorage() {
      if (!this.workflowId) return false
      
      const key = `restoration_flow_${this.workflowId}`
      const data = storageManager.getItem(key)
      
      if (data) {
        this.currentStep = data.currentStep || 0
        this.formData = { ...this.formData, ...data.formData }
        this.privacyAccepted = data.privacyAccepted || false
        this.imageEditData = { ...this.imageEditData, ...data.imageEditData }
        this.hasChanges = data.hasChanges || false
        
        console.log('从本地存储恢复修复流程数据')
        return true
      }
      return false
    },
    
    // 检查数据是否过期
    isDataExpired() {
      if (!this.workflowId) return true
      
      const key = `restoration_flow_${this.workflowId}`
      const data = storageManager.getItem(key)
      
      if (data) {
        const isExpired = Date.now() - data.timestamp > 24 * 60 * 60 * 1000
        return isExpired
      }
      return true
    },
    
    // 清空表单数据（保留流程状态）
    clearFormData() {
      this.formData = {
        image_file: [],
        image_desc: '',
        image_desc_file: null,
        restoration_opinion: '',
        opinion_tags: '',
        opinion_file: null,
        remark: '',
        attachment_file: null
      }
      
      this.imageEditData = {
        originalImage: null,
        editedImage: null,
        fabricData: null
      }
      
      this.privacyAccepted = false
      this.hasChanges = false
    },
    
    // 从本地存储移除
    removeFromStorage() {
      if (this.workflowId) {
        storageManager.removeItem(`restoration_flow_${this.workflowId}`)
      }
    },
    
    // 清理表单数据，移除文件对象
    sanitizeFormData(formData) {
      const sanitized = { ...formData }
      
      // 处理图片文件数组，保留URL信息
      if (sanitized.image_file && Array.isArray(sanitized.image_file)) {
        sanitized.image_file = sanitized.image_file.map(file => {
          if (file && typeof file === 'object') {
            // 确保URL能够持久化保存
            let url = file.url
            if (!url && file.raw) {
              // 如果raw文件存在但没有URL，创建URL
              url = URL.createObjectURL(file.raw)
            }
            
            return {
              name: file.name,
              size: file.size,
              type: file.type,
              lastModified: file.lastModified,
              url: url,
              uid: file.uid || file.id || Date.now() + Math.random(),
              // 保留原始文件对象用于编辑页面
              raw: file.raw || file
            }
          }
          return file
        })
      }
      
      // 处理视频文件数组，保留URL和缩略图信息
      if (sanitized.video_file && Array.isArray(sanitized.video_file)) {
        sanitized.video_file = sanitized.video_file.map(file => {
          if (file && typeof file === 'object') {
            // 确保URL和缩略图能够持久化保存
            let url = file.url
            let thumbUrl = file.thumbUrl
            if (!url && file.raw) {
              url = URL.createObjectURL(file.raw)
            }
            if (!thumbUrl && file.url) {
              thumbUrl = file.url
            }
            
            return {
              name: file.name,
              size: file.size,
              type: file.type,
              lastModified: file.lastModified,
              url: url,
              thumbUrl: thumbUrl,
              uid: file.uid || file.id || Date.now() + Math.random(),
              // 保留原始文件对象用于编辑页面
              raw: file.raw || file,
              // 保留视频缩略图生成状态
              _posterReady: file._posterReady || false
            }
          }
          return file
        })
      }
      
      // 移除其他文件对象，只保留基本信息
      Object.keys(sanitized).forEach(key => {
        if (key !== 'image_file' && key !== 'video_file' && sanitized[key] && typeof sanitized[key] === 'object' && sanitized[key].name) {
          // 如果是文件对象，只保存基本信息
          sanitized[key] = {
            name: sanitized[key].name,
            size: sanitized[key].size,
            type: sanitized[key].type,
            lastModified: sanitized[key].lastModified
          }
        }
      })
      
      return sanitized
    },
    
    // 获取存储使用情况
    getStorageUsage() {
      return storageManager.getStorageUsage()
    },
    
    // 清理存储空间
    cleanupStorage() {
      storageManager.cleanupStorage()
    },
    
    // 强制清理存储空间
    forceCleanupStorage() {
      storageManager.forceCleanup()
    },
    
    // 更新质量检测数据
    updateQualityCheck(data) {
      Object.assign(this.formData, data)
      this.hasChanges = true
      this.saveToStorage()
    },
    
    // 获取质量检测数据
    getQualityCheckData() {
      return {
        quality_check: this.formData.quality_check || [],
        quality_statement: this.formData.quality_statement || ''
      }
    },
    
    // 检查质量检测是否完成
    isQualityCheckComplete() {
      const qualityCheck = this.formData.quality_check || []
      const hasStatement = (this.formData.quality_statement || '').trim().length > 0
      return qualityCheck.length === 4 && hasStatement
    }
  }
})

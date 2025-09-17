<template>
  <Layout>
    <div class="restoration-flow">
      <!-- 页面头部 -->
      <div class="flow-header">
        <div class="flow-title">
          <h2>修复提交流程</h2>
          <p>工作流ID: {{ store.workflowId }}</p>
        </div>
        
        <div class="flow-actions-header">
          <t-button 
            theme="default" 
            variant="outline" 
            @click="handleExit"
            :disabled="store.isSubmitting"
          >
            <template #icon>
              <t-icon name="close" />
            </template>
            退出流程
          </t-button>
        </div>
      </div>
      
      <!-- 进度条 -->
      <div class="flow-progress">
        <t-steps 
          :current="store.currentStep" 
          :options="stepOptions"
          theme="dot"
        />
      </div>
      
      <!-- 页面内容 -->
      <div class="flow-content">
        <router-view />
      </div>
      
      <!-- 导航按钮 -->
      <div class="flow-actions" v-if="store.currentStep < 5">
        <t-button 
          @click="goBack" 
          :disabled="!store.canGoBack || store.isSubmitting"
          theme="default"
        >
          <template #icon>
            <t-icon name="chevron-left" />
          </template>
          返回上一步
        </t-button>
        
        <t-button 
          theme="primary" 
          @click="goNext" 
          :disabled="!store.canGoNext || store.isSubmitting"
          :loading="store.isSubmitting && store.currentStep === 4"
        >
          {{ store.getNextButtonText }}
          <template #suffix>
            <t-icon name="chevron-right" />
          </template>
        </t-button>
      </div>
    </div>

    <!-- 离开确认对话框 -->
    <t-dialog
      v-model:visible="showExitDialog"
      header="确认退出"
      width="400px"
      :footer="false"
    >
      <p>您有未保存的修复信息，确定要退出流程吗？</p>
      <p class="exit-warning">退出后数据将被清除，无法恢复。</p>
      
      <div class="dialog-footer">
        <t-space>
          <t-button theme="default" @click="showExitDialog = false">取消</t-button>
          <t-button theme="danger" @click="confirmExit">确定退出</t-button>
        </t-space>
      </div>
    </t-dialog>

    <!-- 质量监督确认对话框 -->
    <t-dialog
      v-model:visible="showQualityDialog"
      header="质量监督确认"
      width="400px"
      :footer="false"
    >
      <p>{{ qualityDialogMessage }}</p>
      
      <div class="dialog-footer">
        <t-space>
          <t-button theme="default" @click="cancelQualitySupervision">取消</t-button>
          <t-button theme="primary" @click="confirmQualitySupervision">确认进行质量监督</t-button>
        </t-space>
      </div>
    </t-dialog>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { useRestorationFlowStore } from '@/stores/restorationFlow'
import Layout from '@/components/Layout.vue'

/**
 * 修复提交流程布局组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const router = useRouter()
const route = useRoute()
const store = useRestorationFlowStore()

const showExitDialog = ref(false)
const showQualityDialog = ref(false)
const qualityDialogMessage = ref('')

// 步骤选项配置
const stepOptions = computed(() => 
  store.steps.map((step, index) => ({
    title: step.label,
    content: step.label,
    status: index < store.currentStep ? 'finish' : 
           index === store.currentStep ? 'process' : 'default'
  }))
)

// 页面离开检查
const checkUnsavedChanges = () => {
  if (store.hasChanges && store.currentStep !== 5) {
    return '您有未保存的修复信息，确定要离开吗？'
  }
  return null
}

// 返回上一步
const goBack = async () => {
  if (store.prevStep()) {
    const targetRoute = `/restoration-flow/${store.workflowId}/${store.getCurrentStep.value}`
    await router.push(targetRoute)
  }
}

// 进行下一步
const goNext = async () => {
  // 如果是图片编辑步骤（步骤2），先自动保存编辑内容
  if (store.currentStep === 2) {
    await autoSaveImageEdit()
  }
  
  // 如果是质量监督步骤（步骤3），显示确认对话框
  if (store.currentStep === 3) {
    await showQualitySupervisionConfirm()
    return
  }
  
  if (store.currentStep === 4) {
    // 第五步是提交，调用提交方法
    const success = await store.submitFlow()
    if (success) {
      await router.push(`/restoration-flow/${store.workflowId}/success`)
    }
  } else if (store.nextStep()) {
    const targetRoute = `/restoration-flow/${store.workflowId}/${store.getCurrentStep.value}`
    await router.push(targetRoute)
  }
}

// 显示质量监督确认对话框
const showQualitySupervisionConfirm = async () => {
  try {
    // 获取用户信息
    const currentUserStr = localStorage.getItem('currentUser')
    let userName = '当前用户'
    let userRole = '修复专家'
    
    if (currentUserStr) {
      const currentUser = JSON.parse(currentUserStr)
      userName = currentUser.name || currentUser.full_name || currentUser.display_name || '当前用户'
      userRole = currentUser.role || currentUser.user_type || '修复专家'
    }
    
    // 设置对话框消息
    qualityDialogMessage.value = `确认由 ${userName}（${userRole}）进行质量监督检测吗？`
    
    // 显示对话框
    showQualityDialog.value = true
  } catch (error) {
    console.error('显示质量监督确认对话框失败:', error)
  }
}

// 确认质量监督
const confirmQualitySupervision = async () => {
  try {
    // 关闭对话框
    showQualityDialog.value = false
    
    // 显示成功消息
    const { MessagePlugin } = await import('tdesign-vue-next')
    MessagePlugin.success('质量监督检测已启动')
    
    // 进入下一步
    if (store.nextStep()) {
      await router.push(`/restoration-flow/${store.workflowId}/${store.getCurrentStep.value}`)
    }
  } catch (error) {
    console.error('确认质量监督失败:', error)
  }
}

// 取消质量监督
const cancelQualitySupervision = async () => {
  try {
    // 关闭对话框
    showQualityDialog.value = false
    
    // 显示取消消息
    const { MessagePlugin } = await import('tdesign-vue-next')
    MessagePlugin.info('已取消质量监督检测')
  } catch (error) {
    console.error('取消质量监督失败:', error)
  }
}

// 自动保存图片编辑内容
const autoSaveImageEdit = async () => {
  try {
    // 获取当前页面的画布元素
    const canvasElement = document.querySelector('.fabric-canvas')
    if (!canvasElement) {
      console.log('未找到画布元素，跳过自动保存')
      return
    }
    
    // 检查是否有 fabric 实例
    const fabricInstance = canvasElement.fabric
    if (!fabricInstance) {
      console.log('未找到 fabric 实例，跳过自动保存')
      return
    }
    
    // 导出为数据URL
    const dataURL = fabricInstance.toDataURL({
      format: 'png',
      quality: 0.9
    })
    
    // 保存到store
    store.saveImageEdit({
      editedImage: dataURL,
      fabricData: JSON.stringify(fabricInstance.toJSON()),
      hasEdited: true
    })
    
    console.log('自动保存图片编辑内容成功')
  } catch (error) {
    console.error('自动保存图片编辑失败:', error)
    // 不显示错误提示，静默处理
  }
}

// 处理退出流程
const handleExit = () => {
  if (store.hasChanges && store.currentStep !== 5) {
    showExitDialog.value = true
  } else {
    confirmExit()
  }
}

// 确认退出
const confirmExit = () => {
  // 清除所有流程数据和本地存储
  store.clearFlow()
  showExitDialog.value = false
  
  // 清除所有相关的本地存储
  clearAllFlowStorage()
  
  router.push('/restoration')
  MessagePlugin.info('已退出修复提交流程，所有数据已清除')
}

// 清除所有流程相关的本地存储
const clearAllFlowStorage = () => {
  try {
    // 清除当前工作流的存储
    if (store.workflowId) {
      localStorage.removeItem(`restoration_flow_${store.workflowId}`)
      localStorage.removeItem(`workflow_submitted_${store.workflowId}`)
    }
    
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
    
    console.log('已清除所有修复流程相关的本地存储')
  } catch (error) {
    console.error('清除本地存储失败:', error)
  }
}

// 监听浏览器返回/刷新事件
const handleBeforeUnload = (event) => {
  const message = checkUnsavedChanges()
  if (message) {
    event.preventDefault()
    event.returnValue = message
    return message
  }
}

// 路由守卫 - 检查离开当前页面
const handleRouteLeave = (to, from, next) => {
  if (!to.path.startsWith('/restoration-flow/')) {
    const message = checkUnsavedChanges()
    if (message && !confirm(message)) {
      next(false)
      return
    }
    
    // 离开修复流程时，清除所有数据
    if (store.hasChanges || store.workflowId) {
      store.clearFlow()
      clearAllFlowStorage()
    }
  }
  next()
}

// 监听路由变化，同步当前步骤
watch(() => route.path, (newPath) => {
  // 根据路由路径设置当前步骤
  if (newPath.includes('/privacy')) {
    store.currentStep = 0
  } else if (newPath.includes('/form')) {
    store.currentStep = 1
  } else if (newPath.includes('/image-edit')) {
    store.currentStep = 2
  } else if (newPath.includes('/quality-supervision')) {
    store.currentStep = 3
  } else if (newPath.includes('/confirm')) {
    store.currentStep = 4
  } else if (newPath.includes('/success')) {
    store.currentStep = 5
  }
}, { immediate: true })

onMounted(() => {
  // 初始化工作流
  const workflowId = route.params.workflowId
  if (workflowId) {
    store.initFlow(workflowId)
  }
  
  // 添加页面离开监听
  window.addEventListener('beforeunload', handleBeforeUnload)
  
  // 添加路由守卫
  router.beforeEach(handleRouteLeave)
})

onUnmounted(() => {
  // 清理事件监听
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
</script>

<style scoped>
.restoration-flow {
  max-width: 1900px;
  margin: 0 auto;
  padding: 16px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
}

.flow-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.flow-title h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.flow-title p {
  color: #6b7280;
  margin: 0;
  font-size: 14px;
}

.flow-progress {
  margin-bottom: 20px;
  padding: 0 16px;
  flex-shrink: 0;
}

.flow-content {
  flex: 1;
  margin-bottom: 20px;
  overflow-y: auto;
  min-height: 0;
}

.flow-actions {
  
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-top: 1px solid #3870e0;
  /* background: transparent; */
  flex-shrink: 0;
}

.exit-warning {
  color: #dc2626;
  font-size: 14px;
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .restoration-flow {
    max-width: 1400px;
  }
}

@media (max-width: 1200px) {
  .restoration-flow {
    max-width: 1200px;
  }
}

@media (max-width: 768px) {
  .restoration-flow {
    padding: 16px;
    max-width: 100%;
  }
  
  .flow-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .flow-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .flow-actions > * {
    width: 100%;
  }
}
</style>

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
      <div class="flow-actions" v-if="store.currentStep < 4">
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
          :loading="store.isSubmitting && store.currentStep === 3"
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
  if (store.hasChanges && store.currentStep !== 4) {
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
  
  if (store.currentStep === 3) {
    // 第四步是提交，调用提交方法
    const success = await store.submitFlow()
    if (success) {
      await router.push(`/restoration-flow/${store.workflowId}/success`)
    }
  } else if (store.nextStep()) {
    const targetRoute = `/restoration-flow/${store.workflowId}/${store.getCurrentStep.value}`
    await router.push(targetRoute)
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
  if (store.hasChanges && store.currentStep !== 4) {
    showExitDialog.value = true
  } else {
    confirmExit()
  }
}

// 确认退出
const confirmExit = () => {
  store.clearFlow()
  showExitDialog.value = false
  router.push('/restoration')
  MessagePlugin.info('已退出修复提交流程')
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
    
    if (store.hasChanges) {
      store.clearFlow()
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
  } else if (newPath.includes('/confirm')) {
    store.currentStep = 3
  } else if (newPath.includes('/success')) {
    store.currentStep = 4
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
  overflow: hidden;
  min-height: 0;
}

.flow-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-top: 1px solid #e5e7eb;
  background: #fff;
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
@media (max-width: 768px) {
  .restoration-flow {
    padding: 16px;
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

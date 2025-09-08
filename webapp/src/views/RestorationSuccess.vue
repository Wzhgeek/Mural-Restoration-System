<template>
  <div class="success-page">
    <div class="success-container">
      <div class="success-icon">
        <t-icon name="check-circle" size="72px" />
      </div>
      
      <h2 class="success-title">修复申请提交成功！</h2>
      
      <p class="success-description">
        您的修复申请已成功提交，系统将开始处理您的申请。
      </p>
      
      <div class="success-details">
        <t-descriptions :column="1" bordered>
          <t-descriptions-item label="工作流ID">{{ store.workflowId }}</t-descriptions-item>
          <t-descriptions-item label="提交时间">{{ submitTime }}</t-descriptions-item>
          <t-descriptions-item label="下一步">等待专家评估</t-descriptions-item>
        </t-descriptions>
      </div>
      
      <div class="next-steps">
        <h3>后续流程</h3>
        <div class="steps-list">
          <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-content">
              <h4>专家评估</h4>
              <p>修复专家将对您提交的方案进行评估和审核</p>
            </div>
          </div>
          
          <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-content">
              <h4>方案反馈</h4>
              <p>您将收到专家的评估意见和建议</p>
            </div>
          </div>
          
          <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-content">
              <h4>继续完善</h4>
              <p>根据反馈意见继续完善修复方案</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="action-buttons">
        <t-button theme="primary" @click="goToWorkflowList" size="large">
          <template #icon>
            <t-icon name="view-list" />
          </template>
          查看我的工作流
        </t-button>
        
        <t-button theme="default" @click="goToDashboard" size="large">
          <template #icon>
            <t-icon name="dashboard" />
          </template>
          返回仪表盘
        </t-button>
        
        <t-button theme="default" variant="outline" @click="createNewWorkflow" size="large">
          <template #icon>
            <t-icon name="add" />
          </template>
          创建新工作流
        </t-button>
      </div>
      
      <!-- 分享和保存选项 -->
      <div class="additional-actions">
        <h4>其他操作</h4>
        <div class="action-list">
          <t-button variant="text" @click="copyWorkflowId">
            <template #icon>
              <t-icon name="copy" />
            </template>
            复制工作流ID
          </t-button>
          
          <t-button variant="text" @click="downloadSummary">
            <template #icon>
              <t-icon name="download" />
            </template>
            下载提交摘要
          </t-button>
          
          <t-button variant="text" @click="shareWorkflow">
            <template #icon>
              <t-icon name="share" />
            </template>
            分享工作流
          </t-button>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { useRestorationFlowStore } from '@/stores/restorationFlow'

/**
 * 提交成功页面
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const store = useRestorationFlowStore()
const router = useRouter()

const submitTime = ref('')

// 跳转到工作流列表
const goToWorkflowList = () => {
  // 确保数据已清空
  store.clearFlow()
  router.push('/restoration')
}

// 跳转到仪表盘
const goToDashboard = () => {
  // 确保数据已清空
  store.clearFlow()
  router.push('/dashboard')
}

// 创建新工作流
const createNewWorkflow = () => {
  // 确保数据已清空
  store.clearFlow()
  router.push('/restoration')
  MessagePlugin.info('可以创建新的修复工作流')
}

// 复制工作流ID
const copyWorkflowId = () => {
  if (!store.workflowId) return
  
  try {
    navigator.clipboard.writeText(store.workflowId).then(() => {
      MessagePlugin.success('工作流ID已复制到剪贴板')
    })
  } catch (error) {
    // 兼容旧浏览器
    const textArea = document.createElement('textarea')
    textArea.value = store.workflowId
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    MessagePlugin.success('工作流ID已复制到剪贴板')
  }
}

// 下载提交摘要
const downloadSummary = () => {
  try {
    const summary = {
      workflowId: store.workflowId,
      submitTime: submitTime.value,
      formData: {
        imageDesc: store.formData.image_desc || '未填写',
        restorationOpinion: store.formData.restoration_opinion || '未填写',
        opinionTags: store.formData.opinion_tags || '未填写',
        remark: store.formData.remark || '未填写'
      },
      hasImageEdit: !!store.imageEditData.editedImage
    }
    
    const content = `
修复申请提交摘要

工作流ID: ${summary.workflowId}
提交时间: ${summary.submitTime}
图片编辑: ${summary.hasImageEdit ? '是' : '否'}

=== 表单信息 ===
图片描述: ${summary.formData.imageDesc}

修复意见: ${summary.formData.restorationOpinion}

修复标签: ${summary.formData.opinionTags}

备注说明: ${summary.formData.remark}

=== 系统信息 ===
生成时间: ${new Date().toLocaleString('zh-CN')}
系统名称: 克孜尔石窟壁画智慧修复全生命周期管理系统
    `.trim()
    
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = `修复申请摘要_${store.workflowId}_${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    
    URL.revokeObjectURL(url)
    MessagePlugin.success('提交摘要已下载')
  } catch (error) {
    console.error('下载失败:', error)
    MessagePlugin.error('下载失败，请重试')
  }
}

// 分享工作流
const shareWorkflow = () => {
  const shareText = `我刚刚在克孜尔石窟壁画修复系统中提交了一个修复申请，工作流ID: ${store.workflowId}`
  
  if (navigator.share) {
    // 使用原生分享API
    navigator.share({
      title: '修复申请已提交',
      text: shareText,
      url: window.location.origin
    }).catch(error => {
      console.log('分享取消:', error)
    })
  } else {
    // 复制到剪贴板
    try {
      navigator.clipboard.writeText(shareText).then(() => {
        MessagePlugin.success('分享文本已复制到剪贴板')
      })
    } catch (error) {
      MessagePlugin.error('分享功能不可用')
    }
  }
}

onMounted(() => {
  // 设置提交时间
  submitTime.value = new Date().toLocaleString('zh-CN')
  
  // 如果没有工作流ID，重定向到修复页面
  if (!store.workflowId) {
    MessagePlugin.warning('未找到工作流信息，请重新开始')
    router.push('/restoration')
  } else {
    // 显示成功信息
    MessagePlugin.success('修复申请已成功提交！')
    
    // 注意：不再自动清空数据，保持在成功页面
    // 数据将在用户主动操作（如点击按钮）时清空
    console.log('提交成功，保持在成功页面')
  }
})
</script>

<style scoped>
.success-page {
  max-width: 800px;
  margin: 0 auto;
  max-height: 880px;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
}

.success-container {
  text-align: center;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 100%;
  overflow-y: auto;
}

.success-icon {
  color: #10b981;
  margin-bottom: 24px;
}

.success-title {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
}

.success-description {
  font-size: 16px;
  color: #6b7280;
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.success-details {
  max-width: 400px;
  margin: 0 auto 24px auto;
  text-align: left;
}

.next-steps {
  text-align: left;
  margin: 24px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.next-steps h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
  text-align: center;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #0052d9;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.step-content p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
  margin: 24px 0;
}

.additional-actions {
  margin: 24px 0;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.additional-actions h4 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 16px 0;
}

.action-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
}


/* 响应式设计 */
@media (max-width: 768px) {
  .success-container {
    padding: 24px;
    margin: 16px;
  }
  
  .success-title {
    font-size: 24px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons > * {
    width: 100%;
  }
  
  .steps-list {
    gap: 20px;
  }
  
  .step-item {
    flex-direction: column;
    text-align: center;
    align-items: center;
  }
  
  .step-content {
    text-align: center;
  }
}
</style>

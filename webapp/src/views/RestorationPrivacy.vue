<template>
  <div class="privacy-page">
    <div class="page-header">
      <h3>保密协议</h3>
      
      <div class="privacy-reminder">
      <t-icon name="info-circle" />
      <span>温馨提示：请仔细阅读协议内容，确保您完全理解并同意所有条款后再进行下一步操作</span>
    </div>
    </div>
    
    <t-card class="privacy-card">
      <div class="privacy-content" ref="privacyContentRef" @scroll="handleScroll">
        <div v-if="loading" class="loading-container">
          <t-loading size="medium" />
          <p>加载协议内容中...</p>
        </div>
        
        <div v-else class="privacy-text">
          {{ privacyContent }}
        </div>
      </div>
      
      <div class="privacy-status">
        
        <div class="privacy-tip" v-if="!canAgree">
          <t-icon name="info-circle" />
          <span>请仔细阅读协议内容后继续</span>
        </div>
        
        <div class="privacy-agreement" v-if="canAgree">
          <t-checkbox v-model="agreed" size="large">
            我已仔细阅读并同意上述保密协议的所有条款
          </t-checkbox>
        </div>
      </div>
    </t-card>
    
    <!-- 温馨提示 -->
   
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { getPrivacyAgreement } from '@/api/restoration'
import { useRestorationFlowStore } from '@/stores/restorationFlow'

/**
 * 保密协议页面
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const store = useRestorationFlowStore()

const loading = ref(true)
const privacyContent = ref('')
const canAgree = ref(false)
const agreed = ref(store.privacyAccepted)

const privacyContentRef = ref(null)

// 处理滚动事件（已移除滚动限制，直接允许同意）
const handleScroll = () => {
  // 不再需要滚动检测，直接设置为可同意状态
  canAgree.value = true
}

// 监听同意状态变化
watch(agreed, (newValue) => {
  if (newValue) {
    store.acceptPrivacy()
    MessagePlugin.success('已同意保密协议，可以继续下一步')
  }
})

// 加载保密协议内容
const loadPrivacyContent = async () => {
  try {
    loading.value = true
    const response = await getPrivacyAgreement()
    privacyContent.value = response.data?.content || response.content || '保密协议内容'
    
    // 等待DOM更新后检查内容高度
    setTimeout(() => {
      handleScroll()
    }, 100)
  } catch (error) {
    console.error('加载保密协议失败:', error)
    MessagePlugin.error('加载保密协议失败: ' + (error.response?.data?.detail || error.message))
    
    // 使用默认内容
    privacyContent.value = `
克孜尔石窟壁画智慧修复全生命周期管理系统保密协议

1. 保密义务
用户在使用本系统进行壁画修复工作时，应当严格遵守保密义务，不得向无关人员泄露任何涉及石窟壁画的修复信息、技术资料、图像数据等敏感信息。

2. 数据安全
用户承诺妥善保管系统账号和密码，不得将账号信息泄露给他人。上传到系统的所有壁画图像、修复方案、评估报告等数据均属于敏感文化遗产资料，必须严格保密。

3. 使用范围
系统提供的所有功能和数据仅限于石窟壁画修复研究使用，不得用于其他商业用途或学术目的之外的活动。

4. 责任承担
如因用户违反保密协议导致敏感信息泄露或造成其他损失，用户应承担相应的法律责任和经济责任。

5. 协议效力
本协议自用户点击同意之时生效，在用户使用系统期间持续有效。

请仔细阅读以上条款，确认同意后方可继续使用系统功能。
    `.trim()
    
    setTimeout(() => {
      handleScroll()
    }, 100)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPrivacyContent()
})
</script>

<style scoped>
.privacy-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-header p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.privacy-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.privacy-content {
  padding: 24px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 24px;
  position: relative;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
}

.privacy-text {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #374151;
  font-size: 14px;
}

.privacy-status {
  padding: 0 24px 24px 24px;
}


.privacy-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fef3c7;
  border-radius: 6px;
  color: #d97706;
  font-size: 14px;
  margin-bottom: 16px;
}

.privacy-agreement {
  padding: 16px;
  background: #f0f9ff;
  border-radius: 6px;
  border: 1px solid #0ea5e9;
}

.privacy-agreement :deep(.t-checkbox__label) {
  font-weight: 500;
  color: #1f2937;
}

.privacy-reminder {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  background: #f0f9ff;
  border-radius: 6px;
  border: 1px solid #bae6fd;
  color: #0369a1;
  font-size: 13px;
  line-height: 1.5;
}


/* 响应式设计 */
@media (max-width: 768px) {
  .privacy-content {
    padding: 16px;
  }
  
  .privacy-text {
    font-size: 13px;
    line-height: 1.6;
  }
  
  .privacy-reminder {
    font-size: 12px;
    padding: 10px 12px;
    margin-top: 12px;
  }
}
</style>

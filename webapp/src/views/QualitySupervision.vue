<template>
  <div class="quality-supervision-step">
    <!-- 质量自检步骤内容 -->
    <div class="step-content">
      <div class="notice-message">
        <t-icon name="check-circle" size="20px" />
        <span>请对您提交的修复方案进行质量自检确认。</span>
      </div>
      
      <div class="quality-check-section">
        <h5>质量自检项目</h5>
        <p class="items-desc">请仔细检查以下项目，确保您的修复方案质量符合要求：</p>
        
        <div class="check-items">
          <t-checkbox-group v-model="formData.quality_check" @change="handleFormChange">
            <div class="check-grid">
              <div class="check-item" v-for="(item, index) in qualityCheckItems" :key="index">
                <t-checkbox :value="item.value">
                  {{ item.label }}
                </t-checkbox>
              </div>
            </div>
          </t-checkbox-group>
        </div>
        
        <div class="quality-statement">
          <t-form-item label="质量保证声明" name="quality_statement">
            <t-textarea
              v-model="formData.quality_statement"
              placeholder="请在此声明您对提交内容质量的保证，包括检查过程和确认事项..."
              :autosize="{ minRows: 3, maxRows: 6 }"
              @change="handleFormChange"
            />
          </t-form-item>
        </div>
      </div>
      
      <div class="submitter-info">
        <h5>提交者信息</h5>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">姓名</span>
            <span class="value">{{ userInfo.name || '未获取' }}</span>
          </div>
          <div class="info-item">
            <span class="label">角色</span>
            <span class="value">{{ userInfo.role || '修复专家' }}</span>
          </div>
          <div class="info-item">
            <span class="label">单位</span>
            <span class="value">{{ userInfo.unit || '未设置' }}</span>
          </div>
        </div>
      </div>
      
      <!-- 验证状态显示 -->
      <div class="validation-status">
        <div class="status-item" :class="{ completed: validationStatus.checkedCount === 4 }">
          <t-icon :name="validationStatus.checkedCount === 4 ? 'check-circle' : 'time'" size="16px" />
          <span>质量检测项目：{{ validationStatus.checkedCount }}/4 已完成</span>
        </div>
        <div class="status-item" :class="{ completed: validationStatus.hasStatement }">
          <t-icon :name="validationStatus.hasStatement ? 'check-circle' : 'time'" size="16px" />
          <span>质量保证声明：{{ validationStatus.hasStatement ? '已填写' : '未填写' }}</span>
        </div>
      </div>
      
      <div class="warning-message" :class="{ 'can-continue': canContinue }">
        <t-icon :name="canContinue ? 'check-circle' : 'info-circle'" size="16px" />
        <span v-if="canContinue">
          质量自检已完成，可以进入下一阶段。
        </span>
        <span v-else>
          请完成所有质量检测项目并填写质量保证声明后才能继续。
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRestorationFlowStore } from '@/stores/restorationFlow'

/**
 * 质量自检步骤组件
 * 让提交者对自己提交的内容进行质量检测
 */

const store = useRestorationFlowStore()

// 表单数据
const formData = ref({
  quality_check: [],
  quality_statement: ''
})

// 用户信息
const userInfo = ref({
  name: '',
  role: '',
  unit: ''
})

// 质量检测项目
const qualityCheckItems = ref([
  { value: 'content_accuracy', label: '内容准确性：我已仔细核对所有填写内容，确保信息准确无误' },
  { value: 'file_quality', label: '文件质量：我已确认上传的图片和视频质量清晰，符合要求' },
  { value: 'description_complete', label: '描述完整：我已提供详细的图片描述和修复意见' },
  { value: 'data_integrity', label: '数据完整性：我已确认所有必要信息都已填写完整' }
])

// 处理质量检测复选框变化 - 现在由t-checkbox-group自动处理

// 处理表单变化
const handleFormChange = () => {
  // 保存到store中
  store.updateQualityCheck({
    quality_check: formData.value.quality_check,
    quality_statement: formData.value.quality_statement
  })
}

// 检查是否可以继续
const canContinue = computed(() => {
  // 必须勾选所有4个质量检测项目
  const allChecked = formData.value.quality_check.length === 4
  // 必须填写质量保证声明
  const hasStatement = formData.value.quality_statement.trim().length > 0
  return allChecked && hasStatement
})

// 获取验证状态信息
const validationStatus = computed(() => {
  const checkedCount = formData.value.quality_check.length
  const hasStatement = formData.value.quality_statement.trim().length > 0
  
  return {
    checkedCount,
    hasStatement,
    canContinue: checkedCount === 4 && hasStatement
  }
})

// 获取用户信息
const getUserInfo = () => {
  try {
    const currentUserStr = localStorage.getItem('currentUser')
    if (currentUserStr) {
      const currentUser = JSON.parse(currentUserStr)
      userInfo.value = {
        name: currentUser.full_name || currentUser.name || '未设置',
        role: currentUser.role_name || currentUser.role || '修复专家',
        unit: currentUser.unit || '未设置'
      }
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 初始化表单数据
const initFormData = () => {
  // 从store中恢复数据
  const storeData = store.getQualityCheckData()
  if (storeData) {
    formData.value.quality_check = storeData.quality_check || []
    formData.value.quality_statement = storeData.quality_statement || ''
  }
}

onMounted(() => {
  getUserInfo()
  initFormData()
})
</script>

<style scoped>
.quality-supervision-step {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.notice-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #0052d9;
  color: #1f2937;
  font-size: 15px;
  font-weight: 500;
}

.notice-message .t-icon {
  color: #10b981;
  flex-shrink: 0;
}

.quality-check-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.quality-check-section h5 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #0052d9;
}

.items-desc {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.check-items {
  margin-bottom: 20px;
}

.check-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.check-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
  min-height: 80px;
  display: flex;
  align-items: flex-start;
}

.check-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.check-item .t-checkbox {
  width: 100%;
  height: 100%;
}

.check-item .t-checkbox__label {
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  user-select: none;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .check-grid {
    gap: 12px;
  }
  
  .check-item {
    padding: 12px;
    min-height: 70px;
  }
  
  .check-item .t-checkbox__label {
    font-size: 13px;
  }
}

.quality-statement {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.submitter-info {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.submitter-info h5 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #0052d9;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item .value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.validation-status {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 14px;
  color: #6b7280;
}

.status-item.completed {
  color: #10b981;
}

.status-item .t-icon {
  flex-shrink: 0;
}

.warning-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #fef3c7;
  border-radius: 8px;
  color: #d97706;
  font-size: 14px;
  line-height: 1.6;
}

.warning-message.can-continue {
  background: #f0f9ff;
  color: #1e40af;
}

.warning-message .t-icon {
  color: #f59e0b;
  flex-shrink: 0;
  margin-top: 2px;
}

.warning-message.can-continue .t-icon {
  color: #10b981;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .quality-supervision-step {
    padding: 16px;
  }
  
  .notice-message {
    padding: 12px;
    font-size: 14px;
  }
  
  .quality-check-section,
  .submitter-info {
    padding: 16px;
  }
  
  .quality-check-section h5,
  .submitter-info h5 {
    font-size: 15px;
  }
  
  .items-desc {
    font-size: 13px;
  }
  
  /* 响应式样式已在上面定义 */
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .validation-status {
    padding: 12px;
  }
  
  .status-item {
    font-size: 13px;
    padding: 6px 0;
  }
  
  .warning-message {
    padding: 12px;
    font-size: 13px;
  }
}
</style>


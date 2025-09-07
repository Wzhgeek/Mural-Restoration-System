<template>
  <div class="confirm-page">
    <div class="page-header">
      <h3>确认提交信息</h3>
      <p>请仔细核对所有信息，确认无误后提交修复表单</p>
    </div>
    
    <div class="confirm-container">
      <!-- 基本信息 -->
      <t-card class="info-section" title="基本信息">
        <t-descriptions :column="2">
          <t-descriptions-item label="工作流ID">{{ store.workflowId }}</t-descriptions-item>
          <t-descriptions-item label="提交时间">{{ currentTime }}</t-descriptions-item>
          <t-descriptions-item label="保密协议">
            <t-tag theme="success" variant="light">已同意</t-tag>
          </t-descriptions-item>
        </t-descriptions>
      </t-card>
      
      <!-- 图片信息 -->
      <t-card class="info-section" title="壁画图片信息">
        <div class="image-info">
          <div class="image-preview" v-if="imagePreview">
            <div class="preview-container">
              <img :src="imagePreview" alt="壁画图片预览" class="preview-image" />
              <div class="image-overlay" v-if="hasImageEdit">
                <t-tag theme="primary" variant="light">已编辑</t-tag>
              </div>
            </div>
          </div>
          
          <div class="image-details">
            <div class="detail-item" v-if="store.formData.image_desc">
              <strong>图片描述：</strong>
              <p class="detail-content">{{ store.formData.image_desc }}</p>
            </div>
            
            <div class="detail-item" v-if="store.formData.image_desc_file">
              <strong>图片描述附件：</strong>
              <div class="file-info">
                <t-icon name="attach" />
                <span>{{ getFileName(store.formData.image_desc_file) }}</span>
              </div>
            </div>
            
            <div class="detail-item" v-if="!store.formData.image_desc && !store.formData.image_file">
              <p class="no-data">未上传图片信息</p>
            </div>
          </div>
        </div>
      </t-card>
      
      <!-- 修复方案信息 -->
      <t-card class="info-section" title="修复方案信息">
        <div class="restoration-info">
          <div class="detail-item" v-if="store.formData.restoration_opinion">
            <strong>修复意见：</strong>
            <p class="detail-content">{{ store.formData.restoration_opinion }}</p>
          </div>
          
          <div class="detail-item" v-if="formattedTags.length > 0">
            <strong>修复标签：</strong>
            <div class="tags-container">
              <t-tag 
                v-for="tag in formattedTags" 
                :key="tag" 
                theme="primary" 
                variant="light"
              >
                {{ tag }}
              </t-tag>
            </div>
          </div>
          
          <div class="detail-item" v-if="store.formData.opinion_file">
            <strong>修复意见附件：</strong>
            <div class="file-info">
              <t-icon name="attach" />
              <span>{{ getFileName(store.formData.opinion_file) }}</span>
            </div>
          </div>
          
          <div class="detail-item" v-if="!store.formData.restoration_opinion">
            <p class="no-data">未填写修复意见</p>
          </div>
        </div>
      </t-card>
      
      <!-- 其他信息 -->
      <t-card class="info-section" title="其他信息">
        <div class="other-info">
          <div class="detail-item" v-if="store.formData.remark">
            <strong>备注说明：</strong>
            <p class="detail-content">{{ store.formData.remark }}</p>
          </div>
          
          <div class="detail-item" v-if="store.formData.attachment_file">
            <strong>其他附件：</strong>
            <div class="file-info">
              <t-icon name="attach" />
              <span>{{ getFileName(store.formData.attachment_file) }}</span>
            </div>
          </div>
          
          <div class="detail-item" v-if="!store.formData.remark && !store.formData.attachment_file">
            <p class="no-data">无其他信息</p>
          </div>
        </div>
      </t-card>
      
      <!-- 图片编辑信息 -->
      <t-card class="info-section" title="图片编辑" v-if="hasImageEdit">
        <div class="edit-info">
          <div class="detail-item">
            <strong>编辑状态：</strong>
            <t-tag theme="success" variant="light">已进行图片编辑</t-tag>
          </div>
          
          <div class="edit-preview" v-if="store.imageEditData.editedImage">
            <strong>编辑后预览：</strong>
            <div class="edited-image-container">
              <img :src="store.imageEditData.editedImage" alt="编辑后图片" class="edited-image" />
            </div>
          </div>
        </div>
      </t-card>
      
      <!-- 提交确认 -->
      <div class="submit-section">
        <div class="submit-warning">
          <t-icon name="info-circle" />
          <span>请确认以上信息无误。提交后将无法修改，系统将开始处理您的修复申请。</span>
        </div>
        
        <div class="submit-actions">
          <t-button @click="goBack" :disabled="store.isSubmitting">
            返回修改
          </t-button>
          <t-button 
            theme="primary" 
            @click="handleSubmit" 
            :loading="store.isSubmitting"
            size="large"
          >
            确认提交修复申请
          </t-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { useRestorationFlowStore } from '@/stores/restorationFlow'

/**
 * 信息确认页面
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const store = useRestorationFlowStore()
const router = useRouter()

const currentTime = ref('')

// 计算属性
const imagePreview = computed(() => {
  if (store.imageEditData.editedImage) {
    return store.imageEditData.editedImage
  } else if (store.formData.image_file) {
    const imageFile = store.formData.image_file
    
    if (imageFile instanceof File) {
      return URL.createObjectURL(imageFile)
    } else if (typeof imageFile === 'string') {
      return imageFile
    } else if (imageFile && imageFile.raw) {
      return URL.createObjectURL(imageFile.raw)
    } else if (imageFile && imageFile.url) {
      return imageFile.url
    }
  }
  return null
})

const hasImageEdit = computed(() => {
  return store.imageEditData.editedImage && store.imageEditData.fabricData
})

const formattedTags = computed(() => {
  if (!store.formData.opinion_tags) return []
  return store.formData.opinion_tags
    .split(',')
    .map(tag => tag.trim())
    .filter(tag => tag)
})

// 获取文件名
const getFileName = (file) => {
  if (!file) return ''
  
  if (file instanceof File) {
    return file.name
  }
  
  if (typeof file === 'string') {
    return file.split('/').pop() || file
  }
  
  if (file.name) {
    return file.name
  }
  
  return '未知文件'
}

// 返回修改
const goBack = () => {
  if (store.prevStep()) {
    router.push(`/restoration-flow/${store.workflowId}/image-edit`)
  }
}

// 处理提交
const handleSubmit = async () => {
  try {
    // 最后确认
    const confirmed = confirm('确认提交修复申请吗？提交后将无法修改。')
    if (!confirmed) return
    
    // 提交表单
    const success = await store.submitFlow()
    
    if (success) {
      // 跳转到成功页面
      router.push(`/restoration-flow/${store.workflowId}/success`)
    }
  } catch (error) {
    console.error('提交失败:', error)
    MessagePlugin.error('提交失败，请重试')
  }
}

// 更新当前时间
const updateCurrentTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

onMounted(() => {
  updateCurrentTime()
  
  // 每秒更新时间
  const timer = setInterval(updateCurrentTime, 1000)
  
  // 组件卸载时清理定时器
  onUnmounted(() => {
    clearInterval(timer)
  })
})
</script>

<style scoped>
.confirm-page {
  padding: 16px;
  max-width: 1000px;
  margin: 0 auto;
  height: calc(100vh - 200px);
  overflow-y: auto;
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

.confirm-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

.info-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.image-info {
  display: flex;
  gap: 24px;
}

.image-preview {
  flex-shrink: 0;
}

.preview-container {
  position: relative;
  width: 200px;
  height: 150px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
}

.image-details {
  flex: 1;
}

.detail-item {
  margin-bottom: 16px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-item strong {
  color: #374151;
  display: block;
  margin-bottom: 4px;
}

.detail-content {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid #0052d9;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #0052d9;
  font-size: 14px;
}

.no-data {
  color: #9ca3af;
  font-style: italic;
  margin: 0;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.restoration-info,
.other-info,
.edit-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.edit-preview {
  margin-top: 16px;
}

.edited-image-container {
  margin-top: 8px;
  max-width: 300px;
}

.edited-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.submit-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 2px solid #0052d9;
  flex-shrink: 0;
  margin-top: auto;
}

.submit-warning {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 16px;
  background: #fef3c7;
  border-radius: 6px;
  color: #d97706;
  margin-bottom: 20px;
}

.submit-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .image-info {
    flex-direction: column;
  }
  
  .preview-container {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }
  
  .submit-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .submit-actions > * {
    width: 100%;
  }
  
  .edited-image-container {
    max-width: 100%;
  }
}
</style>

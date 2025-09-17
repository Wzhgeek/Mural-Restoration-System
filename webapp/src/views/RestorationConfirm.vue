<template>
  <div class="confirm-page">
    <div class="page-header">
      <h3>确认提交信息</h3>
      <p>请仔细核对所有信息，确认无误后提交任务表单</p>
    </div>
    
    <div class="confirm-container">
      <!-- 统一信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <h4>提交信息确认</h4>
        </div>
        <div class="card-content">
          <!-- 基本信息 -->
          <div class="section">
            <h5 class="section-title">基本信息</h5>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">工作流ID</span>
                <span class="value">{{ store.workflowId }}</span>
              </div>
              <div class="info-item">
                <span class="label">提交时间</span>
                <span class="value">{{ currentTime }}</span>
              </div>
              <div class="info-item">
                <span class="label">保密协议</span>
                <t-tag theme="success" variant="light" size="small">已同意</t-tag>
              </div>
            </div>
          </div>
          
          <!-- 图片信息 -->
          <div class="section" v-if="imagePreview || store.formData.image_desc || store.formData.image_desc_file">
            <h5 class="section-title">壁画图片信息</h5>
            <div class="image-section">
              <div class="image-preview" v-if="imagePreview">
                <img :src="imagePreview" alt="壁画图片预览" class="preview-image" />
                <t-tag v-if="hasImageEdit" theme="primary" variant="light" size="small" class="edit-tag">已编辑</t-tag>
              </div>
              
              <div class="content-section">
                <div class="content-item" v-if="store.formData.image_desc">
                  <span class="label">图片描述</span>
                  <div class="content-text">{{ store.formData.image_desc }}</div>
                </div>
                
                <div class="content-item" v-if="store.formData.image_desc_file">
                  <span class="label">图片描述附件</span>
                  <div class="file-item">
                    <t-icon name="attach" size="14px" />
                    <span>{{ getFileName(store.formData.image_desc_file) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 修复方案信息 -->
          <div class="section" v-if="store.formData.restoration_opinion || formattedTags.length > 0 || store.formData.opinion_file">
            <h5 class="section-title">任务方案信息</h5>
            <div class="content-item" v-if="store.formData.restoration_opinion">
              <span class="label">任务意见</span>
              <div class="content-text">{{ store.formData.restoration_opinion }}</div>
            </div>
            
            <div class="content-item" v-if="formattedTags.length > 0">
              <span class="label">任务标签</span>
              <div class="tags-list">
                <t-tag 
                  v-for="tag in formattedTags" 
                  :key="tag" 
                  theme="primary" 
                  variant="light"
                  size="small"
                >
                  {{ tag }}
                </t-tag>
              </div>
            </div>
            
            <div class="content-item" v-if="store.formData.opinion_file">
              <span class="label">任务意见附件</span>
              <div class="file-item">
                <t-icon name="attach" size="14px" />
                <span>{{ getFileName(store.formData.opinion_file) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 其他信息 -->
          <div class="section" v-if="store.formData.remark || store.formData.attachment_file">
            <h5 class="section-title">其他信息</h5>
            <div class="content-item" v-if="store.formData.remark">
              <span class="label">备注说明</span>
              <div class="content-text">{{ store.formData.remark }}</div>
            </div>
            
            <div class="content-item" v-if="store.formData.attachment_file">
              <span class="label">其他附件</span>
              <div class="file-item">
                <t-icon name="attach" size="14px" />
                <span>{{ getFileName(store.formData.attachment_file) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 图片编辑信息 -->
          <div class="section" v-if="hasImageEdit">
            <h5 class="section-title">图片编辑</h5>
            <div class="content-item">
              <span class="label">编辑状态</span>
              <t-tag theme="success" variant="light" size="small">已进行图片编辑</t-tag>
            </div>
            
            <div class="content-item" v-if="store.imageEditData.editedImage">
              <span class="label">编辑后预览</span>
              <div class="edited-preview">
                <img :src="store.imageEditData.editedImage" alt="编辑后图片" class="edited-image" />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 提交确认 -->
      <div class="submit-section">
        <div class="submit-warning">
          <t-icon name="info-circle" />
          <span>请确认以上信息无误。提交后将无法修改，系统将开始处理您的任务申请。</span>
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
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 200px);
  background: #fff;
}

.page-header {
  text-align: center;
  margin-bottom: 20px;
}

.page-header h3 {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 6px 0;
}

.page-header p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.confirm-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
  width: 100%;
}

/* 信息卡片样式 */
.info-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  background: #f8f9fa;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.card-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.card-content {
  padding: 16px;
}

/* 基本信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
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

/* 图片区域 */
.image-section {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.image-preview {
  position: relative;
  flex-shrink: 0;
  width: 120px;
  height: 90px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.edit-tag {
  position: absolute;
  top: 4px;
  right: 4px;
}

.content-section {
  flex: 1;
  min-width: 0;
}

/* 章节样式 */
.section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 12px 0;
  padding-bottom: 6px;
  border-bottom: 2px solid #0052d9;
  display: inline-block;
}

/* 内容项样式 */
.content-item {
  margin-bottom: 12px;
}

.content-item:last-child {
  margin-bottom: 0;
}

.content-item .label {
  display: block;
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.content-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #0052d9;
  word-break: break-word;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #0052d9;
  font-size: 14px;
}

.empty-text {
  color: #9ca3af;
  font-style: italic;
  font-size: 14px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

/* 编辑后图片预览 */
.edited-preview {
  margin-top: 8px;
  max-width: 200px;
}

.edited-image {
  width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 提交区域 */
.submit-section {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  border: 2px solid #0052d9;
  margin-top: 8px;
}

.submit-warning {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: #fef3c7;
  border-radius: 6px;
  color: #d97706;
  margin-bottom: 16px;
  font-size: 14px;
}



/* 响应式设计 */
@media (max-width: 768px) {
  .confirm-page {
    padding: 16px;
  }
  
  .image-section {
    flex-direction: column;
  }
  
  .image-preview {
    width: 100%;
    max-width: 200px;
    height: 120px;
    margin: 0 auto;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  
  .edited-preview {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .confirm-container {
    gap: 12px;
  }
  
  .card-content {
    padding: 12px;
  }
  
  .card-header {
    padding: 10px 12px;
  }
}
</style>

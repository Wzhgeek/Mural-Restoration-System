<template>
  <div class="form-page">
    <div class="page-header">
      <h3>填写修复表单</h3>
      <p>请详细填写壁画修复相关信息，表单将自动保存</p>
    </div>
    
    <t-card class="form-card">
      <t-form 
        ref="formRef" 
        :model="formData" 
        :rules="formRules" 
        layout="vertical"
        @change="handleFormChange"
      >
        <t-row :gutter="[24, 16]">
          <!-- 左列 - 图片相关 -->
          <t-col :xs="24" :md="12">
            <h4 class="section-title">壁画图片信息</h4>
            
            <t-form-item label="壁画图片" name="image_file" help="支持 JPG、PNG 格式，大小不超过 10MB">
              <t-upload
                v-model="formData.image_file"
                :auto-upload="false"
                accept="image/*"
                :max="1"
                :size-limit="10 * 1024 * 1024"
                @change="handleImageChange"
                theme="image"
              >
                <template #upload-dragger>
                  <div class="upload-dragger">
                    <t-icon name="cloud-upload" size="48px" />
                    <p>点击或拖拽上传壁画图片</p>
                    <p class="upload-tip">建议上传高清图片以便后续编辑</p>
                  </div>
                </template>
              </t-upload>
            </t-form-item>
            
            <t-form-item label="图片描述" name="image_desc" help="描述壁画的内容、状态、损坏情况等">
              <t-textarea 
                v-model="formData.image_desc" 
                placeholder="例如：此壁画位于石窟东壁，描绘佛陀说法场面，画面色彩较为鲜艳，局部有轻微剥落现象..."
                :autosize="{ minRows: 4, maxRows: 8 }"
                @change="handleFormChange"
              />
            </t-form-item>
            
            <t-form-item label="图片描述附件" help="可上传相关的文档、报告等">
              <t-upload
                v-model="formData.image_desc_file"
                :auto-upload="false"
                accept=".pdf,.doc,.docx,.txt"
                :max="1"
                :size-limit="20 * 1024 * 1024"
                @change="handleFormChange"
              >
                <template #upload-dragger>
                  <div class="upload-dragger-small">
                    <t-icon name="attach" size="24px" />
                    <span>上传相关文档</span>
                  </div>
                </template>
              </t-upload>
            </t-form-item>
          </t-col>
          
          <!-- 右列 - 修复相关 -->
          <t-col :xs="24" :md="12">
            <h4 class="section-title">修复方案信息</h4>
            
            <t-form-item label="修复意见" name="restoration_opinion" help="详细描述修复方案和建议">
              <t-textarea 
                v-model="formData.restoration_opinion" 
                placeholder="例如：建议先进行表面浮灰清理，然后使用XX材料进行加固处理，最后进行色彩补充..."
                :autosize="{ minRows: 4, maxRows: 8 }"
                @change="handleFormChange"
              />
            </t-form-item>
            
            <t-form-item label="修复标签" help="用逗号分隔多个标签">
              <t-input 
                v-model="formData.opinion_tags" 
                placeholder="浮灰清理,加固处理,色彩补充,结构修复"
                @change="handleFormChange"
              />
              <div class="tags-preview" v-if="previewTags.length > 0">
                <t-tag 
                  v-for="tag in previewTags" 
                  :key="tag" 
                  theme="primary" 
                  variant="light"
                  closable
                  @close="removeTag(tag)"
                >
                  {{ tag }}
                </t-tag>
              </div>
            </t-form-item>
            
            <t-form-item label="修复意见附件" help="可上传修复方案相关文档">
              <t-upload
                v-model="formData.opinion_file"
                :auto-upload="false"
                accept=".pdf,.doc,.docx,.txt"
                :max="1"
                :size-limit="20 * 1024 * 1024"
                @change="handleFormChange"
              >
                <template #upload-dragger>
                  <div class="upload-dragger-small">
                    <t-icon name="attach" size="24px" />
                    <span>上传方案文档</span>
                  </div>
                </template>
              </t-upload>
            </t-form-item>
          </t-col>
        </t-row>
        
        <!-- 底部区域 - 备注和其他附件 -->
        <t-row :gutter="[24, 16]">
          <t-col :xs="24" :md="12">
            <t-form-item label="备注说明" help="其他需要说明的内容">
              <t-textarea 
                v-model="formData.remark" 
                placeholder="请输入其他需要说明的内容..."
                :autosize="{ minRows: 3, maxRows: 6 }"
                @change="handleFormChange"
              />
            </t-form-item>
          </t-col>
          
          <t-col :xs="24" :md="12">
            <t-form-item label="其他附件" help="可上传其他相关文件">
              <t-upload
                v-model="formData.attachment_file"
                :auto-upload="false"
                :max="1"
                :size-limit="20 * 1024 * 1024"
                @change="handleFormChange"
              >
                <template #upload-dragger>
                  <div class="upload-dragger-small">
                    <t-icon name="attach" size="24px" />
                    <span>上传其他文件</span>
                  </div>
                </template>
              </t-upload>
            </t-form-item>
          </t-col>
        </t-row>
      </t-form>
      
      <!-- 表单状态提示 -->
      <div class="form-status">
        <div class="auto-save-tip">
          <t-icon name="check-circle" v-if="savedAt" />
          <t-icon name="time" v-else />
          <span v-if="savedAt">已自动保存 ({{ savedAt }})</span>
          <span v-else>表单将自动保存</span>
        </div>
        
        <div class="form-validation" v-if="!isFormValid">
          <t-icon name="info-circle" />
          <span>至少需要填写图片描述或修复意见才能继续</span>
        </div>
      </div>
    </t-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { useRestorationFlowStore } from '@/stores/restorationFlow'

/**
 * 修复表单页面
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const store = useRestorationFlowStore()

const formRef = ref(null)
const savedAt = ref('')
const saveTimer = ref(null)

// 表单数据
const formData = ref({
  image_file: [],
  image_desc: '',
  image_desc_file: [],
  restoration_opinion: '',
  opinion_tags: '',
  opinion_file: [],
  remark: '',
  attachment_file: []
})

// 表单验证规则
const formRules = {
  // 根据需求，图片和修复意见都是可选的，但至少需要一个
}

// 计算属性
const previewTags = computed(() => {
  if (!formData.value.opinion_tags) return []
  return formData.value.opinion_tags
    .split(',')
    .map(tag => tag.trim())
    .filter(tag => tag)
})

const isFormValid = computed(() => {
  return formData.value.image_desc || formData.value.restoration_opinion
})

// 从 store 初始化表单数据
const initFormData = () => {
  // 检查是否是新流程（store中没有数据）
  const isNewFlow = !store.formData.image_desc && 
                   !store.formData.restoration_opinion && 
                   !store.formData.opinion_tags && 
                   !store.formData.remark
  
  if (isNewFlow) {
    // 新流程，清空所有表单数据
    formData.value.image_desc = ''
    formData.value.restoration_opinion = ''
    formData.value.opinion_tags = ''
    formData.value.remark = ''
    formData.value.image_file = []
    formData.value.image_desc_file = []
    formData.value.opinion_file = []
    formData.value.attachment_file = []
    console.log('新流程，清空表单数据')
  } else {
    // 恢复已保存的表单数据
    formData.value.image_desc = store.formData.image_desc || ''
    formData.value.restoration_opinion = store.formData.restoration_opinion || ''
    formData.value.opinion_tags = store.formData.opinion_tags || ''
    formData.value.remark = store.formData.remark || ''
    
    // 文件字段保持为空数组，让用户重新上传
    formData.value.image_file = []
    formData.value.image_desc_file = []
    formData.value.opinion_file = []
    formData.value.attachment_file = []
    console.log('恢复已保存的表单数据')
  }
}

// 处理表单变化
const handleFormChange = () => {
  // 准备要保存的数据
  const dataToSave = {
    image_desc: formData.value.image_desc,
    restoration_opinion: formData.value.restoration_opinion,
    opinion_tags: formData.value.opinion_tags,
    remark: formData.value.remark
  }
  
  // 处理文件数据 - 只在文件变化时更新
  if (formData.value.image_file && formData.value.image_file.length > 0) {
    const file = formData.value.image_file[0]
    dataToSave.image_file = file.raw || file
    console.log('表单变化 - 更新图片文件:', dataToSave.image_file)
  }
  if (formData.value.image_desc_file && formData.value.image_desc_file.length > 0) {
    dataToSave.image_desc_file = formData.value.image_desc_file[0].raw || formData.value.image_desc_file[0]
  }
  if (formData.value.opinion_file && formData.value.opinion_file.length > 0) {
    dataToSave.opinion_file = formData.value.opinion_file[0].raw || formData.value.opinion_file[0]
  }
  if (formData.value.attachment_file && formData.value.attachment_file.length > 0) {
    dataToSave.attachment_file = formData.value.attachment_file[0].raw || formData.value.attachment_file[0]
  }
  
  // 更新 store
  store.updateFormData(dataToSave)
  
  // 防抖保存
  if (saveTimer.value) {
    clearTimeout(saveTimer.value)
  }
  
  saveTimer.value = setTimeout(() => {
    savedAt.value = new Date().toLocaleTimeString()
  }, 1000)
}

// 处理图片上传
const handleImageChange = (files) => {
  console.log('图片上传变化:', files)
  formData.value.image_file = files || []
  if (files && files.length > 0) {
    // 保存原始文件到 store，用于后续处理
    const file = files[0]
    const fileToSave = file.raw || file
    console.log('保存文件到store:', fileToSave)
    store.updateFormData({ 
      image_file: fileToSave 
    })
  }
  handleFormChange()
}

// 移除标签
const removeTag = (tagToRemove) => {
  const tags = previewTags.value.filter(tag => tag !== tagToRemove)
  formData.value.opinion_tags = tags.join(', ')
  handleFormChange()
}

// 监听表单数据变化 - 只监听非文件字段
watch(
  () => ({
    image_desc: formData.value.image_desc,
    restoration_opinion: formData.value.restoration_opinion,
    opinion_tags: formData.value.opinion_tags,
    remark: formData.value.remark
  }),
  () => {
    handleFormChange()
  },
  { deep: true }
)

onMounted(() => {
  initFormData()
})
</script>

<style scoped>
.form-page {
  max-width: 1000px;
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

.form-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #0052d9;
}

.upload-dragger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background: #f9fafb;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-dragger:hover {
  border-color: #0052d9;
  background: #f0f7ff;
}

.upload-dragger-small {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  border: 2px dashed #d1d5db;
  border-radius: 6px;
  background: #f9fafb;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-dragger-small:hover {
  border-color: #0052d9;
  background: #f0f7ff;
}

.upload-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.tags-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.form-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.auto-save-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #10b981;
  font-size: 14px;
}

.form-validation {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #f59e0b;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-status {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .upload-dragger {
    padding: 24px 16px;
  }
  
  .section-title {
    font-size: 14px;
  }
}
</style>

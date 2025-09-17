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
        <!-- 图片信息部分 -->
        <div class="section">
          <div class="section-bar"><span class="section-title">壁画图片信息</span></div>

          <t-form-item label="壁画图片" name="image_file" help="支持 JPG、PNG 格式，单张≤10MB，最多 9 张">
            <t-upload
              v-model:files="formData.image_file"
              theme="image"
              accept="image/*"
              :max="9"
              multiple
              :auto-upload="false"
              :before-upload="beforeImgUpload"
              @change="handleImageChange"
              class="img-upload"
            />
          </t-form-item>

          <t-form-item label="图片描述" name="image_desc">
            <t-textarea
              v-model="formData.image_desc"
              placeholder="请输入图片描述..."
              :autosize="{ minRows: 4, maxRows: 8 }"
              @change="handleFormChange"
            />
    
          </t-form-item>

          <t-form-item label="图片描述附件">
            <t-upload
              v-model="formData.image_desc_file"
              theme="file"
              :auto-upload="false"
              accept=".pdf,.doc,.docx,.txt"
              :max="1"
              :size-limit="20 * 1024 * 1024"
              @change="handleFormChange"
              class="file-upload"
            >
              <template #trigger>
                <t-button variant="outline" size="small">选择文件</t-button>
              </template>
            </t-upload>
          </t-form-item>
        </div>

        <!-- 视频信息部分（保留） -->
        <div class="section">
          <div class="section-bar"><span class="section-title">壁画视频信息</span></div>

          <t-form-item label="壁画视频" name="video_file" help="支持 MP4、AVI、MOV、MKV、WebM 格式，单个≤100MB，最多 5 个">
            <t-upload
              ref="videoUploadRef"
              v-model:files="formData.video_file"
              theme="image"
              accept="video/*,.mp4,.avi,.mov,.mkv,.webm,.m4v"
              :max="5"
              multiple
              :auto-upload="false"
              :before-upload="beforeVideoUpload"
              @change="handleVideoChange"
              :use-trigger-slot="true"
              class="video-upload"
            >
              <template #trigger>
                <!-- 改成 button + 手动触发 -->
                <button type="button" class="upload-trigger" @click="openVideoPicker">
                  <t-icon name="video-camera" size="20px" />
                  <span>点击上传视频</span>
                </button>
              </template>
            </t-upload>
          </t-form-item>

          <t-form-item label="视频描述" name="video_desc">
            <t-textarea
              v-model="formData.video_desc"
              placeholder="请输入视频描述..."
              :autosize="{ minRows: 4, maxRows: 8 }"
              @change="handleFormChange"
            />

          </t-form-item>

          <t-form-item label="视频描述附件">
            <t-upload
              v-model="formData.video_desc_file"
              theme="file"
              :auto-upload="false"
              accept=".pdf,.doc,.docx,.txt"
              :max="1"
              :size-limit="20 * 1024 * 1024"
              @change="handleFormChange"
              class="file-upload"
            >
              <template #trigger>
                <t-button variant="outline" size="small">选择文件</t-button>
              </template>
            </t-upload>
          </t-form-item>
        </div>

        <!-- 修复方案信息部分 -->
        <div class="section">
          <div class="section-bar"><span class="section-title">修复方案信息</span></div>

          <t-form-item label="修复意见" name="restoration_opinion">
            <t-textarea
              v-model="formData.restoration_opinion"
              placeholder="请输入修复意见..."
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

            <div class="tags-preview" v-if="previewTags.length">
              <t-tag
                v-for="tag in previewTags"
                :key="tag"
                theme="primary"
                variant="light"
                closable
                @close="removeTag(tag)"
              >{{ tag }}</t-tag>
            </div>
          </t-form-item>

          <t-form-item label="修复意见附件">
            <t-upload
              v-model="formData.opinion_file"
              theme="file"
              :auto-upload="false"
              accept=".pdf,.doc,.docx,.txt"
              :max="1"
              :size-limit="20 * 1024 * 1024"
              @change="handleFormChange"
              class="file-upload"
            >
              <template #trigger>
                <t-button variant="outline" size="small">选择文件</t-button>
              </template>
            </t-upload>
          </t-form-item>

          <t-form-item label="备注说明" help="其他需要说明的内容">
            <t-textarea
              v-model="formData.remark"
              placeholder="请输入其他需要说明的内容..."
              :autosize="{ minRows: 3, maxRows: 6 }"
              @change="handleFormChange"
            />
          </t-form-item>

          <t-form-item label="其他附件">
            <t-upload
              v-model="formData.attachment_file"
              theme="file"
              :auto-upload="false"
              :max="1"
              :size-limit="20 * 1024 * 1024"
              @change="handleFormChange"
              class="file-upload"
            >
              <template #trigger>
                <t-button variant="outline" size="small">选择文件</t-button>
              </template>
            </t-upload>
          </t-form-item>
        </div>

        <!-- 质量检测部分 -->
        <div class="section">
          <div class="section-bar"><span class="section-title">质量检测</span></div>
          
          <t-form-item label="质量自检确认" name="quality_check" required>
            <div class="quality-check-list">
              <t-checkbox 
                :checked="formData.quality_check.includes('content_accuracy')"
                value="content_accuracy"
                @change="handleQualityCheckChange"
              >
                内容准确性：我已仔细核对所有填写内容，确保信息准确无误
              </t-checkbox>
              <t-checkbox 
                :checked="formData.quality_check.includes('file_quality')"
                value="file_quality"
                @change="handleQualityCheckChange"
              >
                文件质量：我已确认上传的图片和视频质量清晰，符合要求
              </t-checkbox>
              <t-checkbox 
                :checked="formData.quality_check.includes('description_complete')"
                value="description_complete"
                @change="handleQualityCheckChange"
              >
                描述完整：我已提供详细的图片描述和修复意见
              </t-checkbox>
              <t-checkbox 
                :checked="formData.quality_check.includes('data_integrity')"
                value="data_integrity"
                @change="handleQualityCheckChange"
              >
                数据完整性：我已确认所有必要信息都已填写完整
              </t-checkbox>
            </div>
          </t-form-item>

          <t-form-item label="质量保证声明" name="quality_statement">
            <t-textarea
              v-model="formData.quality_statement"
              placeholder="请在此声明您对提交内容质量的保证，包括检查过程和确认事项..."
              :autosize="{ minRows: 3, maxRows: 6 }"
              @change="handleFormChange"
            />
          </t-form-item>
        </div>

        <!-- 操作人员信息部分 -->
        <div class="section">
          <div class="section-bar"><span class="section-title">操作人员信息</span></div>
          
          <t-form-item label="提交人员单位" name="submitter_unit">
            <t-input
              v-model="formData.submitter_unit"
              placeholder="请输入您的单位名称"
              @change="handleFormChange"
            />
          </t-form-item>

          <t-form-item label="操作人员单位" name="operator_unit">
            <t-input
              v-model="formData.operator_unit"
              placeholder="请输入操作人员单位名称"
              @change="handleFormChange"
            />
          </t-form-item>
        </div>
      </t-form>

      <!-- 状态 -->
      <div class="form-status">
        <div class="auto-save-tip">
          <t-icon name="check-circle" v-if="savedAt" />
          <t-icon name="time" v-else />
          <span v-if="savedAt">已自动保存 ({{ savedAt }})</span>
          <span v-else>表单将自动保存</span>
        </div>
        <div class="form-validation" v-if="!isFormValid">
          <t-icon name="info-circle" />
          <span>{{ validationMessage }}</span>
        </div>
        <div class="form-validation success" v-else>
          <t-icon name="check-circle" />
          <span>{{ validationMessage }}</span>
        </div>
        </div>
      </t-card>

    </div>

    <!-- 文件重命名对话框 -->
    <t-dialog
      v-model:visible="showRenameDialog"
      header="重命名文件"
      width="400px"
      :footer="false"
      v-if="renameFileInfo"
    >
      <div class="rename-dialog-content">
        <div class="file-info">
          <t-icon :name="renameFileInfo?.type === 'image' ? 'image' : 'video-camera'" size="24px" />
          <span class="file-type">{{ renameFileInfo?.type === 'image' ? '图片' : '视频' }}</span>
          <span class="original-name">{{ renameFileInfo?.originalName || '' }}</span>
        </div>
        
        <t-form-item label="新文件名" required>
          <t-input
            v-model="newFileName"
            placeholder="请输入新的文件名"
            :maxlength="50"
          />
        </t-form-item>
        
        <div class="file-extension-tip">
          <t-icon name="info-circle" />
          <span>请保持文件扩展名不变 ({{ renameFileInfo?.extension || '' }})</span>
        </div>
      </div>
      
      <div class="dialog-footer">
        <t-space>
          <t-button theme="default" @click="cancelRename">取消</t-button>
          <t-button theme="primary" @click="confirmRename" :disabled="!newFileName.trim()">确认</t-button>
        </t-space>
      </div>
    </t-dialog>
  </template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { useRestorationFlowStore } from '@/stores/restorationFlow'

const store = useRestorationFlowStore()
const formRef = ref(null)
const videoUploadRef = ref(null)
const savedAt = ref('')
const saveTimer = ref(null)

// 重命名对话框相关
const showRenameDialog = ref(false)
const newFileName = ref('')
const renameFileInfo = ref({
  type: '', // 'image' 或 'video'
  originalName: '',
  extension: '',
  file: null,
  fileList: null,
  index: -1
})


const formData = ref({
  image_file: [],
  image_desc: '',
  image_desc_file: [],
  video_file: [],
  video_desc: '',
  video_desc_file: [],
  restoration_opinion: '',
  opinion_tags: '',
  opinion_file: [],
  remark: '',
  attachment_file: [],
  quality_check: [],
  quality_statement: '',
  submitter_unit: '',
  operator_unit: ''
})

const formRules = {}

const previewTags = computed(() => {
  if (!formData.value.opinion_tags) return []
  return formData.value.opinion_tags.split(',').map(t => t.trim()).filter(Boolean)
})

// 表单验证逻辑
const isFormValid = computed(() => {
  // 必须填写所有必要信息
  const hasImageDesc = !!formData.value.image_desc?.trim()
  const hasVideoDesc = !!formData.value.video_desc?.trim()
  const hasRestorationOpinion = !!formData.value.restoration_opinion?.trim()
  const hasOpinionTags = formData.value.restoration_opinion?.trim() ? !!formData.value.opinion_tags?.trim() : true
  
  // 至少需要上传图片或视频中的一种
  const hasImageFiles = formData.value.image_file && formData.value.image_file.length > 0
  const hasVideoFiles = formData.value.video_file && formData.value.video_file.length > 0
  const hasFiles = hasImageFiles || hasVideoFiles
  
  // 质量检测必须全部通过
  const hasQualityCheck = formData.value.quality_check && formData.value.quality_check.length === 4
  
  // 必须填写提交人员单位
  const hasSubmitterUnit = !!formData.value.submitter_unit?.trim()
  
  return hasImageDesc && hasVideoDesc && hasRestorationOpinion && hasOpinionTags && hasFiles && hasQualityCheck && hasSubmitterUnit
})

// 获取详细的验证状态信息
const validationStatus = computed(() => {
  const status = {
    hasImageDesc: !!formData.value.image_desc?.trim(),
    hasVideoDesc: !!formData.value.video_desc?.trim(),
    hasRestorationOpinion: !!formData.value.restoration_opinion?.trim(),
    hasOpinionTags: formData.value.restoration_opinion?.trim() ? !!formData.value.opinion_tags?.trim() : true,
    hasImageFiles: formData.value.image_file && formData.value.image_file.length > 0,
    hasVideoFiles: formData.value.video_file && formData.value.video_file.length > 0,
    hasFiles: (formData.value.image_file && formData.value.image_file.length > 0) || (formData.value.video_file && formData.value.video_file.length > 0),
    hasQualityCheck: formData.value.quality_check && formData.value.quality_check.length === 4,
    hasSubmitterUnit: !!formData.value.submitter_unit?.trim()
  }
  
  return status
})

// 获取验证提示信息
const validationMessage = computed(() => {
  if (isFormValid.value) {
    return '表单填写完整，可以继续下一步'
  }
  
  const status = validationStatus.value
  const missingItems = []
  
  if (!status.hasImageDesc) missingItems.push('图片描述')
  if (!status.hasVideoDesc) missingItems.push('视频描述')
  if (!status.hasRestorationOpinion) missingItems.push('修复意见')
  if (!status.hasOpinionTags) missingItems.push('修复标签')
  if (!status.hasFiles) missingItems.push('至少上传一张图片或一个视频')
  if (!status.hasQualityCheck) missingItems.push('质量自检确认')
  if (!status.hasSubmitterUnit) missingItems.push('提交人员单位')
  
  return `请完成以下必填项：${missingItems.join('、')}`
})

const initFormData = async () => {
  const isNewFlow =
    !store.formData.image_desc &&
    !store.formData.video_desc &&
    !store.formData.restoration_opinion &&
    !store.formData.opinion_tags &&
    !store.formData.remark

  if (isNewFlow) {
    formData.value.image_desc = ''
    formData.value.video_desc = ''
    formData.value.restoration_opinion = ''
    formData.value.opinion_tags = ''
    formData.value.remark = ''
    formData.value.image_file = []
    formData.value.image_desc_file = []
    formData.value.video_file = []
    formData.value.video_desc_file = []
    formData.value.opinion_file = []
    formData.value.attachment_file = []
    formData.value.quality_check = []
    formData.value.quality_statement = ''
    formData.value.submitter_unit = ''
    formData.value.operator_unit = ''
  } else {
    formData.value.image_desc = store.formData.image_desc || ''
    formData.value.video_desc = store.formData.video_desc || ''
    formData.value.restoration_opinion = store.formData.restoration_opinion || ''
    formData.value.opinion_tags = store.formData.opinion_tags || ''
    formData.value.remark = store.formData.remark || ''
    formData.value.quality_check = store.formData.quality_check || []
    formData.value.quality_statement = store.formData.quality_statement || ''
    formData.value.submitter_unit = store.formData.submitter_unit || ''
    formData.value.operator_unit = store.formData.operator_unit || ''
    
    // 恢复文件数据，保持用户已上传的文件
    formData.value.image_file = store.formData.image_file || []
    formData.value.image_desc_file = store.formData.image_desc_file || []
    formData.value.video_file = store.formData.video_file || []
    formData.value.video_desc_file = store.formData.video_desc_file || []
    formData.value.opinion_file = store.formData.opinion_file || []
    formData.value.attachment_file = store.formData.attachment_file || []
    
    // 恢复视频缩略图显示
    if (formData.value.video_file && formData.value.video_file.length > 0) {
      await restoreVideoThumbnails()
    }
  }
}

// 处理质量检测复选框变化
const handleQualityCheckChange = (checked, context) => {
  const value = context.value
  if (checked) {
    if (!formData.value.quality_check.includes(value)) {
      formData.value.quality_check.push(value)
    }
  } else {
    const index = formData.value.quality_check.indexOf(value)
    if (index > -1) {
      formData.value.quality_check.splice(index, 1)
    }
  }
  handleFormChange()
}

const handleFormChange = () => {
  const dataToSave = {
    image_desc: formData.value.image_desc,
    video_desc: formData.value.video_desc,
    restoration_opinion: formData.value.restoration_opinion,
    opinion_tags: formData.value.opinion_tags,
    remark: formData.value.remark,
    quality_check: formData.value.quality_check,
    quality_statement: formData.value.quality_statement,
    submitter_unit: formData.value.submitter_unit,
    operator_unit: formData.value.operator_unit
  }
  if (Array.isArray(formData.value.image_file) && formData.value.image_file.length) {
    dataToSave.image_file = formData.value.image_file.map(f => {
      // 保留完整的文件对象信息，包括URL
      return {
        ...f,
        raw: f.raw || f,
        url: f.url || (f.raw ? URL.createObjectURL(f.raw) : null),
        uid: f.uid || f.id || Date.now() + Math.random(),
        // 确保文件对象能够被正确序列化
        name: f.name,
        size: f.size,
        type: f.type,
        lastModified: f.lastModified
      }
    })
  }
  if (Array.isArray(formData.value.image_desc_file) && formData.value.image_desc_file.length) {
    dataToSave.image_desc_file = formData.value.image_desc_file[0].raw || formData.value.image_desc_file[0]
  }
  if (Array.isArray(formData.value.video_file) && formData.value.video_file.length) {
    dataToSave.video_file = formData.value.video_file.map(f => {
      // 保留完整的视频文件对象信息，包括URL和缩略图
      return {
        ...f,
        raw: f.raw || f,
        url: f.url || (f.raw ? URL.createObjectURL(f.raw) : null),
        thumbUrl: f.thumbUrl || f.url, // 保留缩略图URL
        uid: f.uid || f.id || Date.now() + Math.random(),
        // 确保文件对象能够被正确序列化
        name: f.name,
        size: f.size,
        type: f.type,
        lastModified: f.lastModified,
        // 保留视频缩略图生成状态
        _posterReady: f._posterReady || false
      }
    })
  }
  if (Array.isArray(formData.value.video_desc_file) && formData.value.video_desc_file.length) {
    dataToSave.video_desc_file = formData.value.video_desc_file[0].raw || formData.value.video_desc_file[0]
  }
  if (Array.isArray(formData.value.opinion_file) && formData.value.opinion_file.length) {
    dataToSave.opinion_file = formData.value.opinion_file[0].raw || formData.value.opinion_file[0]
  }
  if (Array.isArray(formData.value.attachment_file) && formData.value.attachment_file.length) {
    dataToSave.attachment_file = formData.value.attachment_file[0].raw || formData.value.attachment_file[0]
  }

  store.updateFormData(dataToSave)

  if (saveTimer.value) clearTimeout(saveTimer.value)
  saveTimer.value = setTimeout(() => {
    savedAt.value = new Date().toLocaleTimeString()
  }, 1000)
}

const handleImageChange = (fileList) => {
  // 检查是否有新上传的文件需要重命名
  if (fileList && fileList.length > 0) {
    const newFiles = fileList.filter(file => !file._renamed)
    if (newFiles.length > 0) {
      // 显示重命名对话框
      showRenameDialogForFile(newFiles[0], 'image', formData.value.image_file, fileList.length - 1)
      return
    }
  }
  
  // v-model:files 已经把 t-upload 的 UploadFile[] 写进 formData.image_file
  handleFormChange()
}

// 生成视频首帧缩略图
const generateVideoThumbnail = (file) => {
  return new Promise((resolve) => {
    const video = document.createElement('video')
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    video.preload = 'metadata'
    video.muted = true
    video.crossOrigin = 'anonymous'
    video.src = URL.createObjectURL(file)
    
    // 设置超时，避免长时间等待
    const timeout = setTimeout(() => {
      URL.revokeObjectURL(video.src)
      resolve('')
    }, 10000) // 10秒超时
    
    video.onloadedmetadata = () => {
      try {
        // 设置视频到第1秒
        video.currentTime = 1
      } catch (error) {
        clearTimeout(timeout)
        URL.revokeObjectURL(video.src)
        resolve('')
      }
    }
    
    video.onseeked = () => {
      try {
        // 设置canvas尺寸
        canvas.width = 160
        canvas.height = 100
        
        // 绘制视频帧到canvas
        ctx.drawImage(video, 0, 0, 160, 100)
        
        // 转换为base64图片
        const thumbnail = canvas.toDataURL('image/jpeg', 0.8)
        
        clearTimeout(timeout)
        URL.revokeObjectURL(video.src)
        
        resolve(thumbnail)
      } catch (error) {
        clearTimeout(timeout)
        URL.revokeObjectURL(video.src)
        resolve('')
      }
    }
    
    video.onerror = () => {
      clearTimeout(timeout)
      URL.revokeObjectURL(video.src)
      resolve('')
    }
  })
}

const openVideoPicker = () => {
  // 直接点隐藏 input，兼容所有版本
  const root = videoUploadRef.value?.$el || videoUploadRef.value?.$refs?.uploadRef || null
  const input = root?.querySelector?.('input[type="file"]')
  if (input) input.click()
}

const handleVideoChange = async (fileList) => {
  const list = formData.value.video_file || []
  
  // 检查是否有新上传的文件需要重命名
  if (fileList && fileList.length > 0) {
    const newFiles = fileList.filter(file => !file._renamed)
    if (newFiles.length > 0) {
      // 显示重命名对话框
      showRenameDialogForFile(newFiles[0], 'video', formData.value.video_file, fileList.length - 1)
      return
    }
  }
  
  // 为每个视频文件生成缩略图
  for (const item of list) {
    const file = item.raw || item
    if (!item._posterReady && file && /^video\//.test(file.type || '')) {
      // 立即设置状态为处理中，避免显示"图片加载中"
      item.status = 'progress'
      item._posterReady = false
      
      // 异步生成缩略图，不阻塞UI
      generateVideoThumbnail(file).then(poster => {
        if (poster) {
          item.url = poster                      // 用首帧当封面
          item.thumbUrl = poster                 // 同时保存到 thumbUrl 以备后用
        }
        item.status = 'success'                            // 关键：去掉"图片加载中"
        item._posterReady = true                           // 标记已完成
        
        // 触发表单更新
        handleFormChange()
      }).catch(error => {
        console.warn('生成视频缩略图失败:', error)
        item.url = ''
        item.thumbUrl = ''
        item.status = 'success'                            // 即使失败也设为成功状态
        item._posterReady = true
        
        // 触发表单更新
        handleFormChange()
      })
    }
  }
  
  // 立即触发表单更新，保存文件信息
  handleFormChange()
}

// 恢复视频缩略图显示
const restoreVideoThumbnails = async () => {
  const list = formData.value.video_file || []
  
  for (const item of list) {
    // 如果已经有缩略图URL，直接使用
    if (item.thumbUrl && item._posterReady) {
      item.url = item.thumbUrl
      item.status = 'success'
      continue
    }
    
    // 如果没有缩略图，尝试重新生成
    const file = item.raw || item
    if (file && /^video\//.test(file.type || '') && !item._posterReady) {
      // 设置状态为处理中，避免显示"图片加载中"
      item.status = 'progress'
      
      try {
        const poster = await generateVideoThumbnail(file)
        if (poster) {
          item.url = poster
          item.thumbUrl = poster
          item.status = 'success'
          item._posterReady = true
        } else {
          item.status = 'success'
          item._posterReady = true
        }
      } catch (error) {
        console.warn('恢复视频缩略图失败:', error)
        item.status = 'success'
        item._posterReady = true
      }
    }
  }
}


// 类型/大小校验
const beforeImgUpload = (file) => {
  if (!file || !file.type) {
    MessagePlugin.warning('文件类型无效')
    return false
  }
  const okType = /^image\//.test(file.type)
  const okSize = file.size <= 10 * 1024 * 1024
  if (!okType || !okSize) {
    MessagePlugin.warning('仅支持 JPG/PNG 且单张 ≤ 10MB')
    return false
  }
  return true
}

const beforeVideoUpload = (file) => {
  if (!file || !file.type) {
    MessagePlugin.warning('文件类型无效')
    return false
  }
  const okType = /^video\//.test(file.type) || /\.(mp4|avi|mov|mkv|webm|m4v)$/i.test(file.name || '')
  const okSize = file.size <= 100 * 1024 * 1024
  if (!okType || !okSize) {
    MessagePlugin.warning('仅支持 MP4/AVI/MOV/MKV/WebM 且单个 ≤ 100MB')
    return false
  }
  return true
}


const removeTag = tag => {
  const tags = previewTags.value.filter(t => t !== tag)
  formData.value.opinion_tags = tags.join(', ')
  handleFormChange()
}

// 显示重命名对话框
const showRenameDialogForFile = (file, type, fileList, index) => {
  const originalName = file.name || file.raw?.name || '未命名文件'
  const extension = originalName.split('.').pop() || ''
  const nameWithoutExt = originalName.replace(/\.[^/.]+$/, '')
  
  renameFileInfo.value = {
    type,
    originalName,
    extension,
    file,
    fileList,
    index
  }
  
  newFileName.value = nameWithoutExt
  showRenameDialog.value = true
}


// 确认重命名
const confirmRename = () => {
  if (!newFileName.value.trim()) {
    MessagePlugin.warning('请输入文件名')
    return
  }
  
  if (!renameFileInfo.value) {
    MessagePlugin.error('文件信息丢失，请重新上传')
    showRenameDialog.value = false
    return
  }
  
  const { file, fileList, index, extension } = renameFileInfo.value
  const newName = `${newFileName.value.trim()}.${extension}`
  
  // 检查文件名是否重复
  const existingNames = fileList.map(f => f.name || f.raw?.name).filter(Boolean)
  if (existingNames.includes(newName)) {
    MessagePlugin.warning('文件名已存在，请使用其他名称')
    return
  }
  
  // 更新文件名 - 创建新的 File 对象
  if (file.raw) {
    // 创建新的 File 对象，保持其他属性不变
    const newFile = new File([file.raw], newName, {
      type: file.raw.type,
      lastModified: file.raw.lastModified
    })
    file.raw = newFile
  }
  
  // 更新显示名称
  file.name = newName
  file._renamed = true
  
  MessagePlugin.success(`文件已重命名为: ${newName}`)
  
  // 关闭对话框
  showRenameDialog.value = false
  newFileName.value = ''
  
  // 触发表单更新
  handleFormChange()
  
  // 如果是视频文件，继续处理缩略图生成
  if (renameFileInfo.value.type === 'video') {
    handleVideoThumbnailGeneration()
  }
}

// 取消重命名
const cancelRename = () => {
  if (!renameFileInfo.value) {
    showRenameDialog.value = false
    newFileName.value = ''
    return
  }
  
  const { file } = renameFileInfo.value
  
  // 从文件列表中移除未重命名的文件
  if (renameFileInfo.value.type === 'image') {
    const index = formData.value.image_file.findIndex(f => f === file)
    if (index > -1) {
      formData.value.image_file.splice(index, 1)
    }
  } else if (renameFileInfo.value.type === 'video') {
    const index = formData.value.video_file.findIndex(f => f === file)
    if (index > -1) {
      formData.value.video_file.splice(index, 1)
    }
  }
  
  showRenameDialog.value = false
  newFileName.value = ''
  
  // 触发表单更新
  handleFormChange()
}

// 处理视频缩略图生成（重命名后）
const handleVideoThumbnailGeneration = async () => {
  const list = formData.value.video_file || []
  
  for (const item of list) {
    const file = item.raw || item
    if (!item._posterReady && file && /^video\//.test(file.type || '')) {
      // 立即设置状态为处理中，避免显示"图片加载中"
      item.status = 'progress'
      item._posterReady = false
      
      // 异步生成缩略图，不阻塞UI
      generateVideoThumbnail(file).then(poster => {
        if (poster) {
          item.url = poster                      // 用首帧当封面
          item.thumbUrl = poster                 // 同时保存到 thumbUrl 以备后用
        }
        item.status = 'success'                            // 关键：去掉"图片加载中"
        item._posterReady = true                           // 标记已完成
        
        // 触发表单更新
        handleFormChange()
      }).catch(error => {
        console.warn('生成视频缩略图失败:', error)
        item.url = ''
        item.thumbUrl = ''
        item.status = 'success'                            // 即使失败也设为成功状态
        item._posterReady = true
        
        // 触发表单更新
        handleFormChange()
      })
    }
  }
}

watch(
  () => ({
    image_desc: formData.value.image_desc,
    video_desc: formData.value.video_desc,
    restoration_opinion: formData.value.restoration_opinion,
    opinion_tags: formData.value.opinion_tags,
    remark: formData.value.remark
  }),
  () => handleFormChange(),
  { deep: true }
)

onMounted(async () => {
  await initFormData()
})
</script>

<style scoped>
 /* ===== 关键修改：容器改为全宽流式，消除右侧空白 ===== */
 .form-page {
   width: 100%;
   max-width: 100%;        /* 取消 1000px 限制 */
   margin: 0;              /* 不再强制居中盒 */
   padding: 0 200px 32px;   /* 两侧留 60px 空白区域 */
   box-sizing: border-box;
 }

.form-card {
  width: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}

.page-header { margin: 12px 0 8px; }
.page-header h3 {
  font-size: 20px; font-weight: 600; color: #1f2937; margin: 0 0 6px;
}
.page-header p { color:#6b7280; font-size:14px; margin:0; }

 /* Section 标题条，细线风格 */
 .section { padding: 8px 0 0; }
 .section-bar {
   height: 36px; display:flex; align-items:center; justify-content:center;
   border-bottom: 2px solid #1857d3; margin-bottom: 12px;
 }
 .section-title { font-size: 15px; font-weight: 600; color:#1f2937; }

/* 上传组件样式 */
.img-upload, .video-upload { 
  width: 100%; 
}

/* 自定义上传按钮样式 */
.img-upload :deep(.t-upload__trigger),
.video-upload :deep(.t-upload__trigger) {
  width: 120px !important;
  height: 80px !important;
  border: 1px dashed #d1d5db !important;
  border-radius: 8px !important;
  background: #f9fafb !important;
  color: #6b7280 !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.2s ease !important;
}

.img-upload :deep(.t-upload__trigger:hover),
.video-upload :deep(.t-upload__trigger:hover) {
  border-color: #0052d9 !important;
  background: #f0f7ff !important;
}

.img-upload :deep(.t-upload__trigger .t-icon),
.video-upload :deep(.t-upload__trigger .t-icon) {
  font-size: 28px !important;
  margin-bottom: 4px !important;
}

.img-upload :deep(.t-upload__trigger .t-upload__text),
.video-upload :deep(.t-upload__trigger .t-upload__text) {
  font-size: 11px !important;
  margin-top: 4px !important;
}

/* 统一文件上传按钮区域 */
.file-upload :deep(.t-upload__trigger) { display:inline-flex; }

/* 标签预览 */
.tags-preview { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }



/* 视频缩略图样式优化 */
.video-upload :deep(.t-upload__file-item) {
  position: relative;
}

.video-upload :deep(.t-upload__file-item .t-upload__file-name) {
  font-size: 12px;
  color: #374151;
  margin-top: 4px;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 视频缩略图容器 */
.video-upload :deep(.t-upload__file-item .t-upload__file-preview) {
  width: 160px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  position: relative;
}

/* 视频缩略图图片 */
.video-upload :deep(.t-upload__file-item .t-upload__file-preview img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 视频处理中状态样式 */
.video-upload :deep(.t-upload__file-item[data-status="progress"] .t-upload__file-preview) {
  background: #f0f7ff;
  border-color: #0052d9;
}

.video-upload :deep(.t-upload__file-item[data-status="progress"] .t-upload__file-preview::after) {
  content: "视频处理中...";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #0052d9;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  border-radius: 4px;
  z-index: 1;
}

/* 自定义上传触发器样式 */
.upload-trigger {
  width: 110px;
  height: 108px;
  border: 1px dashed #d1d5db;
  border-radius: 8px;
  background: #f9fafb;
  color: #6b7280;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: .2s;
  pointer-events: auto; /* 确保可点击 */
}
.upload-trigger:hover {
  border-color: #0052d9;
  background: #f0f7ff;
}
.upload-trigger span {
  font-size: 11px;
  margin-top: 4px;
}

/* 让触发区一定可点击 */
.video-upload :deep(.t-upload__trigger) { 
  pointer-events: auto; 
}

/* 如你有父级 label/遮罩，兜底提高层级 */
.video-upload { 
  position: relative; 
  z-index: 1; 
}

/* 隐藏视频上传的预览图标，只保留删除图标 */
/* 仅视频上传区域生效 */
.video-upload :deep(.t-upload__card-actions .t-icon-browse),
.video-upload :deep(.t-upload__card-actions .t-icon-view),
/* 兼容个别版本：第一个操作按钮就是预览 */
.video-upload :deep(.t-upload__card-actions .t-upload__card-action:first-child) {
  display: none !important;
}


/* 底部状态条 */
.form-status {
  display:flex; justify-content:space-between; align-items:center;
  margin-top: 20px; padding-top:12px; border-top:1px solid #e5e7eb;
}
.auto-save-tip, .form-validation { display:flex; align-items:center; gap:6px; font-size:14px; }
.auto-save-tip { color:#10b981; }
.form-validation { color:#f59e0b; }
.form-validation.success { color:#10b981; }

/* 重命名对话框样式 */
.rename-dialog-content {
  padding: 16px 0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 20px;
}

.file-type {
  font-weight: 500;
  color: #374151;
}

.original-name {
  color: #6b7280;
  font-size: 14px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-extension-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  color: #6b7280;
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

/* 适配窄屏 */
@media (max-width: 768px) {
  .form-page { padding: 0 20px 24px; }
  .form-status { flex-direction:column; gap:10px; align-items:flex-start; }
  
  .file-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .original-name {
    width: 100%;
  }
}

/* 质量检测列表样式 */
.quality-check-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quality-check-list .t-checkbox {
  margin-bottom: 8px;
}

.quality-check-list .t-checkbox__label {
  font-size: 14px;
  line-height: 1.5;
  color: #374151;
}
</style>

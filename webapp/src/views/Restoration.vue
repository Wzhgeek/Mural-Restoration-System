<template>
  <Layout>
    <div class="restoration-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">修复提交</h2>
      <p class="page-description">发起和管理修复工作流程</p>
    </div>

    <!-- 操作按钮区域 -->
    <div class="action-buttons">
      <t-button theme="primary" @click="showCreateWorkflowModal">
        <template #icon>
          <t-icon name="add" />
        </template>
        创建新工作流
      </t-button>
      <t-button theme="default" variant="outline" @click="loadWorkflows">
        <template #icon>
          <t-icon name="refresh" />
        </template>
        刷新列表
      </t-button>
    </div>

    <!-- 工作流列表 -->
    <t-card title="我的工作流" :bordered="false" class="workflow-list-card">
      <div v-if="loading" class="loading-container">
        <t-loading size="medium" />
        <p>加载中...</p>
      </div>
      
      <div v-else-if="workflows.length === 0" class="empty-container">
        <t-icon name="inbox" size="48px" />
        <p>暂无工作流</p>
        <t-button theme="primary" variant="outline" @click="showCreateWorkflowModal">
          创建第一个工作流
        </t-button>
      </div>
      
      <div v-else class="workflow-table">
        <t-table
          :data="workflows"
          :columns="workflowColumns"
          row-key="workflow_id"
          :pagination="paginationConfig"
          @page-change="handlePageChange"
        >
          <template #status="{ row }">
            <t-tag :theme="getStatusTheme(row.status)" variant="light">
              {{ getStatusText(row.status) }}
            </t-tag>
          </template>
          
          <template #created_at="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
          
          <template #operation="{ row }">
            <t-space>
              <t-button theme="primary" variant="text" size="small" @click="viewWorkflowDetails(row.workflow_id)">
                查看详情
              </t-button>
              <t-button 
                v-if="row.status === 'draft' || row.status === 'running'" 
                theme="primary" 
                variant="text" 
                size="small" 
                @click="startRestorationFlow(row.workflow_id)"
              >
                提交表单
              </t-button>
            </t-space>
          </template>
        </t-table>
      </div>
    </t-card>

    <!-- 创建工作流模态框 -->
    <t-dialog
      v-model:visible="createWorkflowVisible"
      header="创建新工作流"
      width="600px"
      :footer="false"
    >
      <t-form ref="createWorkflowForm" :model="workflowForm" :rules="workflowRules" @submit="handleCreateWorkflow">
        <t-form-item label="工作流标题" name="title">
          <t-input v-model="workflowForm.title" placeholder="请输入工作流标题" />
        </t-form-item>
        
        <t-form-item label="描述" name="description">
          <t-textarea 
            v-model="workflowForm.description" 
            placeholder="请输入工作流描述"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </t-form-item>
        
        <div class="dialog-footer">
          <t-space>
            <t-button theme="default" @click="createWorkflowVisible = false">取消</t-button>
            <t-button theme="primary" type="submit" :loading="submitting">创建</t-button>
          </t-space>
        </div>
      </t-form>
    </t-dialog>

    <!-- 工作流详情模态框 -->
    <t-dialog
      v-model:visible="workflowDetailsVisible"
      header="工作流详情"
      width="90vw"
      height="85vh"
      :footer="false"
      class="workflow-details-dialog"
      :style="{ maxWidth: '1400px', maxHeight: '900px' }"
    >
      <div v-if="workflowDetails" class="workflow-details">
        <div class="workflow-info">
          <t-descriptions :column="2" :label-style="{ width: '120px' }">
            <t-descriptions-item label="工作流ID">{{ workflowDetails.workflow_id }}</t-descriptions-item>
            <t-descriptions-item label="标题">{{ workflowDetails.title }}</t-descriptions-item>
            <t-descriptions-item label="发起人">{{ workflowDetails.initiator_name }}</t-descriptions-item>
            <t-descriptions-item label="当前步骤">第 {{ workflowDetails.current_step }} 步</t-descriptions-item>
            <t-descriptions-item label="状态">
              <t-tag :theme="getStatusTheme(workflowDetails.status)" variant="light">
                {{ getStatusText(workflowDetails.status) }}
              </t-tag>
            </t-descriptions-item>
            <t-descriptions-item label="创建时间">{{ formatDate(workflowDetails.created_at) }}</t-descriptions-item>
            <t-descriptions-item label="更新时间">{{ formatDate(workflowDetails.updated_at) }}</t-descriptions-item>
          </t-descriptions>
          <div v-if="workflowDetails.description" class="workflow-description">
            <strong>描述：</strong>{{ workflowDetails.description }}
          </div>
        </div>

        <t-divider />

        <div class="workflow-content">
          <t-row :gutter="[24, 24]" class="workflow-row">
            <!-- 表单列表 -->
            <t-col :xs="12" :xl="8" class="workflow-col">
              <t-card title="修复表单历史" :bordered="false" class="forms-card">
                <div v-if="workflowForms.length === 0" class="empty-forms">
                  <t-icon name="inbox" size="32px" />
                  <p>暂无表单</p>
                </div>
                <div v-else class="forms-list" ref="formsListRef">
                  <div 
                    v-for="(form, index) in workflowForms" 
                    :key="form.form_id"
                    class="form-item"
                  >
                    <div class="form-header">
                      <div class="form-title">
                        <strong>第 {{ form.step_no }} 步 - {{ form.submitter_name }}</strong>
                      </div>
                      <div class="form-time">{{ formatDate(form.created_at) }}</div>
                    </div>
                    
                    <div class="form-content">
                      <div v-if="form.image_url" class="form-image">
                        <t-image
                          :src="form.image_url"
                          :style="{ maxWidth: '200px', height: 'auto' }"
                          fit="cover"
                          :lazy="true"
                          :error="'图片加载失败'"
                        />
                      </div>
                      
                      <div v-if="form.image_desc" class="form-field">
                        <strong>图片描述：</strong>{{ form.image_desc }}
                      </div>
                      
                      <div v-if="form.image_desc_file" class="form-field">
                        <strong>图片描述附件：</strong>
                        <t-button theme="primary" variant="text" size="small" @click="downloadFile(form.image_desc_file)">
                          <template #icon>
                            <t-icon name="download" />
                          </template>
                          下载附件
                        </t-button>
                      </div>
                      
                      <div v-if="form.restoration_opinion" class="form-field">
                        <strong>修复意见：</strong>{{ form.restoration_opinion }}
                      </div>
                      
                      <div v-if="form.opinion_file" class="form-field">
                        <strong>修复意见附件：</strong>
                        <t-button theme="primary" variant="text" size="small" @click="downloadFile(form.opinion_file)">
                          <template #icon>
                            <t-icon name="download" />
                          </template>
                          下载附件
                        </t-button>
                      </div>
                      
                      <div v-if="form.opinion_tags && form.opinion_tags.length > 0" class="form-field">
                        <strong>标签：</strong>
                        <t-space>
                          <t-tag v-for="tag in (Array.isArray(form.opinion_tags) ? form.opinion_tags : [])" :key="tag" theme="primary" variant="light">
                            {{ tag }}
                          </t-tag>
                        </t-space>
                      </div>
                      
                      <div v-if="form.remark" class="form-field">
                        <strong>备注：</strong>{{ form.remark }}
                      </div>
                      
                      <div v-if="form.attachment" class="form-field">
                        <strong>其他附件：</strong>
                        <t-button theme="primary" variant="text" size="small" @click="downloadFile(form.attachment)">
                          <template #icon>
                            <t-icon name="download" />
                          </template>
                          下载附件
                        </t-button>
                      </div>
                      
                      <div class="form-actions">
                        <t-space>
                          <t-button 
                            v-if="canRequestRollback && workflowForms.length > 1"
                            theme="warning" 
                            variant="outline" 
                            size="small"
                            @click="requestRollback(workflowDetails.workflow_id, form.form_id)"
                          >
                            申请回溯到此步骤
                          </t-button>
                          <t-button 
                            v-if="canFinalize"
                            theme="success" 
                            variant="outline" 
                            size="small"
                            @click="finalizeWorkflow(workflowDetails.workflow_id, form.form_id)"
                          >
                            设为最终方案
                          </t-button>
                        </t-space>
                      </div>
                    </div>
                  </div>
                </div>
              </t-card>
            </t-col>
            
            <!-- 评估意见 -->
            <t-col :xs="12" :xl="4" class="workflow-col">
              <t-card title="评估意见" :bordered="false" class="evaluations-card">
                <div v-if="workflowEvaluations.length === 0" class="empty-evaluations">
                  <t-icon name="inbox" size="32px" />
                  <p>暂无评估</p>
                </div>
                <div v-else class="evaluations-list">
                  <div 
                    v-for="evaluation in workflowEvaluations" 
                    :key="evaluation.evaluate_id"
                    class="evaluation-item"
                  >
                    <div class="evaluation-header">
                      <div class="evaluator-name">{{ evaluation.evaluator_name }}</div>
                      <t-tag theme="primary" variant="light">评分: {{ evaluation.score }}</t-tag>
                    </div>
                    
                    <div v-if="evaluation.comment" class="evaluation-comment">
                      {{ evaluation.comment }}
                    </div>
                    
                    <div v-if="evaluation.evaluation_file" class="evaluation-file">
                      <strong>评估文件：</strong>
                      <t-button theme="primary" variant="text" size="small" @click="downloadFile(evaluation.evaluation_file)">
                        <template #icon>
                          <t-icon name="download" />
                        </template>
                        下载文件
                      </t-button>
                    </div>
                    
                    <div class="evaluation-time">{{ formatDate(evaluation.created_at) }}</div>
                  </div>
                </div>
                
                <div v-if="canEvaluate" class="evaluation-actions">
                  <t-button theme="primary" @click="showEvaluationModal(workflowDetails.workflow_id)">
                    添加评估
                  </t-button>
                </div>
              </t-card>
            </t-col>
          </t-row>
        </div>
      </div>
    </t-dialog>

    <!-- 提交表单模态框 -->
    <t-dialog
      v-model:visible="createFormVisible"
      header="提交修复表单"
      width="800px"
      overflow="hidden"
      :footer="false"
    >
      <t-form ref="createFormForm" :model="formData" :rules="formRules" @submit="handleSubmitForm">
        <t-row :gutter="[16, 16]">
          <t-col :xs="12">
            <t-form-item label="壁画图片" name="image_file">
              <t-upload
                v-model="formData.image_file"
                :auto-upload="false"
                accept="image/*"
                :max="1"
                :size-limit="10 * 1024 * 1024"
                @change="handleImageChange"
              >
                <template #upload-dragger>
                  <div class="upload-dragger">
                    <t-icon name="cloud-upload" size="48px" />
                    <p>点击或拖拽上传图片</p>
                    <p class="upload-tip">支持 JPG、PNG 格式，大小不超过 10MB</p>
                  </div>
                </template>
              </t-upload>
            </t-form-item>
          </t-col>
          
          <t-col :xs="12">
            <t-form-item label="图片描述" name="image_desc">
              <t-textarea 
                v-model="formData.image_desc" 
                placeholder="请描述壁画图片的内容和状态"
                :autosize="{ minRows: 3, maxRows: 6 }"
              />
            </t-form-item>
            
            <t-form-item label="图片描述附件">
              <t-upload
                v-model="formData.image_desc_file"
                :auto-upload="false"
                accept=".pdf,.doc,.docx,.txt"
                :max="1"
                :size-limit="20 * 1024 * 1024"
              >
                <template #upload-dragger>
                  <div class="upload-dragger-small">
                    <t-icon name="attach" size="24px" />
                    <span>上传附件</span>
                  </div>
                </template>
              </t-upload>
            </t-form-item>
          </t-col>
        </t-row>
        
        <t-row :gutter="[16, 16]">
          <t-col :xs="12">
            <t-form-item label="修复意见" name="restoration_opinion">
              <t-textarea 
                v-model="formData.restoration_opinion" 
                placeholder="请详细描述修复意见和方案"
                :autosize="{ minRows: 4, maxRows: 8 }"
              />
            </t-form-item>
          </t-col>
          
          <t-col :xs="12">
            <t-form-item label="修复标签">
              <t-input 
                v-model="formData.opinion_tags" 
                placeholder="用逗号分隔，如：浮灰清理,内容修补,颜料补充"
              />
            </t-form-item>
            
            <t-form-item label="修复意见附件">
              <t-upload
                v-model="formData.opinion_file"
                :auto-upload="false"
                accept=".pdf,.doc,.docx,.txt"
                :max="1"
                :size-limit="20 * 1024 * 1024"
              >
                <template #upload-dragger>
                  <div class="upload-dragger-small">
                    <t-icon name="attach" size="24px" />
                    <span>上传附件</span>
                  </div>
                </template>
              </t-upload>
            </t-form-item>
          </t-col>
        </t-row>
        
        <t-row :gutter="[16, 16]">
          <t-col :xs="12">
            <t-form-item label="备注">
              <t-textarea 
                v-model="formData.remark" 
                placeholder="其他需要说明的内容"
                :autosize="{ minRows: 3, maxRows: 6 }"
              />
            </t-form-item>
          </t-col>
          
          <t-col :xs="12">
            <t-form-item label="其他附件">
              <t-upload
                v-model="formData.attachment_file"
                :auto-upload="false"
                :max="1"
                :size-limit="20 * 1024 * 1024"
              >
                <template #upload-dragger>
                  <div class="upload-dragger-small">
                    <t-icon name="attach" size="24px" />
                    <span>上传附件</span>
                  </div>
                </template>
              </t-upload>
            </t-form-item>
          </t-col>
        </t-row>
        
        <div class="dialog-footer">
          <t-space>
            <t-button theme="default" @click="createFormVisible = false">取消</t-button>
            <t-button theme="primary" type="submit" :loading="submitting">提交表单</t-button>
          </t-space>
        </div>
      </t-form>
    </t-dialog>

    <!-- 回溯申请模态框 -->
    <t-dialog
      v-model:visible="rollbackVisible"
      header="申请回溯"
      width="600px"
      :footer="false"
    >
      <t-form ref="rollbackForm" :model="rollbackData" :rules="rollbackRules" @submit="handleSubmitRollback">
        <t-form-item label="回溯原因" name="reason">
          <t-textarea 
            v-model="rollbackData.reason" 
            placeholder="请详细说明申请回溯的原因..."
            :autosize="{ minRows: 4, maxRows: 8 }"
          />
        </t-form-item>
        
        <t-form-item label="支撑材料（可选）">
          <t-upload
            v-model="rollbackData.support_file"
            :auto-upload="false"
            accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
            :max="1"
            :size-limit="20 * 1024 * 1024"
          >
            <template #upload-dragger>
              <div class="upload-dragger-small">
                <t-icon name="attach" size="24px" />
                <span>上传支撑文件</span>
              </div>
            </template>
          </t-upload>
        </t-form-item>
        
        <div class="dialog-footer">
          <t-space>
            <t-button theme="default" @click="rollbackVisible = false">取消</t-button>
            <t-button theme="primary" type="submit" :loading="submitting">提交申请</t-button>
          </t-space>
        </div>
      </t-form>
    </t-dialog>

    <!-- 评估模态框 -->
    <t-dialog
      v-model:visible="evaluationVisible"
      header="添加评估意见"
      width="600px"
      :footer="false"
    >
      <t-form ref="evaluationForm" :model="evaluationData" :rules="evaluationRules" @submit="handleSubmitEvaluation">
        <t-form-item label="评分" name="score">
          <t-input-number 
            v-model="evaluationData.score" 
            :min="0" 
            :max="100" 
            placeholder="请输入评分 (0-100分)"
          />
        </t-form-item>
        
        <t-form-item label="评估意见">
          <t-textarea 
            v-model="evaluationData.comment" 
            placeholder="请输入评估意见"
            :autosize="{ minRows: 4, maxRows: 8 }"
          />
        </t-form-item>
        
        <t-form-item label="支撑文件（可选）">
          <t-upload
            v-model="evaluationData.support_file"
            :auto-upload="false"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif"
            :max="1"
            :size-limit="20 * 1024 * 1024"
          >
            <template #upload-dragger>
              <div class="upload-dragger-small">
                <t-icon name="attach" size="24px" />
                <span>上传文件</span>
              </div>
            </template>
          </t-upload>
        </t-form-item>
        
        <div class="dialog-footer">
          <t-space>
            <t-button theme="default" @click="evaluationVisible = false">取消</t-button>
            <t-button theme="primary" type="submit" :loading="submitting">提交评估</t-button>
          </t-space>
        </div>
      </t-form>
    </t-dialog>

    <!-- 保密协议模态框 -->
    <t-dialog
      v-model:visible="privacyVisible"
      header="保密协议"
      width="600px"
      :footer="false"
    >
      <div class="privacy-content">
        <div class="privacy-text" ref="privacyText">
          {{ privacyAgreement }}
        </div>
        <div class="privacy-tip">
          <t-icon name="info-circle" />
          <span>请仔细阅读上述协议内容，滚动到底部后才能同意</span>
        </div>
      </div>
      
      <div class="dialog-footer">
        <t-space>
          <t-button theme="default" @click="rejectAgreement">不同意</t-button>
          <t-button theme="primary" :disabled="!canAgree" @click="acceptAgreement">同意并继续</t-button>
        </t-space>
      </div>
    </t-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { getWorkflows, createWorkflow, getWorkflowForms, getWorkflowEvaluations, submitForm, requestRollback as apiRequestRollback, finalizeWorkflow as apiFinalizeWorkflow, submitEvaluation, getPrivacyAgreement } from '@/api/restoration'
import Layout from '@/components/Layout.vue'

/**
 * 修复提交页面组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const router = useRouter()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const workflows = ref([])
const currentUser = ref(null)

// 模态框状态
const createWorkflowVisible = ref(false)
const workflowDetailsVisible = ref(false)
const createFormVisible = ref(false)
const rollbackVisible = ref(false)
const evaluationVisible = ref(false)
const privacyVisible = ref(false)

// 表单数据
const workflowForm = reactive({
  title: '',
  description: ''
})

const formData = reactive({
  workflow_id: '',
  image_file: [],
  image_desc: '',
  image_desc_file: [],
  restoration_opinion: '',
  opinion_tags: '',
  opinion_file: [],
  remark: '',
  attachment_file: []
})

const rollbackData = reactive({
  workflow_id: '',
  target_form_id: '',
  reason: '',
  support_file: []
})

const evaluationData = reactive({
  workflow_id: '',
  score: null,
  comment: '',
  support_file: []
})

// 工作流详情数据
const workflowDetails = ref(null)
const workflowForms = ref([])
const workflowEvaluations = ref([])
const privacyAgreement = ref('')
const canAgree = ref(false)

// 表单列表引用
const formsListRef = ref(null)

// 分页配置
const paginationConfig = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 表格列配置
const workflowColumns = [
  { colKey: 'title', title: '标题', width: 200 },
  { colKey: 'initiator_name', title: '发起人', width: 120 },
  { colKey: 'current_step', title: '当前步骤', width: 100 },
  { colKey: 'status', title: '状态', width: 100 },
  { colKey: 'created_at', title: '创建时间', width: 160 },
  { colKey: 'operation', title: '操作', width: 200, fixed: 'right' }
]

// 表单验证规则
const workflowRules = {
  title: [{ required: true, message: '请输入工作流标题' }]
}

const formRules = {
  // 根据接口文档，图片和修复意见都是可选的
  // image_file: [{ required: true, message: '请上传壁画图片' }],
  // restoration_opinion: [{ required: true, message: '请输入修复意见' }]
}

const rollbackRules = {
  reason: [{ required: true, message: '请输入回溯原因' }]
}

const evaluationRules = {
  score: [{ required: true, message: '请输入评分' }]
}

// 计算属性
const canRequestRollback = computed(() => {
  return currentUser.value?.role_key === 'restorer'
})

const canFinalize = computed(() => {
  return currentUser.value?.role_key !== 'evaluator'
})

const canEvaluate = computed(() => {
  return currentUser.value?.role_key === 'evaluator' || currentUser.value?.role_key === 'admin'
})

// 方法
const loadWorkflows = async () => {
  try {
    loading.value = true
    const response = await getWorkflows()
    // 根据接口文档，直接返回数组数据
    workflows.value = Array.isArray(response) ? response : (response.data || [])
    paginationConfig.total = workflows.value.length
  } catch (error) {
    console.error('加载工作流失败:', error)
    MessagePlugin.error('加载工作流失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const showCreateWorkflowModal = () => {
  workflowForm.title = ''
  workflowForm.description = ''
  createWorkflowVisible.value = true
}

const handleCreateWorkflow = async () => {
  try {
    submitting.value = true
    await createWorkflow(workflowForm)
    MessagePlugin.success('工作流创建成功')
    createWorkflowVisible.value = false
    loadWorkflows()
  } catch (error) {
    console.error('创建工作流失败:', error)
    MessagePlugin.error('创建工作流失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

const viewWorkflowDetails = async (workflowId) => {
  try {
    const [formsResponse, evaluationsResponse] = await Promise.all([
      getWorkflowForms(workflowId),
      getWorkflowEvaluations(workflowId)
    ])
    
    workflowDetails.value = workflows.value.find(w => w.workflow_id === workflowId)
    // 根据接口文档，直接返回数组数据
    workflowForms.value = Array.isArray(formsResponse) ? formsResponse : (formsResponse.data || [])
    workflowEvaluations.value = Array.isArray(evaluationsResponse) ? evaluationsResponse : (evaluationsResponse.data || [])
    workflowDetailsVisible.value = true
    
    // 等待DOM更新后初始化滚动
    nextTick(() => {
      initScrollBehavior()
    })
  } catch (error) {
    console.error('加载工作流详情失败:', error)
    MessagePlugin.error('加载工作流详情失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 初始化滚动行为
const initScrollBehavior = () => {
  if (formsListRef.value) {
    // 设置初始滚动位置，显示略大于单个form-item的高度
    const formItemHeight = 200 // 与CSS中min-height一致
    const initialScrollHeight = formItemHeight + 50 // 略大于单个form-item的高度
    formsListRef.value.scrollTop = 0
    
    // 添加滚动事件监听，实现平滑滚动到form-item边界
    formsListRef.value.addEventListener('scroll', handleFormsScroll)
  }
}

// 处理表单列表滚动事件
const handleFormsScroll = (event) => {
  const container = event.target
  const scrollTop = container.scrollTop
  const formItemHeight = 216 // 200px min-height + 16px margin-bottom
  
  // 计算当前应该滚动到的form-item索引
  const currentIndex = Math.round(scrollTop / formItemHeight)
  const targetScrollTop = currentIndex * formItemHeight
  
  // 平滑滚动到最近的form-item边界
  if (Math.abs(scrollTop - targetScrollTop) > 5) {
    container.scrollTo({
      top: targetScrollTop,
      behavior: 'smooth'
    })
  }
}

// 使用新的流程页面
const startRestorationFlow = (workflowId) => {
  // 跳转到新的修复提交流程
  router.push(`/restoration-flow/${workflowId}/privacy`)
}

// 保留旧的方法作为备用（可在后续版本中删除）
const showCreateFormModal = async (workflowId) => {
  // 提示用户使用新流程
  MessagePlugin.info('正在跳转到新的修复提交流程...')
  startRestorationFlow(workflowId)
}

const handleSubmitForm = async () => {
  try {
    submitting.value = true
    
    const submitData = new FormData()
    submitData.append('workflow_id', formData.workflow_id)
    submitData.append('image_desc', formData.image_desc || '')
    submitData.append('restoration_opinion', formData.restoration_opinion || '')
    submitData.append('opinion_tags', formData.opinion_tags || '')
    submitData.append('remark', formData.remark || '')
    
    // 添加文件 - 根据接口文档，opinion_tags应该是JSON数组格式
    if (formData.opinion_tags) {
      const tags = formData.opinion_tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      submitData.set('opinion_tags', JSON.stringify(tags))
    }
    
    if (formData.image_file && formData.image_file[0]) {
      submitData.append('image_file', formData.image_file[0].raw)
    }
    if (formData.image_desc_file && formData.image_desc_file[0]) {
      submitData.append('image_desc_file', formData.image_desc_file[0].raw)
    }
    if (formData.opinion_file && formData.opinion_file[0]) {
      submitData.append('opinion_file', formData.opinion_file[0].raw)
    }
    if (formData.attachment_file && formData.attachment_file[0]) {
      submitData.append('attachment_file', formData.attachment_file[0].raw)
    }
    
    await submitForm(submitData)
    MessagePlugin.success('表单提交成功')
    createFormVisible.value = false
    loadWorkflows()
  } catch (error) {
    console.error('提交表单失败:', error)
    MessagePlugin.error('提交表单失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const requestRollback = (workflowId, targetFormId) => {
  rollbackData.workflow_id = workflowId
  rollbackData.target_form_id = targetFormId
  rollbackData.reason = ''
  rollbackData.support_file = []
  rollbackVisible.value = true
}

const handleSubmitRollback = async () => {
  try {
    submitting.value = true
    
    const submitData = new FormData()
    submitData.append('workflow_id', rollbackData.workflow_id)
    submitData.append('target_form_id', rollbackData.target_form_id)
    submitData.append('reason', rollbackData.reason)
    
    if (rollbackData.support_file && rollbackData.support_file[0]) {
      submitData.append('support_file', rollbackData.support_file[0].raw)
    }
    
    await apiRequestRollback(submitData)
    MessagePlugin.success('回溯申请已提交')
    rollbackVisible.value = false
    loadWorkflows()
  } catch (error) {
    console.error('提交回溯申请失败:', error)
    MessagePlugin.error('提交回溯申请失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const finalizeWorkflow = async (workflowId, formId) => {
  try {
    // 使用浏览器原生确认对话框
    const confirmed = confirm('确认将此步骤设为最终方案吗？这将结束整个工作流。')
    
    if (confirmed) {
      const formData = new FormData()
      formData.append('final_form_id', formId)
      
      await apiFinalizeWorkflow(workflowId, formData)
      MessagePlugin.success('已设为最终方案')
      workflowDetailsVisible.value = false
      loadWorkflows()
    }
  } catch (error) {
    console.error('设为最终方案失败:', error)
    MessagePlugin.error('设为最终方案失败: ' + (error.response?.data?.detail || error.message))
  }
}

const showEvaluationModal = (workflowId) => {
  evaluationData.workflow_id = workflowId
  evaluationData.score = null
  evaluationData.comment = ''
  evaluationData.support_file = []
  evaluationVisible.value = true
}

const handleSubmitEvaluation = async () => {
  try {
    submitting.value = true
    
    const submitData = new FormData()
    submitData.append('workflow_id', evaluationData.workflow_id)
    submitData.append('score', evaluationData.score)
    submitData.append('comment', evaluationData.comment || '')
    
    if (evaluationData.support_file && evaluationData.support_file[0]) {
      submitData.append('support_file', evaluationData.support_file[0].raw)
    }
    
    await submitEvaluation(submitData)
    MessagePlugin.success('评估提交成功')
    evaluationVisible.value = false
    workflowDetailsVisible.value = false
    loadWorkflows()
  } catch (error) {
    console.error('提交评估失败:', error)
    MessagePlugin.error('提交评估失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const showPrivacyAgreement = async () => {
  return new Promise(async (resolve) => {
    try {
      const response = await getPrivacyAgreement()
      // 根据接口文档，响应格式为 { success: true, message: "获取成功", data: { content: "..." } }
      privacyAgreement.value = response.data?.content || response.content || '保密协议内容加载中...'
      canAgree.value = false
      privacyVisible.value = true
      
      // 监听滚动事件 - 使用更可靠的方式
      nextTick(() => {
        // 等待DOM完全渲染后再查找元素
        setTimeout(() => {
          // 查找实际的滚动容器，应该是 .privacy-content
          const privacyContent = document.querySelector('.privacy-content')
          
          if (privacyContent) {
            
            privacyContent.addEventListener('scroll', () => {
              const scrollTop = privacyContent.scrollTop
              const clientHeight = privacyContent.clientHeight
              const scrollHeight = privacyContent.scrollHeight
              
              
              // 检查是否滚动到底部（允许10px的误差）
              if (scrollTop + clientHeight >= scrollHeight - 10) {
                canAgree.value = true
              }
            })
            
            // 如果内容高度小于容器高度，直接启用按钮
            if (privacyContent.scrollHeight <= privacyContent.clientHeight) {
              canAgree.value = true
            }
          } else {
            console.error('未找到隐私协议容器元素')
          }
        }, 100) // 延迟100ms确保DOM完全渲染
      })
      
      // 设置全局函数
      window.acceptAgreement = () => {
        privacyVisible.value = false
        resolve(true)
      }
      
      window.rejectAgreement = () => {
        privacyVisible.value = false
        resolve(false)
      }
    } catch (error) {
      console.error('加载保密协议失败:', error)
      MessagePlugin.error('加载保密协议失败: ' + (error.response?.data?.detail || error.message))
      resolve(false)
    }
  })
}

const acceptAgreement = () => {
  window.acceptAgreement()
}

const rejectAgreement = () => {
  window.rejectAgreement()
}

const handleImageChange = (files) => {
  if (files && files.length > 0) {
    formData.image_file = files
  }
}

const handlePageChange = (pageInfo) => {
  paginationConfig.current = pageInfo.current
  paginationConfig.pageSize = pageInfo.pageSize
}

const getStatusTheme = (status) => {
  const statusMap = {
    'draft': 'warning',
    'running': 'primary',
    'finished': 'success',
    'paused': 'warning',
    'revoked': 'danger'
  }
  return statusMap[status] || 'default'
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'running': '进行中',
    'finished': '已完成',
    'paused': '已暂停',
    'revoked': '已撤销'
  }
  return statusMap[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const downloadFile = (url) => {
  window.open(url, '_blank')
}

// 清理滚动事件监听器
const cleanupScrollListener = () => {
  if (formsListRef.value) {
    formsListRef.value.removeEventListener('scroll', handleFormsScroll)
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 获取当前用户信息
  const user = localStorage.getItem('currentUser')
  if (user) {
    currentUser.value = JSON.parse(user)
  }
  
  loadWorkflows()
})

// 组件卸载时清理
onUnmounted(() => {
  cleanupScrollListener()
})
</script>

<style scoped>
:deep(.t-dialog__body) {
  overflow: hidden;
}

/* 回溯申请模态框的表单控件内容样式 */
:deep(.t-form__controls-content) {
  padding: 0 0 0 10px;
}
.restoration-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  /* 顶部间距 */
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 24px 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.workflow-list-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #6b7280;
}

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #6b7280;
}

.empty-container p {
  margin: 16px 0;
  font-size: 16px;
}

/* 工作流详情对话框样式 */
.workflow-details-dialog :deep(.t-dialog__body) {
  height: calc(85vh - 120px);
  overflow: hidden;
  padding: 0;
}

.workflow-details {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.workflow-info {
  margin-bottom: 16px;
  padding: 20px;
  flex-shrink: 0;
  border-bottom: 1px solid #e5e7eb;
}

.workflow-description {
  margin-top: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
  color: #374151;
  line-height: 1.5;
}

.workflow-content {
  flex: 1;
  overflow: hidden;
  padding: 0 20px 20px 20px;
  min-height: 0;
}

.forms-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.forms-card :deep(.t-card__body) {
  flex: 1;
  overflow: hidden;
  padding: 16px;
}

.forms-list {
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
}

.form-item {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  transition: all 0.2s ease;
  scroll-margin-top: 16px;
}

.form-item:hover {
  border-color: #0052d9;
  box-shadow: 0 2px 8px rgba(0, 82, 217, 0.1);
}

.form-item:last-child {
  margin-bottom: 0;
}

.evaluations-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.evaluations-card :deep(.t-card__body) {
  flex: 1;
  overflow: hidden;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.evaluations-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  margin-bottom: 16px;
}

.evaluation-item {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  transition: all 0.2s ease;
  scroll-margin-top: 16px;
}

.evaluation-item:hover {
  border-color: #0052d9;
  box-shadow: 0 2px 8px rgba(0, 82, 217, 0.1);
}

.evaluation-item:last-child {
  margin-bottom: 0;
}

.evaluation-actions {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.empty-forms,
.empty-evaluations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: #6b7280;
  height: 100%;
}

/* 表单卡片样式 */
.forms-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.forms-card :deep(.t-card__body) {
  flex: 1;
  overflow: hidden;
  padding: 16px;
}

.forms-list {
  height: 100%;
  overflow-y: auto;
  scroll-behavior: smooth;
  scroll-snap-type: y mandatory;
}

/* 评估卡片样式 */
.evaluations-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.evaluations-card :deep(.t-card__body) {
  flex: 1;
  overflow: hidden;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.evaluations-list {
  flex: 1;
  overflow-y: auto;
  max-height: calc(100% - 60px);
}

.form-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 16px;
  padding: 16px;
  background: #f9fafb;
  min-height: 200px;
  scroll-snap-align: start;
  scroll-snap-stop: always;
}

.evaluation-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 16px;
  padding: 16px;
  background: #f9fafb;
}

.form-header,
.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.form-title {
  font-weight: 600;
  color: #1f2937;
}

.form-time,
.evaluation-time {
  font-size: 12px;
  color: #6b7280;
}

.form-content {
  margin-top: 12px;
}

.form-field {
  margin-bottom: 8px;
  color: #374151;
}

.form-field strong {
  color: #1f2937;
  font-weight: 600;
}

.form-actions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.evaluation-comment {
  margin: 8px 0;
  color: #374151;
  line-height: 1.5;
}

.evaluation-file {
  margin: 8px 0;
}

.evaluation-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

/* 确保行布局固定高度 */
.workflow-row {
  height: 100%;
  margin: 0 !important;
}

.workflow-col {
  height: 100%;
  padding-bottom: 0 !important;
}

.workflow-content :deep(.t-row) {
  height: 100%;
}

.workflow-content :deep(.t-col) {
  height: 100%;
}

/* 优化滚动条样式 */
.forms-list::-webkit-scrollbar,
.evaluations-list::-webkit-scrollbar {
  width: 6px;
}

.forms-list::-webkit-scrollbar-track,
.evaluations-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.forms-list::-webkit-scrollbar-thumb,
.evaluations-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.forms-list::-webkit-scrollbar-thumb:hover,
.evaluations-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
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

.privacy-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
  white-space: pre-wrap;
  line-height: 1.6;
  color: #374151;
}

.privacy-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
  background: #fef3c7;
  border-radius: 6px;
  color: #d97706;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .restoration-page {
    padding: 16px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .workflow-details {
    max-height: 60vh;
  }
  
  .upload-dragger {
    padding: 24px 16px;
  }
  
  .upload-dragger-small {
    padding: 12px;
  }
}
</style>

<template>
  <Layout>
    <div class="evaluation-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h2 class="page-title">评估修复</h2>
        <p class="page-description">评估已完成的修复工作流程</p>
      </div>

      <!-- 操作栏 -->
      <div class="toolbar-section">
        <div class="left-operations">
          <t-button theme="primary" @click="refreshData">
            <template #icon>
              <t-icon name="refresh" />
            </template>
            刷新
          </t-button>
          <t-button theme="default" variant="outline" v-if="canDelete" @click="handleBatchDelete">
            <template #icon>
              <t-icon name="delete" />
            </template>
            批量删除
          </t-button>
        </div>

        <div class="right-operations">
          <t-input
            v-model="searchValue"
            placeholder="搜索工作流..."
            clearable
            style="width: 200px; margin-right: 8px;"
            @enter="handleSearch"
          >
            <template #suffix-icon>
              <t-icon name="search" @click="handleSearch" />
            </template>
          </t-input>

          <t-select
            v-model="statusFilter"
            placeholder="筛选状态"
            clearable
            style="width: 120px; margin-right: 8px;"
            @change="handleFilter"
          >
            <t-option value="all" label="全部工作流" />
            <t-option value="finished" label="已完成" />
            <t-option value="evaluated" label="已评估" />
            <t-option value="unevaluated" label="未评估" />
          </t-select>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-section">
        <t-row :gutter="16">
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.total_evaluations || 0 }}</div>
                <div class="stat-label">总评估</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.total_pending || 0 }}</div>
                <div class="stat-label">待评估</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.total_evaluated || 0 }}</div>
                <div class="stat-label">已评估</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.average_score || 0 }}</div>
                <div class="stat-label">平均评分</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.monthly_evaluations || 0 }}</div>
                <div class="stat-label">本月评估</div>
              </div>
            </t-card>
          </t-col>
        </t-row>
      </div>

      <!-- 数据表格 -->
      <t-card class="data-table-card" :bordered="false">
        <t-table
          :data="tableData"
          :columns="columns"
          :loading="loading"
          :pagination="pagination"
          :selected-row-keys="selectedRowKeys"
          :row-key="rowKey"
          vertical-align="top"
          hover
          @page-change="handlePageChange"
          @select-change="handleSelectChange"
        >
          <template #status="{ row }">
            <t-tag
              :theme="getStatusTheme(row.status, row.has_evaluation)"
              variant="light"
            >
              {{ getStatusText(row.status, row.has_evaluation) }}
            </t-tag>
          </template>

          <template #updated_at="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>

          <template #op="slotProps">
            <t-space>
              <t-link theme="primary" @click="viewWorkflowDetails(slotProps.row)">
                <t-icon name="view" />
                {{ slotProps.row.has_evaluation ? '查看详情' : '查看并评估' }}
              </t-link>
              <t-link theme="danger" v-if="canDelete" @click="handleDelete(slotProps.row)">
                <t-icon name="delete" />
                删除
              </t-link>
            </t-space>
          </template>
        </t-table>
      </t-card>

      <!-- 工作流详情评估对话框 -->
      <t-dialog
        v-model:visible="detailDialogVisible"
        :header="`工作流详情 - ${currentWorkflow?.title || ''}`"
        width="1200px"
        :close-on-overlay-click="false"
        @confirm="handleCloseDetailDialog"
        @cancel="handleCloseDetailDialog"
      >
        <div v-if="currentWorkflow" class="workflow-detail">
          <!-- 工作流基本信息 -->
          <t-descriptions :column="3" title="工作流信息" class="workflow-info">
            <t-descriptions-item label="工作流标题">
              {{ currentWorkflow.title }}
            </t-descriptions-item>
            <t-descriptions-item label="发起人">
              {{ currentWorkflow.initiator_name }}
            </t-descriptions-item>
            <t-descriptions-item label="当前状态">
              <t-tag :theme="getStatusTheme(currentWorkflow.status)" variant="light">
                {{ getStatusText(currentWorkflow.status) }}
              </t-tag>
            </t-descriptions-item>
            <t-descriptions-item label="创建时间">
              {{ formatDate(currentWorkflow.created_at) }}
            </t-descriptions-item>
            <t-descriptions-item label="最后更新">
              {{ formatDate(currentWorkflow.updated_at) }}
            </t-descriptions-item>
            <t-descriptions-item label="评估状态">
              <t-tag :theme="currentWorkflow.has_evaluation ? 'success' : 'warning'" variant="light">
                {{ currentWorkflow.has_evaluation ? '已评估' : '未评估' }}
              </t-tag>
            </t-descriptions-item>
          </t-descriptions>

          <!-- 修复表单历史 -->
          <t-card title="修复表单历史" class="forms-history" :bordered="false">
            <div v-if="workflowForms.length === 0" class="empty-state">
              <t-icon name="file" size="48px" />
              <p>暂无修复表单</p>
            </div>
            <div v-else class="forms-list">
              <t-timeline>
                <t-timeline-item
                  v-for="form in workflowForms"
                  :key="form.form_id"
                  :dot-color="getFormDotColor(form.step_no)"
                >
                  <template #content>
                    <div class="form-item">
                      <div class="form-header">
                        <h4>第 {{ form.step_no }} 步修复</h4>
                        <div class="form-meta">
                          <span class="form-submitter">{{ form.submitter_name }}</span>
                          <span class="form-time">{{ formatDate(form.created_at) }}</span>
                        </div>
                      </div>

                      <div class="form-content">
                        <div v-if="form.image_url" class="form-image">
                          <img
                            :src="form.image_url"
                            :alt="form.image_desc || '修复图片'"
                            @error="handleImageError"
                          />
                        </div>

                        <div class="form-details">
                          <div v-if="form.image_desc" class="form-desc">
                            <strong>图片描述：</strong>{{ form.image_desc }}
                          </div>
                          <div v-if="form.restoration_opinion" class="form-opinion">
                            <strong>修复意见：</strong>{{ form.restoration_opinion }}
                          </div>
                          <div v-if="form.opinion_tags && form.opinion_tags.length > 0" class="form-tags">
                            <strong>标签：</strong>
                            <t-space>
                              <t-tag
                                v-for="tag in form.opinion_tags"
                                :key="tag"
                                theme="primary"
                                variant="light"
                                size="small"
                              >
                                {{ tag }}
                              </t-tag>
                            </t-space>
                          </div>
                          <div v-if="form.remark" class="form-remark">
                            <strong>备注：</strong>{{ form.remark }}
                          </div>
                        </div>
                      </div>

                      <!-- 回溯申请按钮（修复专家） -->
                      <div v-if="userRole === 'restorer' && workflowForms.length > 1" class="form-actions">
                        <t-button
                          theme="warning"
                          size="small"
                          @click="requestRollback(form)"
                        >
                          申请回溯到此步骤
                        </t-button>
                      </div>
                    </div>
                  </template>
                </t-timeline-item>
              </t-timeline>
            </div>
          </t-card>

          <!-- 评估历史 -->
          <t-card title="评估历史" class="evaluations-history" :bordered="false">
            <div v-if="workflowEvaluations.length === 0" class="empty-state">
              <t-icon name="star" size="48px" />
              <p>暂无评估记录</p>
            </div>
            <div v-else class="evaluations-list">
              <div
                v-for="evaluation in workflowEvaluations"
                :key="evaluation.evaluation_id"
                class="evaluation-item"
              >
                <div class="evaluation-header">
                  <div class="evaluation-info">
                    <span class="evaluation-expert">{{ evaluation.evaluator_name }}</span>
                    <span class="evaluation-score">
                      <t-tag theme="success" variant="light">
                        {{ evaluation.score }}分
                      </t-tag>
                    </span>
                  </div>
                  <div class="evaluation-time">{{ formatDate(evaluation.created_at) }}</div>
                </div>
                <div v-if="evaluation.comment" class="evaluation-comment">
                  <strong>评价意见：</strong>{{ evaluation.comment }}
                </div>
                <div v-if="evaluation.evaluation_file" class="evaluation-file">
                  <strong>支撑文件：</strong>
                  <t-link :href="evaluation.evaluation_file" target="_blank" theme="primary">
                    <t-icon name="download" />
                    下载文件
                  </t-link>
                </div>
              </div>
            </div>
          </t-card>

          <!-- 评估表单（评估专家） -->
          <t-card
            v-if="(userRole === 'evaluator' || userRole === 'admin') && workflowEvaluations.length === 0"
            title="提交评估"
            class="evaluation-form"
            :bordered="false"
          >
            <t-form
              ref="evaluationFormRef"
              :data="evaluationFormData"
              :rules="evaluationFormRules"
              :label-width="120"
              @submit="handleSubmitEvaluation"
            >
              <t-form-item name="score" label="评分">
                <t-input-number
                  v-model="evaluationFormData.score"
                  :min="0"
                  :max="100"
                  placeholder="请输入评分 (0-100)"
                  style="width: 200px;"
                />
                <div class="score-text">{{ evaluationFormData.score }}/100 分</div>
              </t-form-item>

              <t-form-item name="comment" label="评价意见">
                <t-textarea
                  v-model="evaluationFormData.comment"
                  placeholder="请输入评价意见..."
                  :maxlength="1000"
                  :autosize="{ minRows: 3, maxRows: 6 }"
                  show-count
                />
              </t-form-item>

              <t-form-item name="support_file" label="支撑文件">
                <t-upload
                  :files="supportFileList"
                  :max="1"
                  :size-limit="{ size: 100, unit: 'MB' }"
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                  theme="file-input"
                  placeholder="选择支撑文件"
                  :auto-upload="false"
                  :request-method="null"
                  @change="handleFileChange"
                  @remove="handleFileRemove"
                  @fail="handleFileUploadFail"
                />
                <div class="file-tip">支持PDF、Word、图片等格式，最大100MB</div>
              </t-form-item>

              <t-form-item class="form-actions">
                <t-space>
                  <t-button
                    theme="primary"
                    type="submit"
                    :loading="evaluationLoading"
                  >
                    提交评估
                  </t-button>
                  <t-button theme="default" @click="resetEvaluationForm">
                    重置
                  </t-button>
                </t-space>
              </t-form-item>
            </t-form>
          </t-card>
        </div>
      </t-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import Layout from '@/components/Layout.vue'
import { getEvaluationWorkflows, deleteWorkflow, batchDeleteWorkflows, getWorkflowDetail, submitEvaluation, getEvaluationStats } from '@/api/evaluation.js'
import request from '@/api/request.js'

// 作者信息
/**
 * 评估修复页面组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// 响应式数据
const loading = ref(false)
const searchValue = ref('')
const statusFilter = ref('')
const tableData = ref([])
const statsData = ref({})
const selectedRowKeys = ref([])
const detailDialogVisible = ref(false)
const currentWorkflow = ref(null)
const workflowForms = ref([])
const workflowEvaluations = ref([])
const userRole = ref('')
const evaluationLoading = ref(false)
const supportFileList = ref([])

// 存储工作流和评估数据用于统计计算
const workflowList = ref([])
const evaluationList = ref([])

const evaluationFormRef = ref()

// 评估表单数据
const evaluationFormData = reactive({
  score: 0,
  comment: '',
  support_file: null
})

// 评估表单验证规则
const evaluationFormRules = {
  score: [
    { required: true, message: '请给出评分', type: 'error' },
    { 
      validator: (val) => {
        const num = parseInt(val)
        return !isNaN(num) && num >= 0 && num <= 100
      }, 
      message: '评分必须是0-100之间的整数', 
      type: 'error' 
    }
  ],
  comment: [
    { required: false, message: '评价意见为可选', type: 'error' }
  ]
}

// 分页配置
const pagination = ref({
  defaultPageSize: 20,
  total: 0,
  defaultCurrent: 1,
  showJumper: true,
  showSizeChanger: true
})

// 表格列配置
const columns = [
  { colKey: 'row-select', type: 'multiple', width: 64, fixed: 'left' },
  {
    title: '标题',
    colKey: 'title',
    width: 250,
    ellipsis: true
  },
  {
    title: '发起人',
    colKey: 'initiator_name',
    width: 120
  },
  {
    title: '状态',
    colKey: 'status',
    width: 100,
    align: 'center'
  },
  {
    title: '完成时间',
    colKey: 'updated_at',
    width: 150,
    sorter: true
  },
  {
    title: '操作',
    colKey: 'op',
    width: 150,
    fixed: 'right'
  }
]

// 计算属性
const canDelete = computed(() => {
  return userRole.value === 'admin'
})

const rowKey = 'workflow_id'

// 方法
const loadData = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      search: searchValue.value,
      status: statusFilter.value === 'all' ? '' : statusFilter.value,
      page: page,
      limit: pagination.value.defaultPageSize
    }

    const response = await getEvaluationWorkflows(params)
    
    // 根据API文档，直接返回工作流数组
    const workflows = response.data || response || []
    
    // 为每个工作流检查评估状态并收集评估数据
    const allEvaluations = []
    const workflowsWithEvaluationStatus = await Promise.all(
      workflows.map(async (workflow) => {
        try {
          // 获取该工作流的评估记录
          const evaluations = await request({
            url: `/api/workflows/${workflow.workflow_id}/evaluations`,
            method: 'GET'
          })
          const workflowEvaluations = evaluations.data || evaluations || []
          
          // 收集评估数据用于统计计算
          allEvaluations.push(...workflowEvaluations)
          
          return {
            ...workflow,
            has_evaluation: workflowEvaluations.length > 0
          }
        } catch (error) {
          console.warn(`获取工作流 ${workflow.workflow_id} 评估状态失败:`, error)
          return {
            ...workflow,
            has_evaluation: false
          }
        }
      })
    )
    
    // 存储带有评估状态的工作流数据用于统计计算
    workflowList.value = workflowsWithEvaluationStatus
    // 存储评估数据用于统计计算
    evaluationList.value = allEvaluations
    
    // 根据筛选条件过滤数据
    let filteredWorkflows = workflowsWithEvaluationStatus
    
    if (statusFilter.value === 'evaluated') {
      filteredWorkflows = workflowsWithEvaluationStatus.filter(workflow => workflow.has_evaluation)
    } else if (statusFilter.value === 'unevaluated') {
      filteredWorkflows = workflowsWithEvaluationStatus.filter(workflow => !workflow.has_evaluation)
    }
    
    tableData.value = filteredWorkflows
    pagination.value.total = filteredWorkflows.length
  } catch (error) {
    console.error('加载评估工作流失败:', error)
    MessagePlugin.error('加载数据失败')
  } finally {
    loading.value = false
    // 数据加载完成后计算统计数据
    calculateStats()
  }
}

const loadStats = async () => {
  try {
    // 计算统计数据
    calculateStats()
  } catch (error) {
    console.error('计算统计数据失败:', error)
    // 静默失败，不显示错误
  }
}

// 计算统计数据
const calculateStats = () => {
  const now = new Date()
  const currentMonth = now.getMonth()
  const currentYear = now.getFullYear()
  
  console.log('开始计算统计数据...')
  console.log('工作流数据:', workflowList.value)
  console.log('评估数据:', evaluationList.value)
  
  // 调试：显示工作流的评估状态
  if (workflowList.value && workflowList.value.length > 0) {
    console.log('工作流评估状态详情:')
    workflowList.value.forEach((workflow, index) => {
      console.log(`工作流${index + 1}: ${workflow.title} - has_evaluation: ${workflow.has_evaluation}`)
    })
  }
  
  // 初始化统计数据
  let totalEvaluations = 0
  let totalPending = 0
  let totalEvaluated = 0
  let averageScore = 0
  let monthlyEvaluations = 0
  
  // 计算工作流统计
  if (workflowList.value && workflowList.value.length > 0) {
    // 总评估 = 待评估 + 已评估
    totalEvaluations = workflowList.value.length
    // 根据has_evaluation字段计算已评估和待评估数量
    totalEvaluated = workflowList.value.filter(workflow => workflow.has_evaluation).length
    totalPending = workflowList.value.filter(workflow => !workflow.has_evaluation).length
    
    console.log(`工作流统计 - 总评估: ${totalEvaluations}, 已评估: ${totalEvaluated}, 待评估: ${totalPending}`)
  }
  
  // 计算评估统计
  if (evaluationList.value && evaluationList.value.length > 0) {
    // 计算平均评分
    const validScores = evaluationList.value
      .filter(evaluation => evaluation.score !== null && evaluation.score !== undefined && evaluation.score >= 0)
      .map(evaluation => evaluation.score)
    
    if (validScores.length > 0) {
      averageScore = Math.round(
        validScores.reduce((sum, score) => sum + score, 0) / validScores.length
      )
    }
    
    // 计算本月评估数量
    monthlyEvaluations = evaluationList.value.filter(evaluation => {
      if (!evaluation.created_at) return false
      const evalDate = new Date(evaluation.created_at)
      return evalDate.getMonth() === currentMonth && evalDate.getFullYear() === currentYear
    }).length
    
    console.log(`评估统计 - 平均评分: ${averageScore}, 本月评估: ${monthlyEvaluations}`)
  }
  
  // 更新统计数据
  statsData.value = {
    total_evaluations: totalEvaluations,
    total_pending: totalPending,
    total_evaluated: totalEvaluated,
    average_score: averageScore,
    monthly_evaluations: monthlyEvaluations
  }
  
  console.log('最终统计数据:', statsData.value)
}

const handleSearch = () => {
  loadData(1)
}

const handleFilter = () => {
  loadData(1)
}

const handlePageChange = (current, pageInfo) => {
  pagination.value.defaultCurrent = current
  loadData(current)
}

const handleSelectChange = (value) => {
  selectedRowKeys.value = value
}

const refreshData = () => {
  loadData(pagination.value.defaultCurrent)
  loadStats()
}

const viewWorkflowDetails = async (row) => {
  try {
    currentWorkflow.value = row

    // 获取工作流详情、表单和评估记录
    const response = await getWorkflowDetail(row.workflow_id)
    workflowForms.value = response.forms || []
    workflowEvaluations.value = response.evaluations || []

    detailDialogVisible.value = true
  } catch (error) {
    console.error('加载工作流详情失败:', error)
    MessagePlugin.error('加载详情失败')
  }
}

const handleCloseDetailDialog = () => {
  detailDialogVisible.value = false
  currentWorkflow.value = null
  workflowForms.value = []
  workflowEvaluations.value = []
  resetEvaluationForm()
}

const handleDelete = async (row) => {
  if (!confirm('确定要删除这个工作流吗？此操作不可撤销！')) {
    return
  }

  try {
    await deleteWorkflow(row.workflow_id)
    MessagePlugin.success('删除成功')
    refreshData()
  } catch (error) {
    console.error('删除工作流失败:', error)
    MessagePlugin.error('删除失败')
  }
}

const handleBatchDelete = async () => {
  if (selectedRowKeys.value.length === 0) {
    MessagePlugin.warning('请先选择要删除的工作流')
    return
  }

  if (!confirm(`确定要删除选中的 ${selectedRowKeys.value.length} 条记录吗？此操作不可撤销！`)) {
    return
  }

  try {
    await batchDeleteWorkflows(selectedRowKeys.value)
    MessagePlugin.success('批量删除成功')
    selectedRowKeys.value = []
    refreshData()
  } catch (error) {
    console.error('批量删除失败:', error)
    MessagePlugin.error('批量删除失败')
  }
}

const handleFileChange = (value) => {
  try {
    supportFileList.value = value || []
    evaluationFormData.support_file = value && value.length > 0 ? value[0].raw : null
  } catch (error) {
    console.error('文件选择处理失败:', error)
    supportFileList.value = []
    evaluationFormData.support_file = null
  }
}

const handleFileRemove = () => {
  supportFileList.value = []
  evaluationFormData.support_file = null
}

const handleFileUploadFail = (error) => {
  console.error('文件上传失败:', error)
  MessagePlugin.error('文件上传失败，请重试')
  supportFileList.value = []
  evaluationFormData.support_file = null
}

const handleSubmitEvaluation = async (context) => {
  if (context.validateResult !== true) {
    return
  }

  evaluationLoading.value = true
  try {
    const evaluationData = {
      workflow_id: currentWorkflow.value.workflow_id,
      score: parseInt(evaluationFormData.score), // 确保评分是整数
      comment: evaluationFormData.comment,
      support_file: evaluationFormData.support_file
    }

    console.log('准备提交评估:', evaluationData)
    console.log('当前工作流:', currentWorkflow.value)
    console.log('工作流状态:', currentWorkflow.value.status)
    console.log('工作流是否已完成:', currentWorkflow.value.status === 'finished')
    
    // 检查用户权限
    const user = getCurrentUser()
    console.log('当前用户:', user)
    console.log('用户角色:', user?.role_key)
    
    // 检查工作流状态
    if (currentWorkflow.value.status !== 'finished') {
      MessagePlugin.error(`工作流状态为"${currentWorkflow.value.status}"，只有已完成的工作流才能进行评估`)
      return
    }

    await submitEvaluation(evaluationData)

    MessagePlugin.success('评估提交成功')

    // 刷新数据
    refreshData()
    handleCloseDetailDialog()
  } catch (error) {
    console.error('提交评估失败:', error)
    
    // 提供更详细的错误信息
    let errorMessage = '提交失败'
    if (error.response) {
      const { status, data } = error.response
      console.error('服务器响应错误:', { status, data })
      console.error('完整错误响应:', error.response)
      console.error('错误详情:', data)
      
      if (status === 500) {
        errorMessage = '服务器内部错误，请检查数据格式或联系管理员'
      } else if (status === 400) {
        errorMessage = data?.detail || data?.message || '请求参数错误'
      } else if (status === 401) {
        errorMessage = '登录已过期，请重新登录'
      } else if (status === 403) {
        errorMessage = '没有权限执行此操作'
      } else if (status === 404) {
        errorMessage = data?.detail || data?.message || '工作流不存在或未完成'
      } else if (status === 422) {
        errorMessage = data?.detail || data?.message || '请求参数格式错误'
      } else {
        errorMessage = data?.detail || data?.message || `请求失败 (${status})`
      }
    } else if (error.request) {
      errorMessage = '网络连接失败，请检查网络设置'
    } else {
      errorMessage = error.message || '请求配置错误'
    }
    
    MessagePlugin.error(errorMessage)
  } finally {
    evaluationLoading.value = false
  }
}

const resetEvaluationForm = () => {
  evaluationFormData.score = 0
  evaluationFormData.comment = ''
  evaluationFormData.support_file = null
  supportFileList.value = []
}

const requestRollback = async (form) => {
  // 这里可以实现回溯申请功能
  MessagePlugin.info('回溯申请功能开发中...')
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  const fallbackDiv = event.target.nextElementSibling
  if (fallbackDiv) {
    fallbackDiv.style.display = 'block'
  }
}

// 工具方法
const getStatusTheme = (status, hasEvaluation = false) => {
  if (hasEvaluation) return 'success'
  if (status === 'finished') return 'warning'
  return 'default'
}

const getStatusText = (status, hasEvaluation = false) => {
  if (hasEvaluation) return '已评估'
  if (status === 'finished') return '已完成'
  return status
}

const getFormDotColor = (stepNo) => {
  const colors = ['primary', 'success', 'warning', 'danger', 'default']
  return colors[(stepNo - 1) % colors.length]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取用户信息
const getCurrentUser = () => {
  const user = localStorage.getItem('currentUser')
  return user ? JSON.parse(user) : null
}

// 生命周期
onMounted(() => {
  const user = getCurrentUser()
  if (user) {
    userRole.value = user.role_key
  }

  // 加载数据
  loadData()
  loadStats()
})
</script>

<style lang="less" scoped>
.evaluation-container {
  padding: 24px;
  background-color: var(--td-bg-color-container);
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--td-text-color-primary);
    margin: 0 0 8px 0;
  }

  .page-description {
    font-size: 14px;
    color: var(--td-text-color-secondary);
    margin: 0;
  }
}

.toolbar-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--td-bg-color-container);
  border-radius: var(--td-radius-medium);
  border: 1px solid var(--td-border-level-1-color);

  .left-operations {
    display: flex;
    gap: 12px;
  }

  .right-operations {
    display: flex;
    align-items: center;
  }
}

.stats-section {
  margin-bottom: 24px;

  .stat-card {
    text-align: center;

    :deep(.t-card__body) {
      padding: 16px;
    }

    .stat-content {
      .stat-number {
        font-size: 24px;
        font-weight: 600;
        color: var(--td-text-color-primary);
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 12px;
        color: var(--td-text-color-secondary);
      }
    }
  }
}

.data-table-card {
  :deep(.t-card__body) {
    padding: 0;
  }
}

.workflow-detail {
  .workflow-info {
    margin-bottom: 24px;
  }

  .forms-history,
  .evaluations-history,
  .evaluation-form {
    margin-bottom: 24px;

    .empty-state {
      text-align: center;
      padding: 40px 20px;
      color: var(--td-text-color-placeholder);

      p {
        margin: 12px 0 0 0;
        font-size: 14px;
      }
    }
  }

  .forms-list {
    :deep(.t-timeline-item) {
      .form-item {
        background: var(--td-bg-color-container);
        border-radius: var(--td-radius-medium);
        padding: 16px;
        border: 1px solid var(--td-border-level-1-color);

        .form-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          h4 {
            margin: 0;
            color: var(--td-text-color-primary);
            font-size: 16px;
            font-weight: 600;
          }

          .form-meta {
            font-size: 12px;
            color: var(--td-text-color-placeholder);

            .form-submitter {
              margin-right: 12px;
            }
          }
        }

        .form-content {
          display: flex;
          gap: 16px;

          .form-image {
            flex-shrink: 0;

            img {
              max-width: 200px;
              height: auto;
              border-radius: var(--td-radius-small);
              border: 1px solid var(--td-border-level-1-color);
            }
          }

          .form-details {
            flex: 1;

            .form-desc,
            .form-opinion,
            .form-remark {
              margin-bottom: 8px;
              line-height: 1.6;
            }

            .form-tags {
              margin-bottom: 8px;
            }
          }
        }

        .form-actions {
          margin-top: 12px;
          text-align: right;
        }
      }
    }
  }

  .evaluations-list {
    .evaluation-item {
      background: var(--td-bg-color-container);
      border-radius: var(--td-radius-medium);
      padding: 16px;
      margin-bottom: 12px;
      border: 1px solid var(--td-border-level-1-color);

      .evaluation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .evaluation-info {
          display: flex;
          align-items: center;
          gap: 12px;

          .evaluation-expert {
            font-weight: 600;
            color: var(--td-text-color-primary);
          }
        }

        .evaluation-time {
          font-size: 12px;
          color: var(--td-text-color-placeholder);
        }
      }

      .evaluation-content,
      .evaluation-comment {
        margin-bottom: 8px;
        line-height: 1.6;
      }
    }
  }

  .evaluation-form {
    .score-text {
      margin-top: 8px;
      font-size: 14px;
      color: var(--td-text-color-secondary);
    }

    .file-tip {
      margin-top: 4px;
      font-size: 12px;
      color: var(--td-text-color-placeholder);
    }

    .form-actions {
      text-align: left;
      margin-top: 24px;
    }
  }

  .evaluation-file {
    margin-top: 8px;
    
    .t-link {
      margin-left: 8px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .evaluation-container {
    padding: 16px;
  }

  .toolbar-section {
    flex-direction: column;
    gap: 16px;

    .left-operations,
    .right-operations {
      width: 100%;
      justify-content: center;
    }

    .right-operations {
      flex-wrap: wrap;
      gap: 8px;
    }
  }

  .workflow-detail {
    .forms-list .form-content {
      flex-direction: column;

      .form-image img {
        max-width: 100%;
      }
    }
  }
}
</style>

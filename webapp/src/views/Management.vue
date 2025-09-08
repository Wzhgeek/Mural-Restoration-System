<template>
  <Layout>
    <div class="management-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h2 class="page-title">修复管理</h2>
        <p class="page-description">管理所有修复工作流程和回溯申请</p>
      </div>

      <!-- 管理员操作栏 -->
      <div class="admin-controls" v-if="isAdmin">
        <div class="left-operations">
          <t-button theme="primary" @click="refreshData">
            <template #icon>
              <t-icon name="refresh" />
            </template>
            刷新数据
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
            <t-option value="all" label="全部状态" />
            <t-option value="draft" label="草稿" />
            <t-option value="running" label="进行中" />
            <t-option value="finished" label="已完成" />
            <t-option value="paused" label="已暂停" />
            <t-option value="revoked" label="已撤销" />
          </t-select>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-section" v-if="statsData">
        <t-row :gutter="16">
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.total_workflows || 0 }}</div>
                <div class="stat-label">总工作流</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.filtered_running_workflows !== undefined ? statsData.filtered_running_workflows : (statsData.running_workflows || 0) }}</div>
                <div class="stat-label">进行中</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.filtered_finished_workflows !== undefined ? statsData.filtered_finished_workflows : (statsData.finished_workflows || 0) }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.pending_evaluations || 0 }}</div>
                <div class="stat-label">待评估</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.filtered_paused_workflows !== undefined ? statsData.filtered_paused_workflows : (statsData.paused_workflows || 0) }}</div>
                <div class="stat-label">已暂停</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ (statsData.completion_rate || 0).toFixed(1) }}%</div>
                <div class="stat-label">完成率</div>
              </div>
            </t-card>
          </t-col>
        </t-row>
      </div>

      <!-- 主要内容区域 -->
      <t-card class="workflows-card" :bordered="false">
        <template #header>
          <div class="card-header-content">
            <h3 class="card-title">所有工作流</h3>
            <div class="header-actions">
              <t-select
                v-model="sortBy"
                placeholder="排序方式"
                size="small"
                style="width: 120px; margin-right: 8px;"
                @change="handleSort"
              >
                <t-option value="created_at_desc" label="最新创建" />
                <t-option value="created_at_asc" label="最早创建" />
                <t-option value="updated_at_desc" label="最近更新" />
                <t-option value="status" label="状态排序" />
              </t-select>
              <t-button theme="default" variant="outline" size="small" @click="loadWorkflows">
                <template #icon>
                  <t-icon name="refresh" />
                </template>
              </t-button>
            </div>
          </div>
        </template>

        <div class="workflows-content">
          <div class="table-container">
            <t-table
              :data="workflowsData"
              :columns="workflowColumns"
              :loading="workflowsLoading"
              :selected-row-keys="selectedWorkflowKeys"
              :row-key="rowKey"
              :sort="sortInfo"
              :pagination="workflowPagination"
              vertical-align="top"
              hover
              stripe
              @select-change="handleWorkflowSelectChange"
              @sort-change="handleWorkflowSort"
              @page-change="handleWorkflowPageChange"
              :max-height="tableMaxHeight"
            >
            <template #status="{ row }">
              <t-tag
                :theme="getWorkflowStatusTheme(row.status)"
                variant="light"
              >
                {{ getWorkflowStatusText(row.status) }}
              </t-tag>
            </template>

            <template #created_at="{ row }">
              {{ formatDate(row.created_at) }}
            </template>

            <template #updated_at="{ row }">
              {{ formatDate(row.updated_at) }}
            </template>

            <template #op="slotProps">
              <t-space>
                <t-link theme="primary" @click="viewWorkflowDetail(slotProps.row)">
                  <t-icon name="view" />
                  查看
                </t-link>
                <t-link theme="danger" @click="handleDeleteWorkflow(slotProps.row)" v-if="canDelete">
                  <t-icon name="delete" />
                  删除
                </t-link>
              </t-space>
            </template>
          </t-table>
          </div>

          <!-- 批量操作按钮 -->
          <div class="batch-actions" v-if="selectedWorkflowKeys.length > 0 && canDelete">
            <t-space>
              <t-button theme="danger" @click="handleBatchDeleteWorkflows">
                <template #icon>
                  <t-icon name="delete" />
                </template>
                批量删除 ({{ selectedWorkflowKeys.length }})
              </t-button>
            </t-space>
          </div>
        </div>
      </t-card>

    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import Layout from '@/components/Layout.vue'
import request from '@/api/request.js'
import {
  getAllWorkflows,
  deleteWorkflow,
  batchDeleteWorkflows,
  getManagementStats
} from '@/api/management.js'

// 作者信息
/**
 * 修复管理页面组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// 响应式数据
const isAdmin = ref(false)
const searchValue = ref('')
const statusFilter = ref('all')
const sortBy = ref('created_at_desc')

const workflowsData = ref([])
const statsData = ref({})
const selectedWorkflowKeys = ref([])

const workflowsLoading = ref(false)
const tableMaxHeight = ref(500)


// 分页配置
const workflowPagination = ref({
  defaultCurrent: 1,
  defaultPageSize: 10,
  total: 0,
  showJumper: true,
  showSizeChanger: true,
  pageSizeOptions: [5, 10, 20, 50]
})

// 排序状态
const sortInfo = ref({})

// 表格列配置
const workflowColumns = [
  { colKey: 'row-select', type: 'multiple', width: 64, fixed: 'left' },
  {
    title: '工作流标题',
    colKey: 'title',
    width: 200,
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
    title: '创建时间',
    colKey: 'created_at',
    width: 150,
    sorter: true
  },
  {
    title: '最后更新',
    colKey: 'updated_at',
    width: 150,
    sorter: true
  },
  {
    title: '操作',
    colKey: 'op',
    width: 120,
    fixed: 'right'
  }
]

const rowKey = 'workflow_id'

// 计算属性
const canDelete = computed(() => {
  return isAdmin.value
})

// 方法

// 排序处理函数
const handleWorkflowSort = (sortInfo) => {
  if (sortInfo) {
    let sortBy = ''
    let sortOrder = 'asc'
    
    // 处理不同的排序事件格式
    if (Array.isArray(sortInfo) && sortInfo.length > 0) {
      // 数组格式
      const sort = sortInfo[0]
      sortBy = sort.sortBy || sort.colKey
      sortOrder = sort.descending ? 'desc' : 'asc'
    } else if (typeof sortInfo === 'object' && Object.keys(sortInfo).length > 0) {
      // 对象格式
      sortBy = Object.keys(sortInfo)[0]
      sortOrder = sortInfo[sortBy] === 'desc' ? 'desc' : 'asc'
    } else if (typeof sortInfo === 'string') {
      // 字符串格式
      sortBy = sortInfo
      sortOrder = 'asc'
    }
    
    if (sortBy) {
      // 对数据进行排序
      const sortedData = [...workflowsData.value].sort((a, b) => {
        let aValue = a[sortBy]
        let bValue = b[sortBy]
        
        // 处理日期字段
        if (sortBy === 'created_at' || sortBy === 'updated_at') {
          aValue = new Date(aValue).getTime()
          bValue = new Date(bValue).getTime()
        }
        
        if (sortOrder === 'desc') {
          return bValue - aValue
        } else {
          return aValue - bValue
        }
      })
      
      // 更新数据
      workflowsData.value = sortedData
      
      // 更新排序状态
      sortInfo.value = { [sortBy]: sortOrder }
    }
  }
}

const loadWorkflows = async (page = 1) => {
  workflowsLoading.value = true
  try {
    const params = {
      search: searchValue.value,
      status: statusFilter.value === 'all' ? '' : statusFilter.value,
      page: page,
      limit: workflowPagination.value.defaultPageSize
    }

    const response = await getAllWorkflows(params)
    // 处理后端返回的分页数据
    if (response && response.items) {
      workflowsData.value = response.items || []
      workflowPagination.value.total = response.total || 0
      workflowPagination.value.defaultCurrent = response.page || page
      
      // 更新统计卡片中的总工作流数为当前筛选条件下的总数
      if (statsData.value) {
        statsData.value.total_workflows = response.total || 0
        // 根据当前筛选条件更新其他统计数据
        updateFilteredStats(response.items || [])
      }
    } else {
      // 兼容旧格式（直接返回数组）
      workflowsData.value = response || []
      workflowPagination.value.total = response.length || 0
      workflowPagination.value.defaultCurrent = page
      
      // 更新统计卡片中的总工作流数为当前筛选条件下的总数
      if (statsData.value) {
        statsData.value.total_workflows = response.length || 0
        // 根据当前筛选条件更新其他统计数据
        updateFilteredStats(response || [])
      }
    }
  } catch (error) {
    console.error('加载工作流失败:', error)
    MessagePlugin.error('加载工作流失败')
  } finally {
    workflowsLoading.value = false
  }
}


const loadStats = async () => {
  try {
    const response = await getManagementStats()
    // 根据后端接口文档，直接返回统计数据对象
    statsData.value = response || {}
  } catch (error) {
    // 静默失败，不显示错误
  }
}

// 根据当前筛选条件更新统计数据
const updateFilteredStats = (workflows) => {
  if (!statsData.value) return
  
  // 计算当前筛选条件下的统计数据
  const runningCount = workflows.filter(w => w.status === 'running').length
  const finishedCount = workflows.filter(w => w.status === 'finished').length
  const pausedCount = workflows.filter(w => w.status === 'paused').length
  
  // 更新统计数据（保持原有的全局统计，但添加筛选后的统计）
  statsData.value.filtered_running_workflows = runningCount
  statsData.value.filtered_finished_workflows = finishedCount
  statsData.value.filtered_paused_workflows = pausedCount
}

// 重置为全局统计数据
const resetToGlobalStats = () => {
  if (statsData.value) {
    // 清除筛选后的统计数据，恢复显示全局统计
    delete statsData.value.filtered_running_workflows
    delete statsData.value.filtered_finished_workflows
    delete statsData.value.filtered_paused_workflows
  }
}

const handleSearch = () => {
  workflowPagination.value.defaultCurrent = 1
  // 如果搜索条件为空，重置为全局统计
  if (!searchValue.value.trim()) {
    resetToGlobalStats()
  }
  loadWorkflows(1)
}

const handleFilter = () => {
  workflowPagination.value.defaultCurrent = 1
  // 如果筛选条件为"全部状态"，重置为全局统计
  if (statusFilter.value === 'all') {
    resetToGlobalStats()
  }
  loadWorkflows(1)
}

const handleSort = () => {
  workflowPagination.value.defaultCurrent = 1
  loadWorkflows(1)
}

const handleWorkflowPageChange = (current, pageInfo) => {
  workflowPagination.value.defaultCurrent = current
  if (pageInfo && pageInfo.pageSize) {
    workflowPagination.value.defaultPageSize = pageInfo.pageSize
  }
  loadWorkflows(current)
}


const handleWorkflowSelectChange = (value) => {
  selectedWorkflowKeys.value = value
}


const refreshData = () => {
  loadWorkflows(workflowPagination.value.defaultCurrent)
  loadStats()
}

const viewWorkflowDetail = async (row) => {
  try {
    // 获取工作流详情，包括表单和评估信息
    const [formsResponse, evaluationsResponse] = await Promise.all([
      request({ url: `/api/workflows/${row.workflow_id}/forms`, method: 'GET' }),
      request({ url: `/api/workflows/${row.workflow_id}/evaluations`, method: 'GET' })
    ])
    
    const forms = formsResponse || []
    const evaluations = evaluationsResponse || []
    
    // 显示工作流详情对话框
    showWorkflowDetailDialog(row, forms, evaluations)
  } catch (error) {

    MessagePlugin.error('获取工作流详情失败')
  }
}

const handleDeleteWorkflow = async (row) => {
  if (!confirm('确定要删除这个工作流吗？此操作不可撤销！')) {
    return
  }

  try {
    await deleteWorkflow(row.workflow_id)
    MessagePlugin.success('删除成功')
    refreshData()
  } catch (error) {

    MessagePlugin.error('删除失败')
  }
}

const handleBatchDeleteWorkflows = async () => {
  if (selectedWorkflowKeys.value.length === 0) {
    MessagePlugin.warning('请先选择要删除的工作流')
    return
  }

  if (!confirm(`确定要删除选中的 ${selectedWorkflowKeys.value.length} 条记录吗？此操作不可撤销！`)) {
    return
  }

  try {
    await batchDeleteWorkflows(selectedWorkflowKeys.value)
    MessagePlugin.success('批量删除成功')
    selectedWorkflowKeys.value = []
    refreshData()
  } catch (error) {
    MessagePlugin.error('批量删除失败')
  }
}


// 工具方法
const getWorkflowStatusTheme = (status) => {
  switch (status) {
    case 'finished': return 'success'
    case 'running': return 'warning'
    case 'draft': return 'info'
    case 'paused': return 'warning'
    case 'revoked': return 'danger'
    default: return 'default'
  }
}

const getWorkflowStatusText = (status) => {
  switch (status) {
    case 'finished': return '已完成'
    case 'running': return '进行中'
    case 'draft': return '草稿'
    case 'paused': return '已暂停'
    case 'revoked': return '已撤销'
    default: return status
  }
}


const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 显示工作流详情对话框
const showWorkflowDetailDialog = (workflow, forms, evaluations) => {
  const dialog = document.createElement('div')
  dialog.className = 't-dialog__mask'
  dialog.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
  `
  
  dialog.innerHTML = `
    <div class="workflow-detail-dialog" style="
      background: white;
      border-radius: 8px;
      max-width: 1000px;
      max-height: 80vh;
      width: 90%;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    ">
      <div class="dialog-header" style="
        padding: 20px;
        border-bottom: 1px solid #e7e7e7;
        display: flex;
        justify-content: space-between;
        align-items: center;
      ">
        <h3 style="margin: 0; font-size: 18px; font-weight: 600;">工作流详情</h3>
        <button class="close-btn" style="
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #666;
        ">&times;</button>
      </div>
      
      <div class="dialog-content" style="
        flex: 1;
        overflow-y: auto;
        padding: 20px;
      ">
        <div class="workflow-info" style="margin-bottom: 24px;">
          <h4 style="margin: 0 0 12px 0; color: #333;">基本信息</h4>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div><strong>标题：</strong>${workflow.title}</div>
            <div><strong>发起人：</strong>${workflow.initiator_name}</div>
            <div><strong>状态：</strong>${getWorkflowStatusText(workflow.status)}</div>
            <div><strong>当前步骤：</strong>第 ${workflow.current_step} 步</div>
            <div><strong>创建时间：</strong>${formatDate(workflow.created_at)}</div>
            <div><strong>更新时间：</strong>${formatDate(workflow.updated_at)}</div>
          </div>
          ${workflow.description ? `<div style="margin-top: 12px;"><strong>描述：</strong>${workflow.description}</div>` : ''}
        </div>
        
        <div class="forms-section" style="margin-bottom: 24px;">
          <h4 style="margin: 0 0 12px 0; color: #333;">修复表单历史</h4>
          ${forms.length === 0 ? '<p style="color: #666; text-align: center; padding: 20px;">暂无表单</p>' : ''}
          ${forms.map((form, index) => `
            <div class="form-item" style="
              border: 1px solid #e7e7e7;
              border-radius: 6px;
              padding: 16px;
              margin-bottom: 12px;
              background: #fafafa;
            ">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong>第 ${form.step_no} 步 - ${form.submitter_name}</strong>
                <span style="font-size: 12px; color: #666;">${formatDate(form.created_at)}</span>
              </div>
              ${form.image_url ? `
                <div style="margin-bottom: 8px;">
                  <img src="${form.image_url}" style="max-width: 200px; height: auto; border-radius: 4px;" 
                       onerror="this.style.display='none'">
                </div>
              ` : ''}
              ${form.image_desc ? `<div style="margin-bottom: 8px;"><strong>图片描述：</strong>${form.image_desc}</div>` : ''}
              ${form.restoration_opinion ? `<div style="margin-bottom: 8px;"><strong>修复意见：</strong>${form.restoration_opinion}</div>` : ''}
              ${form.opinion_tags && form.opinion_tags.length > 0 ? `
                <div style="margin-bottom: 8px;">
                  <strong>标签：</strong>
                  ${form.opinion_tags.map(tag => `<span style="background: #e7e7e7; padding: 2px 6px; border-radius: 3px; font-size: 12px; margin-right: 4px;">${tag}</span>`).join('')}
                </div>
              ` : ''}
              ${form.remark ? `<div><strong>备注：</strong>${form.remark}</div>` : ''}
            </div>
          `).join('')}
        </div>
        
        <div class="evaluations-section">
          <h4 style="margin: 0 0 12px 0; color: #333;">评估意见</h4>
          ${evaluations.length === 0 ? '<p style="color: #666; text-align: center; padding: 20px;">暂无评估</p>' : ''}
          ${evaluations.map(evaluation => `
            <div class="evaluation-item" style="
              border: 1px solid #e7e7e7;
              border-radius: 6px;
              padding: 16px;
              margin-bottom: 12px;
              background: #fafafa;
            ">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong>${evaluation.evaluator_name}</strong>
                <span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">评分: ${evaluation.score}</span>
              </div>
              ${evaluation.comment ? `<div style="margin-bottom: 8px;">${evaluation.comment}</div>` : ''}
              ${evaluation.evaluation_file ? `
                <div>
                  <a href="${evaluation.evaluation_file}" target="_blank" style="color: #007bff; text-decoration: none;">
                    📄 查看评估文件
                  </a>
                </div>
              ` : ''}
              <div style="font-size: 12px; color: #666; margin-top: 8px;">${formatDate(evaluation.created_at)}</div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `
  
  document.body.appendChild(dialog)
  
  // 关闭按钮事件
  dialog.querySelector('.close-btn').onclick = () => {
    document.body.removeChild(dialog)
  }
  
  // 点击背景关闭
  dialog.onclick = (e) => {
    if (e.target === dialog) {
      document.body.removeChild(dialog)
    }
  }
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
    isAdmin.value = user.role_key === 'admin'
  }

  // 加载数据
  loadWorkflows()
  loadStats()
})
</script>

<style lang="less" scoped>
.management-container {
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

.admin-controls {
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

.workflows-card {
  .card-header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;

    .card-title {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--td-text-color-primary);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .workflows-content {
    .table-container {
      border: 1px solid var(--td-border-level-1-color);
      border-radius: var(--td-radius-small);
      overflow: hidden;

      :deep(.t-table) {
        border: none;
      }
    }

    .pagination-container {
      margin-top: 16px;
      text-align: center;
      padding: 16px 0;
    }
  }
}

.batch-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--td-border-level-1-color);
  text-align: center;
}


// 响应式设计
@media (max-width: 768px) {
  .management-container {
    padding: 16px;
  }

  .admin-controls {
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

  .workflows-card {
    .table-container {
      :deep(.t-table) {
        font-size: 12px;
      }
    }
  }
}
</style>

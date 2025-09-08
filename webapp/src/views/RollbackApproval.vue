<template>
  <Layout>
    <div class="rollback-approval-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h2 class="page-title">回溯审批</h2>
        <p class="page-description">管理和审批所有回溯申请</p>
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
            placeholder="搜索回溯申请..."
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
            <t-option value="pending" label="待审批" />
            <t-option value="approved" label="已批准" />
            <t-option value="rejected" label="已拒绝" />
          </t-select>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-section" v-if="statsData">
        <t-row :gutter="16">
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.total_rollbacks || 0 }}</div>
                <div class="stat-label">总申请数</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.pending_rollbacks || 0 }}</div>
                <div class="stat-label">待审批</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.approved_rollbacks || 0 }}</div>
                <div class="stat-label">已批准</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.rejected_rollbacks || 0 }}</div>
                <div class="stat-label">已拒绝</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statsData.today_rollbacks || 0 }}</div>
                <div class="stat-label">今日申请</div>
              </div>
            </t-card>
          </t-col>
          <t-col :span="4">
            <t-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ (statsData.approval_rate || 0).toFixed(1) }}%</div>
                <div class="stat-label">批准率</div>
              </div>
            </t-card>
          </t-col>
        </t-row>
      </div>

      <!-- 主要内容区域 -->
      <t-card class="rollback-requests-card" :bordered="false">
        <template #header>
          <div class="card-header-content">
            <h3 class="card-title">回溯申请列表</h3>
            <div class="header-actions">
              <t-select
                v-model="sortBy"
                placeholder="排序方式"
                size="small"
                style="width: 120px; margin-right: 8px;"
                @change="handleSort"
              >
                <t-option value="created_at_desc" label="最新申请" />
                <t-option value="created_at_asc" label="最早申请" />
                <t-option value="status" label="状态排序" />
                <t-option value="workflow_id" label="工作流ID" />
              </t-select>
              <t-button theme="default" variant="outline" size="small" @click="loadRollbackRequests">
                <template #icon>
                  <t-icon name="refresh" />
                </template>
              </t-button>
            </div>
          </div>
        </template>

        <div v-if="rollbackRequestsData.length === 0 && !loading" class="empty-state">
          <t-icon name="file" size="48px" />
          <p>暂无回溯申请</p>
        </div>

        <div v-else class="rollback-table-container">
          <t-table
            :data="rollbackRequestsData"
            :columns="rollbackColumns"
            :loading="loading"
            :selected-row-keys="selectedRollbackIds"
            row-key="rollback_id"
            :sort="sortInfo"
            :pagination="pagination"
            vertical-align="top"
            hover
            @select-change="handleSelectChange"
            @sort-change="handleTableSort"
            @page-change="handlePageChange"
            max-height="500px"
          >
            <template #status="{ row }">
              <t-tag
                :theme="getRollbackStatusTheme(row.status)"
                variant="light"
              >
                {{ getRollbackStatusText(row.status) }}
              </t-tag>
            </template>

            <template #created_at="{ row }">
              {{ formatDate(row.created_at) }}
            </template>

            <template #approved_at="{ row }">
              {{ row.approved_at ? formatDate(row.approved_at) : '-' }}
            </template>

            <template #reason="{ row }">
              <div class="reason-cell">
                <t-tooltip :content="row.reason" placement="top">
                  <span class="reason-text">{{ truncateText(row.reason, 50) }}</span>
                </t-tooltip>
              </div>
            </template>

            <template #op="{ row }">
              <t-space>
                <t-link theme="primary" @click="viewRollbackDetail(row)">
                  <t-icon name="view" />
                  查看详情
                </t-link>
                <t-link 
                  theme="success" 
                  @click="handleApproveRollback(row, 'approved')" 
                  v-if="row.status === 'pending' && canApprove"
                >
                  <t-icon name="check" />
                  批准
                </t-link>
                <t-link 
                  theme="danger" 
                  @click="handleApproveRollback(row, 'rejected')" 
                  v-if="row.status === 'pending' && canApprove"
                >
                  <t-icon name="close" />
                  拒绝
                </t-link>
                <t-link 
                  theme="danger" 
                  @click="handleDeleteRollback(row)" 
                  v-if="canDelete"
                >
                  <t-icon name="delete" />
                  删除
                </t-link>
              </t-space>
            </template>
          </t-table>

          <!-- 批量操作按钮 -->
          <div class="batch-actions" v-if="selectedRollbackIds.length > 0 && canDelete">
            <t-space>
              <t-button theme="success" @click="handleBatchApprove('approved')" v-if="canBatchApprove">
                <template #icon>
                  <t-icon name="check" />
                </template>
                批量批准 ({{ selectedRollbackIds.length }})
              </t-button>
              <t-button theme="warning" @click="handleBatchApprove('rejected')" v-if="canBatchReject">
                <template #icon>
                  <t-icon name="close" />
                </template>
                批量拒绝 ({{ selectedRollbackIds.length }})
              </t-button>
              <t-button theme="danger" @click="handleBatchDelete">
                <template #icon>
                  <t-icon name="delete" />
                </template>
                批量删除 ({{ selectedRollbackIds.length }})
              </t-button>
            </t-space>
          </div>
        </div>
      </t-card>

      <!-- 审批确认对话框 -->
      <t-dialog
        v-model:visible="approvalDialogVisible"
        :header="approvalAction === 'approved' ? '确认批准' : '确认拒绝'"
        width="500px"
        @confirm="confirmApproval"
        @cancel="cancelApproval"
      >
        <div class="approval-confirm-content">
          <p>确定要{{ approvalAction === 'approved' ? '批准' : '拒绝' }}这个回溯申请吗？</p>
          <div class="approval-details">
            <p><strong>申请人：</strong>{{ approvalTarget?.requester_name }}</p>
            <p><strong>工作流：</strong>#{{ approvalTarget?.workflow_id }}</p>
            <p><strong>申请原因：</strong>{{ approvalTarget?.reason }}</p>
          </div>
          <t-textarea
            v-model="approvalComment"
            placeholder="请输入审批意见（可选）"
            :maxlength="500"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </div>

        <template #footer>
          <t-space>
            <t-button theme="default" @click="cancelApproval">
              取消
            </t-button>
            <t-button
              :theme="approvalAction === 'approved' ? 'success' : 'danger'"
              @click="confirmApproval"
            >
              {{ approvalAction === 'approved' ? '批准申请' : '拒绝申请' }}
            </t-button>
          </t-space>
        </template>
      </t-dialog>

      <!-- 批量审批确认对话框 -->
      <t-dialog
        v-model:visible="batchApprovalDialogVisible"
        :header="batchApprovalAction === 'approved' ? '批量批准确认' : '批量拒绝确认'"
        width="500px"
        @confirm="confirmBatchApproval"
        @cancel="cancelBatchApproval"
      >
        <div class="approval-confirm-content">
          <p>确定要{{ batchApprovalAction === 'approved' ? '批准' : '拒绝' }}选中的 {{ selectedRollbackIds.length }} 个回溯申请吗？</p>
          <t-textarea
            v-model="batchApprovalComment"
            placeholder="请输入批量审批意见（可选）"
            :maxlength="500"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </div>

        <template #footer>
          <t-space>
            <t-button theme="default" @click="cancelBatchApproval">
              取消
            </t-button>
            <t-button
              :theme="batchApprovalAction === 'approved' ? 'success' : 'danger'"
              @click="confirmBatchApproval"
            >
              {{ batchApprovalAction === 'approved' ? '批量批准' : '批量拒绝' }}
            </t-button>
          </t-space>
        </template>
      </t-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import Layout from '@/components/Layout.vue'
import {
  getRollbackRequests,
  approveRollback,
  batchDeleteRollbacks,
  getManagementStats
} from '@/api/management.js'
import request from '@/api/request.js'

/**
 * 回溯审批页面组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// 响应式数据
const isAdmin = ref(false)
const canApprove = ref(false)
const canDelete = ref(false)
const searchValue = ref('')
const statusFilter = ref('all')
const sortBy = ref('created_at_desc')

const rollbackRequestsData = ref([])
const statsData = ref({})
const selectedRollbackIds = ref([])
const loading = ref(false)

// 审批相关
const approvalDialogVisible = ref(false)
const approvalAction = ref('')
const approvalTarget = ref(null)
const approvalComment = ref('')

// 批量审批相关
const batchApprovalDialogVisible = ref(false)
const batchApprovalAction = ref('')
const batchApprovalComment = ref('')

// 分页配置
const pagination = ref({
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
const rollbackColumns = [
  { colKey: 'row-select', type: 'multiple', width: 64, fixed: 'left' },
  {
    title: '申请ID',
    colKey: 'rollback_id',
    width: 100,
    align: 'center'
  },
  {
    title: '工作流ID',
    colKey: 'workflow_id',
    width: 120,
    align: 'center'
  },
  {
    title: '申请人',
    colKey: 'requester_name',
    width: 120
  },
  {
    title: '目标表单ID',
    colKey: 'target_form_id',
    width: 120,
    align: 'center'
  },
  {
    title: '申请原因',
    colKey: 'reason',
    width: 200,
    ellipsis: true
  },
  {
    title: '状态',
    colKey: 'status',
    width: 100,
    align: 'center'
  },
  {
    title: '申请时间',
    colKey: 'created_at',
    width: 150,
    sorter: true
  },
  {
    title: '审批时间',
    colKey: 'approved_at',
    width: 150,
    sorter: true
  },
  {
    title: '操作',
    colKey: 'op',
    width: 200,
    fixed: 'right'
  }
]

// 计算属性
const canBatchApprove = computed(() => {
  return canApprove.value && selectedRollbackIds.value.some(id => {
    const request = rollbackRequestsData.value.find(r => r.rollback_id === id)
    return request && request.status === 'pending'
  })
})

const canBatchReject = computed(() => {
  return canApprove.value && selectedRollbackIds.value.some(id => {
    const request = rollbackRequestsData.value.find(r => r.rollback_id === id)
    return request && request.status === 'pending'
  })
})

// 方法
const loadRollbackRequests = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      search: searchValue.value,
      status: statusFilter.value === 'all' ? '' : statusFilter.value,
      page: page,
      limit: pagination.value.defaultPageSize,
      sort_by: sortBy.value
    }

    const response = await getRollbackRequests(params)
    
    // 处理后端返回的分页数据
    if (response && response.items) {
      rollbackRequestsData.value = response.items || []
      pagination.value.total = response.total || 0
      pagination.value.defaultCurrent = response.page || 1
      
      // 计算统计数据
      calculateRollbackStats(response.items || [])
    } else {
      // 兼容旧格式（直接返回数组）
      rollbackRequestsData.value = response || []
      pagination.value.total = response.length || 0
      
      // 计算统计数据
      calculateRollbackStats(response || [])
    }
  } catch (error) {
    console.error('加载回溯申请失败:', error)
    MessagePlugin.error('加载回溯申请失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await getManagementStats()
    statsData.value = response || {}
  } catch (error) {
    // 静默失败，不显示错误
    console.error('加载统计数据失败:', error)
  }
}

// 计算回溯申请统计数据
const calculateRollbackStats = (rollbackRequests) => {
  if (!rollbackRequests || rollbackRequests.length === 0) {
    // 如果没有数据，重置统计
    statsData.value = {
      total_rollbacks: 0,
      pending_rollbacks: 0,
      approved_rollbacks: 0,
      rejected_rollbacks: 0,
      today_rollbacks: 0,
      approval_rate: 0
    }
    return
  }
  
  // 计算各种状态的申请数量
  const total = rollbackRequests.length
  const pending = rollbackRequests.filter(r => r.status === 'pending').length
  const approved = rollbackRequests.filter(r => r.status === 'approved').length
  const rejected = rollbackRequests.filter(r => r.status === 'rejected').length
  
  // 计算今日申请数量
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayRequests = rollbackRequests.filter(r => {
    const requestDate = new Date(r.created_at)
    requestDate.setHours(0, 0, 0, 0)
    return requestDate.getTime() === today.getTime()
  }).length
  
  // 计算批准率
  const processedCount = approved + rejected
  const approvalRate = processedCount > 0 ? (approved / processedCount * 100) : 0
  
  // 更新统计数据
  statsData.value = {
    total_rollbacks: total,
    pending_rollbacks: pending,
    approved_rollbacks: approved,
    rejected_rollbacks: rejected,
    today_rollbacks: todayRequests,
    approval_rate: Math.round(approvalRate * 10) / 10 // 保留一位小数
  }
}

const handleSearch = () => {
  pagination.value.defaultCurrent = 1
  loadRollbackRequests(1)
}

const handleFilter = () => {
  pagination.value.defaultCurrent = 1
  loadRollbackRequests(1)
}

const handleSort = () => {
  pagination.value.defaultCurrent = 1
  loadRollbackRequests(1)
}

const handleTableSort = (sortInfo) => {
  if (sortInfo && Object.keys(sortInfo).length > 0) {
    const sortBy = Object.keys(sortInfo)[0]
    const sortOrder = sortInfo[sortBy] === 'desc' ? 'desc' : 'asc'
    sortBy.value = `${sortBy}_${sortOrder}`
    handleSort()
  }
}

const handlePageChange = (current, pageInfo) => {
  pagination.value.defaultCurrent = current
  if (pageInfo && pageInfo.pageSize) {
    pagination.value.defaultPageSize = pageInfo.pageSize
  }
  loadRollbackRequests(current)
}

const handleSelectChange = (value) => {
  selectedRollbackIds.value = value
}

const refreshData = () => {
  loadRollbackRequests(pagination.value.defaultCurrent)
  // 注意：统计现在由 loadRollbackRequests() 中的 calculateRollbackStats() 自动计算
}

// 单个审批操作
const handleApproveRollback = (request, action) => {
  approvalTarget.value = request
  approvalAction.value = action
  approvalComment.value = ''
  approvalDialogVisible.value = true
}

const confirmApproval = async () => {
  if (!approvalTarget.value) return

  try {
    await approveRollback(
      approvalTarget.value.rollback_id,
      approvalAction.value,
      approvalComment.value
    )

    const actionText = approvalAction.value === 'approved' ? '批准' : '拒绝'
    MessagePlugin.success(`${actionText}成功`)

    // 关闭对话框并刷新数据
    approvalDialogVisible.value = false
    approvalTarget.value = null
    approvalAction.value = ''
    approvalComment.value = ''

    // 刷新数据（会自动重新计算统计）
    refreshData()
  } catch (error) {
    console.error('审批失败:', error)
    const actionText = approvalAction.value === 'approved' ? '批准' : '拒绝'
    MessagePlugin.error(`${actionText}失败`)
  }
}

const cancelApproval = () => {
  approvalDialogVisible.value = false
  approvalTarget.value = null
  approvalAction.value = ''
  approvalComment.value = ''
}

// 批量审批操作
const handleBatchApprove = (action) => {
  if (selectedRollbackIds.value.length === 0) {
    MessagePlugin.warning('请先选择要审批的申请')
    return
  }

  batchApprovalAction.value = action
  batchApprovalComment.value = ''
  batchApprovalDialogVisible.value = true
}

const confirmBatchApproval = async () => {
  if (selectedRollbackIds.value.length === 0) return

  try {
    // 批量处理每个选中的申请
    const promises = selectedRollbackIds.value.map(id =>
      approveRollback(id, batchApprovalAction.value, batchApprovalComment.value)
    )

    await Promise.all(promises)

    const actionText = batchApprovalAction.value === 'approved' ? '批准' : '拒绝'
    MessagePlugin.success(`批量${actionText}成功`)

    // 关闭对话框并刷新数据
    batchApprovalDialogVisible.value = false
    batchApprovalAction.value = ''
    batchApprovalComment.value = ''
    selectedRollbackIds.value = []

    // 刷新数据（会自动重新计算统计）
    refreshData()
  } catch (error) {
    console.error('批量审批失败:', error)
    const actionText = batchApprovalAction.value === 'approved' ? '批准' : '拒绝'
    MessagePlugin.error(`批量${actionText}失败`)
  }
}

const cancelBatchApproval = () => {
  batchApprovalDialogVisible.value = false
  batchApprovalAction.value = ''
  batchApprovalComment.value = ''
}

// 删除操作
const handleDeleteRollback = async (request) => {
  if (!confirm('确定要删除这个回溯申请吗？此操作不可撤销！')) {
    return
  }

  try {
    await request({ url: `/admin/rollback-requests/${request.rollback_id}`, method: 'DELETE' })
    MessagePlugin.success('删除成功')
    refreshData()
  } catch (error) {
    console.error('删除失败:', error)
    MessagePlugin.error('删除失败')
  }
}

const handleBatchDelete = async () => {
  if (selectedRollbackIds.value.length === 0) {
    MessagePlugin.warning('请先选择要删除的申请')
    return
  }

  if (!confirm(`确定要删除选中的 ${selectedRollbackIds.value.length} 条记录吗？此操作不可撤销！`)) {
    return
  }

  try {
    await batchDeleteRollbacks(selectedRollbackIds.value)
    MessagePlugin.success('批量删除成功')
    selectedRollbackIds.value = []
    refreshData()
  } catch (error) {
    console.error('批量删除失败:', error)
    MessagePlugin.error('批量删除失败')
  }
}

// 查看详情
const viewRollbackDetail = (request) => {
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
    <div class="rollback-detail-dialog" style="
      background: white;
      border-radius: 8px;
      max-width: 600px;
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
        <h3 style="margin: 0; font-size: 18px; font-weight: 600;">回溯申请详情</h3>
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
        <div class="rollback-info" style="margin-bottom: 20px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            <div><strong>申请ID：</strong>${request.rollback_id}</div>
            <div><strong>工作流ID：</strong>${request.workflow_id}</div>
            <div><strong>申请人：</strong>${request.requester_name}</div>
            <div><strong>状态：</strong>${getRollbackStatusText(request.status)}</div>
            <div><strong>申请时间：</strong>${formatDate(request.created_at)}</div>
            ${request.approved_at ? `<div><strong>审批时间：</strong>${formatDate(request.approved_at)}</div>` : ''}
          </div>
          <div style="margin-bottom: 12px;">
            <strong>目标表单ID：</strong>${request.target_form_id}
          </div>
          <div style="margin-bottom: 12px;">
            <strong>申请原因：</strong>
            <div style="background: #f8f9fa; padding: 12px; border-radius: 4px; margin-top: 8px; white-space: pre-wrap;">${request.reason}</div>
          </div>
          ${request.support_file_url ? `
            <div>
              <strong>支撑文件：</strong>
              <div style="margin-top: 8px;">
                <a href="${request.support_file_url}" target="_blank" style="color: #007bff; text-decoration: none;">
                  📎 查看支撑文件
                </a>
              </div>
            </div>
          ` : ''}
          ${request.comment ? `
            <div style="margin-top: 12px;">
              <strong>审批意见：</strong>
              <div style="background: #f8f9fa; padding: 12px; border-radius: 4px; margin-top: 8px; white-space: pre-wrap;">${request.comment}</div>
            </div>
          ` : ''}
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

// 工具方法
const getRollbackStatusTheme = (status) => {
  switch (status) {
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    case 'pending': return 'warning'
    default: return 'default'
  }
}

const getRollbackStatusText = (status) => {
  switch (status) {
    case 'approved': return '已批准'
    case 'rejected': return '已拒绝'
    case 'pending': return '待审批'
    default: return status
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
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
    canApprove.value = user.role_key === 'admin'
    canDelete.value = user.role_key === 'admin'
  }

  // 加载数据
  loadRollbackRequests()
  // 注意：loadStats() 现在由 loadRollbackRequests() 中的 calculateRollbackStats() 处理
})
</script>

<style lang="less" scoped>
.rollback-approval-container {
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

.rollback-requests-card {
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

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: var(--td-text-color-placeholder);

    p {
      margin: 12px 0 0 0;
      font-size: 14px;
    }
  }

  .rollback-table-container {
    .reason-cell {
      .reason-text {
        display: block;
        line-height: 1.4;
      }
    }

    .pagination-container {
      margin-top: 16px;
      text-align: center;
    }
  }
}

.batch-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--td-border-level-1-color);
  text-align: center;
}

.approval-confirm-content {
  p {
    margin-bottom: 16px;
    color: var(--td-text-color-primary);
  }

  .approval-details {
    background: var(--td-bg-color-page);
    padding: 12px;
    border-radius: var(--td-radius-small);
    margin-bottom: 16px;

    p {
      margin: 0 0 8px 0;
      font-size: 14px;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .rollback-approval-container {
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

  .stats-section {
    .t-row {
      :deep(.t-col) {
        margin-bottom: 12px;
      }
    }
  }
}
</style>

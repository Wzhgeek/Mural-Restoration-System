<template>
  <Layout>
    <div class="rollback-history-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">回溯历史</h2>
      <p class="page-description">查看历史回溯申请记录和审批状态</p>
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
      </div>

      <div class="right-operations">
        <t-input
          v-model="searchValue"
          placeholder="搜索回溯记录..."
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
          placeholder="审批状态"
          clearable
          style="width: 120px; margin-right: 8px;"
          @change="handleFilter"
        >
          <t-option value="all" label="全部状态" />
          <t-option value="pending" label="待审批" />
          <t-option value="approved" label="已批准" />
          <t-option value="rejected" label="已拒绝" />
        </t-select>

        <t-date-range-picker
          v-model="dateRange"
          placeholder="选择时间范围"
          style="width: 240px;"
          @change="handleDateRangeChange"
        />
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section" v-if="statsData">
      <t-row :gutter="16">
        <t-col :span="4">
          <t-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statsData.total_requests }}</div>
              <div class="stat-label">总申请数</div>
            </div>
          </t-card>
        </t-col>
        <t-col :span="4">
          <t-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statsData.pending_requests }}</div>
              <div class="stat-label">待审批</div>
            </div>
          </t-card>
        </t-col>
        <t-col :span="4">
          <t-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statsData.approved_requests }}</div>
              <div class="stat-label">已批准</div>
            </div>
          </t-card>
        </t-col>
        <t-col :span="4">
          <t-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statsData.approval_rate }}%</div>
              <div class="stat-label">批准率</div>
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
            :theme="getStatusTheme(row.status)"
            variant="light"
          >
            {{ getStatusText(row.status) }}
          </t-tag>
        </template>

        <template #op="slotProps">
          <t-space>
            <t-link theme="primary" @click="viewDetail(slotProps.row)">
              <t-icon name="view" />
              详情
            </t-link>
            <t-link
              theme="success"
              v-if="canApprove && slotProps.row.status === 'pending'"
              @click="handleApprove(slotProps.row, 'approved')"
            >
              <t-icon name="check" />
              批准
            </t-link>
            <t-link
              theme="danger"
              v-if="canApprove && slotProps.row.status === 'pending'"
              @click="handleApprove(slotProps.row, 'rejected')"
            >
              <t-icon name="close" />
              拒绝
            </t-link>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 详情对话框 -->
    <t-dialog
      v-model:visible="detailVisible"
      header="回溯详情"
      width="800px"
      :footer="false"
      :close-on-overlay-click="true"
    >
      <div v-if="currentDetail" class="detail-content">
        <t-descriptions :column="2" title="基本信息">
          <t-descriptions-item label="申请ID">
            {{ currentDetail.rollback_id }}
          </t-descriptions-item>
          <t-descriptions-item label="工作流ID">
            {{ currentDetail.workflow_id }}
          </t-descriptions-item>
          <t-descriptions-item label="目标表单ID">
            {{ currentDetail.target_form_id }}
          </t-descriptions-item>
          <t-descriptions-item label="申请人">
            {{ currentDetail.requester_name }}
          </t-descriptions-item>
          <t-descriptions-item label="申请时间">
            {{ formatDate(currentDetail.created_at) }}
          </t-descriptions-item>
          <t-descriptions-item label="审批状态">
            <t-tag :theme="getStatusTheme(currentDetail.status)" variant="light">
              {{ getStatusText(currentDetail.status) }}
            </t-tag>
          </t-descriptions-item>
          <t-descriptions-item label="审批人" v-if="currentDetail.approver_name">
            {{ currentDetail.approver_name }}
          </t-descriptions-item>
          <t-descriptions-item label="审批时间" v-if="currentDetail.approved_at">
            {{ formatDate(currentDetail.approved_at) }}
          </t-descriptions-item>
        </t-descriptions>

        <t-divider />

        <div class="request-content">
          <h4>申请原因</h4>
          <p>{{ currentDetail.reason }}</p>
        </div>

        <t-divider />

        <div class="support-file" v-if="currentDetail.support_file_url">
          <h4>支撑文件</h4>
          <t-link :href="currentDetail.support_file_url" target="_blank" theme="primary">
            <t-icon name="download" />
            下载支撑文件
          </t-link>
        </div>

        <t-divider v-if="currentDetail.support_file_url" />

        <div class="approval-comment" v-if="currentDetail.approval_comment">
          <h4>审批意见</h4>
          <p>{{ currentDetail.approval_comment }}</p>
        </div>

        <!-- 审批操作 -->
        <div class="approval-actions" v-if="canApprove && currentDetail.status === 'pending'">
          <t-divider />
          <h4>审批操作</h4>
          <t-space>
            <t-button theme="success" @click="handleApprove(currentDetail, 'approved')">
              <t-icon name="check" />
              批准申请
            </t-button>
            <t-button theme="danger" @click="handleApprove(currentDetail, 'rejected')">
              <t-icon name="close" />
              拒绝申请
            </t-button>
          </t-space>
        </div>
      </div>
    </t-dialog>

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
        <t-textarea
          v-model="approvalComment"
          placeholder="请输入审批意见（可选）"
          :maxlength="500"
          :autosize="{ minRows: 3, maxRows: 6 }"
        />
      </div>
    </t-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import Layout from '@/components/Layout.vue'
import {
  getRollbackHistory,
  getRollbackDetail,
  getRollbackStats,
  deleteRollback,
  adminDeleteRollback,
  batchDeleteRollbacks,
  approveRollback
} from '@/api/rollback.js'

/**
 * 回溯历史页面组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// 响应式数据
const loading = ref(false)
const searchValue = ref('')
const statusFilter = ref('')
const dateRange = ref([])
const tableData = ref([])
const statsData = ref(null)
const selectedRowKeys = ref([])
const detailVisible = ref(false)
const currentDetail = ref(null)
const currentUser = ref(null)

// 审批相关
const approvalDialogVisible = ref(false)
const approvalAction = ref('')
const approvalTarget = ref(null)
const approvalComment = ref('')

// 分页配置
const pagination = ref({
  defaultPageSize: 20,
  total: 0,
  defaultCurrent: 1,
  showJumper: true,
  showSizeChanger: true,
  pageSizeOptions: [5, 10, 20, 50]
})

// 表格列配置
const columns = computed(() => {
  const baseColumns = [
    {
      title: '申请ID',
      colKey: 'rollback_id',
      width: 100,
      ellipsis: true
    },
    {
      title: '工作流ID',
      colKey: 'workflow_id',
      width: 200,
      ellipsis: true
    },
    {
      title: '申请人',
      colKey: 'requester_name',
      width: 120
    },
    {
      title: '申请时间',
      colKey: 'created_at',
      width: 150,
      sorter: true
    },
    {
      title: '审批状态',
      colKey: 'status',
      width: 100,
      align: 'center'
    },
    {
      title: '审批人',
      colKey: 'approver_name',
      width: 120
    },
    {
      title: '操作',
      colKey: 'op',
      width: 200,
      fixed: 'right'
    }
  ]

  // 只有管理员才能看到选择列
  if (currentUser.value?.role_key === 'admin') {
    return [
      { colKey: 'row-select', type: 'multiple', width: 64, fixed: 'left' },
      ...baseColumns
    ]
  }

  return baseColumns
})

// 计算属性
const canDelete = computed(() => {
  return currentUser.value?.role_key === 'admin' || currentUser.value?.role_key === 'restorer'
})

const canApprove = computed(() => {
  return currentUser.value?.role_key === 'admin'
})

// 检查用户是否可以删除特定记录
const canDeleteRecord = (record) => {
  const userRole = currentUser.value?.role_key
  if (userRole === 'admin') {
    return true // 管理员可以删除任何记录
  }
  if (userRole === 'restorer') {
    // 修复专家只能删除自己的申请，且只能删除待审批状态的
    return record.requester_name === currentUser.value?.full_name && record.status === 'pending'
  }
  return false
}

const rowKey = 'rollback_id'

// 方法
const loadData = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      search: searchValue.value,
      status: statusFilter.value,
      date_range: dateRange.value?.length ? dateRange.value.join(',') : '',
      page: page,
      limit: pagination.value.defaultPageSize
    }

    const response = await getRollbackHistory(params)
    // 根据API文档，现在返回分页数据
    if (response && response.items) {
      tableData.value = response.items || []
      pagination.value.total = response.total || 0
    } else {
      // 兼容旧格式
      tableData.value = response || []
      pagination.value.total = response?.length || 0
    }
    
    // 数据加载完成后计算统计信息
    await loadStats()
  } catch (error) {

    MessagePlugin.error('加载数据失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    // 由于后端暂未实现统计接口，直接使用表格数据计算统计信息
    const totalRequests = tableData.value.length
    const approvedRequests = tableData.value.filter(item => item.status === 'approved').length
    const rejectedRequests = tableData.value.filter(item => item.status === 'rejected').length
    const processedRequests = approvedRequests + rejectedRequests
    
    // 批准率 = 已批准数量 / 已处理数量（已批准 + 已拒绝）
    const approvalRate = processedRequests > 0 ? Math.round((approvedRequests / processedRequests) * 100) : 0
    
    statsData.value = {
      total_requests: totalRequests,
      pending_requests: tableData.value.filter(item => item.status === 'pending').length,
      approved_requests: approvedRequests,
      approval_rate: approvalRate
    }
  } catch (error) {
    console.error('计算统计数据失败:', error)
    // 使用默认数据
    statsData.value = {
      total_requests: 0,
      pending_requests: 0,
      approved_requests: 0,
      approval_rate: 0
    }
  }
}

const handleSearch = () => {
  loadData(1)
}

const handleFilter = () => {
  loadData(1)
}

const handleDateRangeChange = () => {
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
}

const viewDetail = async (row) => {
  try {
    const response = await getRollbackDetail(row.rollback_id)
    currentDetail.value = response || row
    detailVisible.value = true
  } catch (error) {
    console.error('加载回溯详情失败:', error)
    // 如果详情接口失败，使用行数据作为详情
    currentDetail.value = row
    detailVisible.value = true
    MessagePlugin.warning('无法加载详细信息，显示基础信息')
  }
}


const handleApprove = (row, action) => {
  approvalTarget.value = row
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

    refreshData()
  } catch (error) {
    console.error('审批操作失败:', error)
    const actionText = approvalAction.value === 'approved' ? '批准' : '拒绝'
    MessagePlugin.error(`${actionText}失败: ${error.message || '未知错误'}`)
  }
}

const cancelApproval = () => {
  approvalDialogVisible.value = false
  approvalTarget.value = null
  approvalAction.value = ''
  approvalComment.value = ''
}

// 工具方法
const getStatusTheme = (status) => {
  switch (status) {
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    case 'pending': return 'warning'
    default: return 'default'
  }
}

const getStatusText = (status) => {
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

// 生命周期
onMounted(async () => {
  // 获取当前用户信息
  const user = localStorage.getItem('user') || localStorage.getItem('currentUser')
  if (user) {
    try {
      currentUser.value = JSON.parse(user)
    } catch (error) {
      console.error('解析用户信息失败:', error)
      currentUser.value = null
    }
  }

  // 等待DOM完全渲染后再加载数据
  await nextTick()
  
  // 加载数据（loadData内部会调用loadStats）
  loadData()
})
</script>

<style lang="less" scoped>
.rollback-history-container {
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

.detail-content {
  .request-content,
  .approval-comment,
  .support-file {
    h4 {
      font-size: 16px;
      font-weight: 600;
      color: var(--td-text-color-primary);
      margin: 16px 0 8px 0;
    }

    p {
      color: var(--td-text-color-secondary);
      line-height: 1.6;
      margin: 0;
    }
  }

  .approval-actions {
    h4 {
      font-size: 16px;
      font-weight: 600;
      color: var(--td-text-color-primary);
      margin: 16px 0 12px 0;
    }
  }
}

.approval-confirm-content {
  p {
    margin-bottom: 16px;
    color: var(--td-text-color-primary);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .rollback-history-container {
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

  .stats-section {
    .t-col {
      margin-bottom: 16px;
    }
  }
}
</style>

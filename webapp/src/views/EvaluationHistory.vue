<template>
  <Layout>
    <div class="evaluation-history-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">评估历史</h2>
      <p class="page-description">查看历史评估记录和评分详情</p>
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
          placeholder="搜索评估记录..."
          clearable
          style="width: 200px; margin-right: 8px;"
          @enter="handleSearch"
        >
          <template #suffix-icon>
            <t-icon name="search" @click="handleSearch" />
          </template>
        </t-input>



        <t-select
          v-model="scoreFilter"
          placeholder="评分范围"
          clearable
          style="width: 120px; margin-right: 8px;"
          @change="handleFilter"
        >
          <t-option value="excellent" label="优秀(80-100)" />
          <t-option value="good" label="良好(60-79)" />
          <t-option value="poor" label="较差(0-59)" />
        </t-select>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <t-row :gutter="16">
        <t-col :span="4">
          <t-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statsData?.total_evaluations || 0 }}</div>
              <div class="stat-label">总评估数</div>
            </div>
          </t-card>
        </t-col>
        <t-col :span="4">
          <t-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statsData?.average_score || 0 }}</div>
              <div class="stat-label">平均评分</div>
            </div>
          </t-card>
        </t-col>
        <t-col :span="4">
          <t-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statsData?.excellent_rate || 0 }}%</div>
              <div class="stat-label">优秀率</div>
            </div>
          </t-card>
        </t-col>
        <t-col :span="4">
          <t-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statsData?.monthly_evaluations || 0 }}</div>
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
        <template #score="{ row }">
          <t-tag
            :theme="getScoreTheme(row.score)"
            variant="light"
          >
            {{ row.score }}分
          </t-tag>
        </template>



        <template #op="slotProps">
          <t-space>
            <t-link theme="primary" @click="viewDetail(slotProps.row)">
              <t-icon name="view" />
              详情
            </t-link>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 详情对话框 -->
    <t-dialog
      v-model:visible="detailVisible"
      header="评估详情"
      width="800px"
      :footer="false"
      :close-on-overlay-click="true"
    >
      <div v-if="currentDetail" class="detail-content">
        <t-descriptions :column="2" title="基本信息">
          <t-descriptions-item label="评估ID">
            {{ currentDetail.evaluate_id }}
          </t-descriptions-item>
          <t-descriptions-item label="工作流ID">
            {{ currentDetail.workflow_id }}
          </t-descriptions-item>
          <t-descriptions-item label="评估专家">
            {{ currentDetail.evaluator_name }}
          </t-descriptions-item>
          <t-descriptions-item label="评估时间">
            {{ formatDate(currentDetail.created_at) }}
          </t-descriptions-item>
          <t-descriptions-item label="评估评分">
            <t-tag :theme="getScoreTheme(currentDetail.score)" variant="light">
              {{ currentDetail.score }}分
            </t-tag>
          </t-descriptions-item>
          <t-descriptions-item label="更新时间" v-if="currentDetail.updated_at">
            {{ formatDate(currentDetail.updated_at) }}
          </t-descriptions-item>
        </t-descriptions>

        <t-divider />

        <div class="evaluation-comment" v-if="currentDetail.comment">
          <h4>评估意见</h4>
          <p>{{ currentDetail.comment }}</p>
        </div>

        <t-divider v-if="currentDetail.evaluation_file" />

        <div class="evaluation-file" v-if="currentDetail.evaluation_file">
          <h4>评估文件</h4>
          <t-link :href="currentDetail.evaluation_file" target="_blank" theme="primary">
            <t-icon name="download" />
            下载评估文件
          </t-link>
        </div>
      </div>
    </t-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import Layout from '@/components/Layout.vue'
import {
  getEvaluationHistory,
  getEvaluationDetail,
  deleteEvaluation,
  batchDeleteEvaluations
} from '@/api/history.js'
import { getEvaluationStats } from '@/api/evaluation.js'

/**
 * 评估历史页面组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// 响应式数据
const loading = ref(false)
const searchValue = ref('')

const scoreFilter = ref('')
const tableData = ref([])
const statsData = ref(null)
const selectedRowKeys = ref([])
const detailVisible = ref(false)
const currentDetail = ref(null)
const currentUser = ref(null)

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
    title: '评估ID',
    colKey: 'evaluate_id',
    width: 100,
    align: 'center'
  },
  {
    title: '工作流ID',
    colKey: 'workflow_id',
    width: 200,
    ellipsis: true
  },
  {
    title: '评估专家',
    colKey: 'evaluator_name',
    width: 120
  },
  {
    title: '评估评分',
    colKey: 'score',
    width: 100,
    align: 'center'
  },
  {
    title: '评估时间',
    colKey: 'created_at',
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

// 计算属性
const canDelete = computed(() => {
  return currentUser.value?.role_key === 'admin'
})

const rowKey = 'evaluate_id'

// 方法
const loadData = async (page = 1) => {
  loading.value = true
  try {
    const response = await getEvaluationHistory()
    let allEvaluations = response || []
    
    // 保存原始数据用于统计计算
    updateStatsFromData(allEvaluations)
    
    // 前端筛选逻辑
    let filteredEvaluations = allEvaluations
    if (searchValue.value) {
      const searchTerm = searchValue.value.toLowerCase()
      filteredEvaluations = filteredEvaluations.filter(evaluation => 
        evaluation.evaluate_id.toString().includes(searchTerm) ||
        evaluation.workflow_id.toString().toLowerCase().includes(searchTerm) ||
        (evaluation.comment && evaluation.comment.toLowerCase().includes(searchTerm)) ||
        evaluation.evaluator_name.toLowerCase().includes(searchTerm)
      )
    }
    
    // 评分筛选
    if (scoreFilter.value) {
      filteredEvaluations = filteredEvaluations.filter(evaluation => {
        const score = evaluation.score
        switch (scoreFilter.value) {
          case 'excellent':
            return score >= 80
          case 'good':
            return score >= 60 && score < 80
          case 'poor':
            return score < 60
          default:
            return true
        }
      })
    }
    
    // 分页处理
    const startIndex = (page - 1) * pagination.value.defaultPageSize
    const endIndex = startIndex + pagination.value.defaultPageSize
    tableData.value = filteredEvaluations.slice(startIndex, endIndex)
    pagination.value.total = filteredEvaluations.length
  } catch (error) {
    console.error('加载评估历史失败:', error)
    MessagePlugin.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  // 统计数据现在在loadData中计算，这里只需要确保有默认值
  if (!statsData.value) {
    statsData.value = {
      total_evaluations: 0,
      average_score: 0,
      excellent_rate: 0,
      monthly_evaluations: 0
    }
  }
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

// 在数据变化时更新统计数据
const updateStatsFromData = (evaluations) => {
  
  const totalEvaluations = evaluations.length
  const averageScore = totalEvaluations > 0 
    ? (evaluations.reduce((sum, evaluation) => sum + evaluation.score, 0) / totalEvaluations).toFixed(1)
    : 0
  
  // 计算优秀率（80分以上）
  const excellentCount = evaluations.filter(evaluation => evaluation.score >= 80).length
  const excellentRate = totalEvaluations > 0 
    ? ((excellentCount / totalEvaluations) * 100).toFixed(1)
    : 0
  
  // 计算本月评估数
  const currentMonth = new Date().getMonth()
  const currentYear = new Date().getFullYear()
  const monthlyEvaluations = evaluations.filter(evaluation => {
    const evalDate = new Date(evaluation.created_at)
    return evalDate.getMonth() === currentMonth && evalDate.getFullYear() === currentYear
  }).length
  
  const newStatsData = {
    total_evaluations: totalEvaluations,
    average_score: averageScore,
    excellent_rate: excellentRate,
    monthly_evaluations: monthlyEvaluations
  }
  
  statsData.value = newStatsData
}

const viewDetail = async (row) => {
  try {
    const response = await getEvaluationDetail(row.evaluate_id)
    currentDetail.value = response
    detailVisible.value = true
  } catch (error) {
    console.error('加载评估详情失败:', error)
    MessagePlugin.error('加载详情失败')
  }
}


// 工具方法
const getScoreTheme = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'warning'
  if (score >= 60) return 'default'
  return 'danger'
}



const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  // 获取当前用户信息
  const user = localStorage.getItem('currentUser')
  if (user) {
    currentUser.value = JSON.parse(user)
  }

  // 初始化统计数据
  statsData.value = {
    total_evaluations: 0,
    average_score: 0,
    excellent_rate: 0,
    monthly_evaluations: 0
  }

  // 加载数据（统计数据会在loadData中计算）
  loadData()
})
</script>

<style lang="less" scoped>
.evaluation-history-container {
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
  .evaluation-comment,
  .evaluation-file {
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
}

// 响应式设计
@media (max-width: 768px) {
  .evaluation-history-container {
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

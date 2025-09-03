<template>
  <Layout>
    <!-- 仪表板页面 -->
    <div class="page-content">
      <!-- 统计卡片区域 -->
      <t-row :gutter="[16, 16]" class="stats-row">
        <t-col v-for="(stat, index) in statsList" :key="stat.label" :xs="6" :xl="3">
          <t-card class="dashboard-item" :class="{ 'dashboard-item--main-color': index === 0 }">
            <div class="dashboard-item-top">
              <div class="stat-number">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
            <div class="dashboard-item-block">
              <Trend :type="stat.trend > 0 ? 'up' : 'down'" :describe="`${Math.abs(stat.trend)}%`" />
            </div>
            <div class="dashboard-item-left">
              <div class="stat-icon">
                <t-icon :name="stat.icon" />
              </div>
              <div v-if="stat.chart" :id="stat.chart" class="mini-chart"></div>
            </div>
          </t-card>
        </t-col>
      </t-row>

      <!-- 图表区域 -->
      <t-row :gutter="[16, 16]" class="charts-row">
        <t-col :xs="12" :xl="8">
          <t-card class="dashboard-chart-card">
            <template #header>
              <div class="chart-header">
                <h3 class="chart-title">工作流趋势</h3>
                <t-date-range-picker
                  v-model="dateRange"
                  @change="handleDateRangeChange"
                  :presets="datePresets"
                  size="small"
                />
              </div>
            </template>
            <div id="trendChart" class="chart-container"></div>
          </t-card>
        </t-col>
        
        <t-col :xs="12" :xl="4">
          <t-card class="dashboard-chart-card">
            <template #header>
              <h3 class="chart-title">评分分布</h3>
            </template>
            <div id="scoreChart" class="chart-container"></div>
          </t-card>
        </t-col>
      </t-row>

      <!-- 最近活动 -->
      <div class="recent-activities-section">
        <t-card class="recent-activities-card">
          <template #header>
            <h3 class="chart-title">最近活动</h3>
          </template>
          <div v-if="recentActivities.length === 0" class="no-data">
            <t-icon name="inbox" size="48px" />
            <p>暂无活动记录</p>
          </div>
          <div v-else class="activities-list">
            <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
              <div class="activity-icon" :class="`activity-icon-${getActivityColor(activity.action)}`">
                {{ getActivityIcon(activity.action) }}
              </div>
              <div class="activity-content">
                <div class="activity-main">
                  <strong>{{ activity.operator }}</strong>
                  <span class="activity-action">{{ getActivityText(activity.action) }}</span>
                  <span v-if="activity.workflow_title" class="activity-target">「{{ activity.workflow_title }}」</span>
                </div>
                <div class="activity-time">{{ activity.time }}</div>
                <div v-if="activity.comment" class="activity-comment">{{ activity.comment }}</div>
              </div>
            </div>
          </div>
        </t-card>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import * as echarts from 'echarts'
import { getDashboardData } from '@/api/dashboard'
import Trend from '@/components/Trend.vue'
import Layout from '@/components/Layout.vue'

/**
 * Dashboard页面组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// 响应式数据
const dashboardData = ref(null)
const loading = ref(false)

// 图表实例
let trendChart = null
let scoreChart = null
let progressChart = null
let moneyChart = null
let refundChart = null

// 日期范围
const dateRange = ref(['2024-01-01', '2024-12-31'])
const datePresets = {
  '最近7天': ['2024-01-01', '2024-01-07'],
  '最近30天': ['2024-01-01', '2024-01-30'],
  '最近3个月': ['2024-01-01', '2024-03-31']
}



// 获取活动文本
const getActivityText = (action) => {
  const actionMap = {
    'submit': '提交表单',
    'rollback': '回溯操作',
    'finalize': '设为最终方案',
    'revoke': '撤销操作',
    'evaluate': '评估完成',
    'approve': '审批通过',
    'reject': '审批拒绝'
  }
  return actionMap[action] || action
}

// 获取活动图标
const getActivityIcon = (action) => {
  const iconMap = {
    'submit': '📝',
    'rollback': '⏮️',
    'finalize': '🎯',
    'revoke': '❌',
    'evaluate': '⭐',
    'approve': '✅',
    'reject': '❌'
  }
  return iconMap[action] || '📋'
}

// 获取活动颜色
const getActivityColor = (action) => {
  const colorMap = {
    'submit': 'primary',
    'rollback': 'warning',
    'finalize': 'success',
    'revoke': 'danger',
    'evaluate': 'info',
    'approve': 'success',
    'reject': 'danger'
  }
  return colorMap[action] || 'secondary'
}

// 检查登录状态
const checkAuth = () => {
  const token = localStorage.getItem('authToken')
  const user = localStorage.getItem('currentUser')
  
  if (!token || !user) {
    MessagePlugin.error('请先登录')
    setTimeout(() => {
      window.location.href = '/login'
    }, 1000)
    return false
  }
  return true
}

// 统计卡片数据
const statsList = computed(() => {
  if (!dashboardData.value) return []
  
  return [
    {
      label: '总工作流',
      value: dashboardData.value.total_workflows || 0,
      icon: 'chart',
      trend: dashboardData.value.workflow_trend || 0,
      chart: 'moneyContainer'
    },
    {
      label: '进行中',
      value: dashboardData.value.running_workflows || 0,
      icon: 'time',
      trend: dashboardData.value.running_trend || 0
    },
    {
      label: '已完成',
      value: dashboardData.value.finished_workflows || 0,
      icon: 'check-circle',
      trend: dashboardData.value.finished_trend || 0,
      chart: 'refundContainer'
    },
    {
      label: '待评估',
      value: dashboardData.value.pending_evaluations || 0,
      icon: 'file',
      trend: dashboardData.value.evaluation_trend || 0
    }
  ]
})

// 最近活动数据
const recentActivities = computed(() => {
  return dashboardData.value?.recent_activities || []
})

// 加载仪表板数据
const loadDashboardData = async () => {
  try {
    loading.value = true
    const response = await getDashboardData()
    dashboardData.value = response.data || response
    
    // 渲染图表
    nextTick(() => {
      renderCharts()
    })
  } catch (error) {
    MessagePlugin.error('加载仪表板数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderCharts = () => {
  // 延迟渲染，确保DOM元素已准备好
  setTimeout(() => {
    renderTrendChart()
    renderScoreChart()
    renderMoneyChart()
    renderRefundChart()
  }, 100)
}

// 渲染趋势图
const renderTrendChart = () => {
  const container = document.getElementById('trendChart')
  if (!container) return
  
  trendChart = echarts.init(container)
  
  // 使用真实数据
  const trendData = dashboardData.value?.workflow_trend_data
  if (!trendData) {
    // 如果没有数据，显示空状态
    const option = {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'middle',
        textStyle: {
          color: '#999',
          fontSize: 14
        }
      }
    }
    trendChart.setOption(option)
    return
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        return `${data.name}: ${data.value}个工作流`
      }
    },
    xAxis: {
      type: 'category',
      data: trendData.labels || ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#666'
      }
    },
    series: [{
      data: trendData.values || [0, 0, 0, 0, 0, 0, 0],
      type: 'line',
      smooth: true,
      itemStyle: {
        color: '#0052d9'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(0, 82, 217, 0.3)'
          }, {
            offset: 1, color: 'rgba(0, 82, 217, 0.05)'
          }]
        }
      }
    }]
  }
  
  trendChart.setOption(option)
}

// 渲染评分分布图
const renderScoreChart = () => {
  const container = document.getElementById('scoreChart')
  if (!container) return
  
  scoreChart = echarts.init(container)
  
  // 使用真实数据
  const scoreDistribution = dashboardData.value?.score_distribution
  if (!scoreDistribution) {
    // 如果没有数据，显示空状态
    const option = {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'middle',
        textStyle: {
          color: '#999',
          fontSize: 14
        }
      }
    }
    scoreChart.setOption(option)
    return
  }
  
  // 将评分分布数据转换为饼图格式
  const pieData = Object.entries(scoreDistribution).map(([range, count]) => {
    let name = ''
    let color = '#0052d9'
    
    // 根据评分范围设置名称和颜色
    if (range === '0-6') {
      name = '较差(0-60分)'
      color = '#d54941'
    } else if (range === '6-7') {
      name = '一般(60-70分)'
      color = '#ed7b2f'
    } else if (range === '7-8') {
      name = '良好(70-80分)'
      color = '#0052d9'
    } else if (range === '8-9') {
      name = '优秀(80-90分)'
      color = '#00a870'
    } else if (range === '9-10') {
      name = '卓越(90-100分)'
      color = '#00a870'
    } else {
      name = `${range}分`
    }
    
    return {
      value: count,
      name: name,
      itemStyle: {
        color: color
      }
    }
  })
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        const total = pieData.reduce((sum, item) => sum + item.value, 0)
        const percentage = total > 0 ? ((params.value / total) * 100).toFixed(1) : 0
        return `${params.name}: ${params.value}个 (${percentage}%)`
      }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: {
        fontSize: 12
      }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      data: pieData,
      itemStyle: {
        borderRadius: 5,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  scoreChart.setOption(option)
}

// 渲染收入图表
const renderMoneyChart = () => {
  const container = document.getElementById('moneyContainer')
  if (!container) return
  
  moneyChart = echarts.init(container)
  
  const option = {
    grid: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0
    },
    xAxis: {
      type: 'category',
      show: false
    },
    yAxis: {
      type: 'value',
      show: false
    },
    series: [{
      data: [820, 932, 901, 934, 1290, 1330, 1320],
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: {
        color: '#0052d9',
        width: 2
      }
    }]
  }
  
  moneyChart.setOption(option)
}

// 渲染退款图表
const renderRefundChart = () => {
  const container = document.getElementById('refundContainer')
  if (!container) return
  
  refundChart = echarts.init(container)
  
  const option = {
    grid: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0
    },
    xAxis: {
      type: 'category',
      show: false
    },
    yAxis: {
      type: 'value',
      show: false
    },
    series: [{
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'bar',
      itemStyle: {
        color: '#00a870'
      }
    }]
  }
  
  refundChart.setOption(option)
}

// 日期范围变化处理
const handleDateRangeChange = (value) => {
  // 这里可以根据新的日期范围重新加载数据
}

// 窗口大小变化时重新渲染图表
const handleResize = () => {
  if (trendChart) {
    trendChart.resize()
  }
  if (scoreChart) {
    scoreChart.resize()
  }
  if (moneyChart) {
    moneyChart.resize()
  }
  if (refundChart) {
    refundChart.resize()
  }
}

// 组件挂载时初始化
onMounted(() => {
  if (checkAuth()) {
    loadDashboardData()
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  
  // 销毁图表实例
  if (trendChart) {
    trendChart.dispose()
  }
  if (scoreChart) {
    scoreChart.dispose()
  }
  if (moneyChart) {
    moneyChart.dispose()
  }
  if (refundChart) {
    refundChart.dispose()
  }
})
</script>

<style scoped>
/* Dashboard页面样式 */
.page-content {
  padding: 10px;
  height: 90%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow: hidden;
}

.stats-row {
  flex-shrink: 0;
  margin-bottom: 0;
}

.charts-row {
  flex-shrink: 0;
  height: 300px;
  margin-bottom: 0;
}

.recent-activities-section {
/* 上边距 */
  margin: 10px 0 0 0;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.dashboard-item {
  padding: 20px 24px;
  height: 100px;
  position: relative;
  overflow: hidden;
}

.dashboard-item :deep(.t-card__title) {
  font-size: 14px;
  font-weight: 500;
  color: #86909c;
  margin-bottom: 8px;
}

.dashboard-item-top {
  margin-bottom: 12px;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #86909c;
}

.dashboard-item-block {
  color: #86909c;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dashboard-item-left {
  position: absolute;
  right: 24px;
  top: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: #f2f3f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0052d9;
  font-size: 20px;
}

.mini-chart {
  width: 60px;
  height: 30px;
}

.dashboard-item--main-color {
  background: #0052d9;
  color: #fff;
}

.dashboard-item--main-color .stat-number,
.dashboard-item--main-color .stat-label {
  color: #fff;
}

.dashboard-item--main-color .stat-icon {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.dashboard-chart-card {
  padding: 5px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.recent-activities-card {
  padding: 5px;
  height: 100%;
  display: flex;
  flex-direction: column;
  /* overflow: hidden; */
}

.dashboard-chart-card :deep(.t-card__title),
.recent-activities-card :deep(.t-card__title) {
  font-size: 18px;
  font-weight: 400;
  color: #1f2937;
}

.dashboard-chart-card :deep(.t-card__body) {
  margin-top: 16px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.recent-activities-card :deep(.t-card__body) {
  margin-top: 16px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-size: 18px;
  font-weight: 400;
  color: #1f2937;
  margin: 0;
}

.chart-container {
  flex: 1;
  min-height: 200px;
  max-height: 280px;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #86909c;
}

.page-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #86909c;
}

.activities-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.activity-icon-primary {
  background: #e6f7ff;
  color: #0052d9;
}

.activity-icon-success {
  background: #f6ffed;
  color: #00a870;
}

.activity-icon-warning {
  background: #fffbe6;
  color: #ed7b2f;
}

.activity-icon-danger {
  background: #fff2f0;
  color: #d54941;
}

.activity-icon-info {
  background: #f0f5ff;
  color: #0052d9;
}

.activity-icon-secondary {
  background: #f5f5f5;
  color: #86909c;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-main {
  margin-bottom: 4px;
  line-height: 1.4;
}

.activity-action {
  color: #1f2937;
  font-weight: 500;
}

.activity-target {
  color: #0052d9;
  font-weight: 500;
}

.activity-time {
  font-size: 12px;
  color: #86909c;
  margin-bottom: 4px;
}

.activity-comment {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-content {
    padding: 5px;
    gap: 4px;
  }

  .charts-row {
    height: 280px;
  }

  .dashboard-item {
    padding: 16px 20px;
    height: 90px;
  }

  .dashboard-chart-card {
    padding: 12px;
  }

  .recent-activities-card {
    padding: 12px;
  }

  .chart-container {
    min-height: 180px;
    max-height: 240px;
  }
}

@media (max-width: 480px) {
  .page-content {
    padding: 8px;
    gap: 8px;
  }

  .charts-row {
    height: 240px;
  }

  .dashboard-item {
    padding: 12px 16px;
    height: 80px;
  }

  .dashboard-chart-card {
    padding: 8px;
  }

  .recent-activities-card {
    padding: 8px;
  }

  .chart-container {
    min-height: 160px;
    max-height: 200px;
  }
}
</style>
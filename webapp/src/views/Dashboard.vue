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

      <!-- 甘特图区域 -->
      <div class="gantt-row">
        <t-card class="gantt-card">
            <template #header>
              <div class="card-header">
                <h3>任务进度甘特图</h3>
              </div>
            </template>
            <!-- 数据统计信息 -->
            <div v-if="ganttSeries.length > 0" style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 6px; font-size: 14px; color: #666;">
              <span>共 {{ ganttSeries[0]?.data?.length || 0 }} 个任务</span>
            </div>
            
            <!-- 甘特图 -->
            <div v-if="ganttSeries.length > 0" class="gantt-chart-container">
              <apexchart
                type="rangeBar"
                height="100%"
                width="100%"
                :options="ganttOptions"
                :series="ganttSeries"
              />
            </div>
            <!-- 没有数据时显示提示信息 -->
            <div v-else class="gantt-no-data">
              <div class="no-data-icon">
                <t-icon name="chart" size="64px" />
              </div>
              <h4>暂无任务数据</h4>
              <p>当前没有可显示的任务进度信息</p>
              <p class="text-secondary">请先创建修复任务或检查数据连接</p>
            </div>
          </t-card>
      </div>

      <!-- 最近活动 -->
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, nextTick, shallowRef } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import * as echarts from 'echarts'
import { getDashboardData } from '@/api/dashboard'
import Trend from '@/components/Trend.vue'
import Layout from '@/components/Layout.vue'
import VueApexCharts from 'vue3-apexcharts'

// ====== 甘特图（轻量展示）最小脚本，直接写进仪表盘页面 ======
const ganttSeries = shallowRef([])
const ganttOptions = shallowRef({
  chart: { 
    type: 'rangeBar', 
    toolbar: { show: false }, 
    height: '100%',
    width: '100%',
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800
    },
    parentHeightOffset: 0,
    zoom: {
      enabled: false
    },
    pan: {
      enabled: false
    }
  },
  plotOptions: { 
    bar: { 
      horizontal: true, 
      rangeBarGroupRows: true,
      barHeight: '70%',
      borderRadius: 4,
      distributed: true
    } 
  },
  xaxis: { 
    type: 'datetime',
    labels: {
      format: 'yyyy/MM/dd',
      style: {
        fontSize: '11px',
        colors: '#1f2937',
        fontWeight: '500'
      },
      rotate: 0,
      trim: false,
      hideOverlappingLabels: true,
      datetimeUTC: false
    },
    axisBorder: {
      show: true,
      color: '#e0e0e0',
      strokeWidth: 1
    },
    axisTicks: {
      show: true,
      color: '#e0e0e0',
      height: 6
    },
    tickAmount: 'dataPoints',
    min: undefined,
    max: undefined
  },
  yaxis: {
    labels: {
      style: {
        fontSize: '12px',
        fontWeight: '500',
        colors: '#1f2937'
      },
      maxWidth: 250,
      trim: false,
      offsetX: 0,
      formatter: function(value) {
        // 确保长标题能够完整显示，如果太长则截断
        if (value && value.length > 20) {
          return value.substring(0, 20) + '...'
        }
        return value
      }
    },
    axisBorder: {
      show: true,
      color: '#e0e0e0'
    }
  },
  dataLabels: {
    enabled: true,
    formatter: function(val, opts) {
      const data = opts.w.config.series[opts.seriesIndex].data[opts.dataPointIndex]
      return data.meta?.progress ? `${data.meta.progress}%` : ''
    },
    style: {
      fontSize: '10px',
      fontWeight: 'bold'
    }
  },
  tooltip: {
    enabled: true,
    custom: function({series, seriesIndex, dataPointIndex, w}) {
      const data = w.config.series[seriesIndex].data[dataPointIndex]
      const startDate = new Date(data.y[0]).toLocaleDateString()
      const endDate = new Date(data.y[1]).toLocaleDateString()
      const progress = data.meta?.progress || 0
      const assignee = data.meta?.assignee || '未分配'
      const status = data.meta?.status || '未知'
      
      // 获取实际的任务条颜色
      let color = data.fillColor
      
      // 如果fillColor不存在，尝试从meta中获取colorIndex
      if (!color && data.meta?.colorIndex !== undefined) {
        color = w.config.colors[data.meta.colorIndex]
      }
      
      // 如果还是没有颜色，根据标题重新计算
      if (!color) {
        const colorIndex = getTaskColorIndex(data.x, dataPointIndex)
        color = w.config.colors[colorIndex]
      }
      
      // 最后的备用颜色
      if (!color) {
        color = '#0052d9'
      }
      
      return `
        <div style="padding: 12px; background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-left: 4px solid ${color};">
          <div style="font-weight: bold; margin-bottom: 8px; color: #1f2937;">${data.x}</div>
          <div style="margin-bottom: 4px;"><strong>开始:</strong> ${startDate}</div>
          <div style="margin-bottom: 4px;"><strong>结束:</strong> ${endDate}</div>
          <div style="margin-bottom: 4px;"><strong>进度:</strong> ${progress}%</div>
          <div style="margin-bottom: 4px;"><strong>负责人:</strong> ${assignee}</div>
          <div style="margin-bottom: 4px;"><strong>状态:</strong> <span style="color: ${color}; font-weight: 500;">${status}</span></div>
          <div style="font-size: 11px; color: #666; margin-top: 6px;">标题颜色: <span style="display: inline-block; width: 12px; height: 12px; background: ${color}; border-radius: 2px; vertical-align: middle; margin-left: 4px;"></span></div>
        </div>
      `
    }
  },
  grid: {
    show: true,
    borderColor: '#e0e0e0',
    strokeDashArray: 3,
    padding: {
      left: 30,
      right: 15,
      top: 15,
      bottom: 25
    }
  },
  colors: [
    '#0052d9', // 主蓝色 - 专业
    '#00a870', // 绿色 - 成功/进行中
    '#ed7b2f', // 橙色 - 警告/待处理
    '#d54941', // 红色 - 紧急/已完成
    '#722ed1', // 紫色 - 特殊任务
    '#13c2c2', // 青色 - 新任务
    '#fa8c16', // 金橙色 - 高优先级
    '#52c41a', // 亮绿色 - 低优先级
    '#1890ff', // 天蓝色 - 默认
    '#f5222d'  // 深红色 - 取消
  ],
  legend: {
    show: false
  },
  responsive: [{
    breakpoint: 768,
    options: {
      chart: {
        width: '100%',
        zoom: {
          enabled: false
        },
        pan: {
          enabled: false
        }
      },
      yaxis: {
        labels: {
          maxWidth: 150,
          formatter: function(value) {
            if (value && value.length > 12) {
              return value.substring(0, 12) + '...'
            }
            return value
          }
        }
      },
      grid: {
        padding: {
          left: 25,
          right: 10,
          top: 10,
          bottom: 20
        }
      },
      xaxis: {
        labels: {
          format: 'yyyy/MM/dd',
          style: {
            fontSize: '10px'
          }
        }
      }
    }
  }, {
    breakpoint: 480,
    options: {
      chart: {
        width: '100%',
        zoom: {
          enabled: false
        },
        pan: {
          enabled: false
        }
      },
      yaxis: {
        labels: {
          maxWidth: 120,
          formatter: function(value) {
            if (value && value.length > 10) {
              return value.substring(0, 10) + '...'
            }
            return value
          }
        }
      },
      grid: {
        padding: {
          left: 20,
          right: 5,
          top: 5,
          bottom: 15
        }
      },
      xaxis: {
        labels: {
          format: 'yyyy/MM/dd',
          style: {
            fontSize: '9px'
          },
          rotate: -45
        }
      }
    }
  }]
})

// 根据任务标题获取颜色索引
function getTaskColorIndex(taskTitle, index) {
  // 基于任务标题的哈希值来分配颜色，确保相同标题的任务颜色一致
  let hash = 0
  if (taskTitle) {
    // 使用更复杂的哈希算法，确保更好的颜色分布
    for (let i = 0; i < taskTitle.length; i++) {
      const char = taskTitle.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // 转换为32位整数
    }
    
    // 添加标题长度作为额外的哈希因子
    hash = hash + taskTitle.length * 31
  }
  
  // 使用哈希值的绝对值来获取颜色索引
  const colorIndex = Math.abs(hash) % ganttOptions.value.colors.length
  return colorIndex
}

async function loadGantt() {
  try {
    const res = await fetch('/api/gantt/tasks')
    if (!res.ok) throw new Error('API请求失败')
    const tasks = await res.json()
    
    // 处理数据，确保时间格式正确
    const processedData = (tasks || []).map((t, index) => {
      const startTime = new Date(t.start).getTime()
      const endTime = new Date(t.end).getTime()
      
      // 确保时间范围有效
      if (isNaN(startTime) || isNaN(endTime) || startTime >= endTime) {
        return null
      }
      
      // 根据任务标题分配颜色
      const colorIndex = getTaskColorIndex(t.name, index)
      
      return {
        x: t.name,
        y: [startTime, endTime],
        fillColor: ganttOptions.value.colors[colorIndex],
        meta: { 
          progress: t.progress ?? 0, 
          assignee: t.assignee, 
          status: t.status,
          workflow_id: t.workflow_id,
          current_step: t.current_step,
          total_forms: t.total_forms,
          colorIndex: colorIndex
        }
      }
    }).filter(item => item !== null) // 过滤掉无效数据
    
    // 更新甘特图数据
    ganttSeries.value = [{
      name: '任务',
      data: processedData
    }]
    
    // 动态计算时间范围
    if (processedData.length > 0) {
      const allTimes = processedData.flatMap(d => d.y)
      const minTime = Math.min(...allTimes)
      const maxTime = Math.max(...allTimes)
      
      // 确保时间范围有效
      if (minTime && maxTime && minTime < maxTime) {
        // 添加一些边距
        const timeRange = maxTime - minTime
        const margin = Math.max(timeRange * 0.1, 24 * 60 * 60 * 1000) // 至少1天的边距
        
        // 更新X轴范围
        ganttOptions.value.xaxis.min = minTime - margin
        ganttOptions.value.xaxis.max = maxTime + margin
        
        // 根据时间范围调整显示格式
        const daysDiff = (maxTime - minTime) / (1000 * 60 * 60 * 24)
        if (daysDiff <= 7) {
          // 一周内显示具体日期
          ganttOptions.value.xaxis.labels.format = 'yyyy/MM/dd'
        } else if (daysDiff <= 30) {
          // 一个月内显示年/月/日
          ganttOptions.value.xaxis.labels.format = 'yyyy/MM/dd'
        } else if (daysDiff <= 365) {
          // 一年内显示年/月
          ganttOptions.value.xaxis.labels.format = 'yyyy/MM'
        } else {
          // 更长时间显示年/月
          ganttOptions.value.xaxis.labels.format = 'yyyy/MM'
        }
      } else {
        // 如果时间范围无效，重置为默认值
        ganttOptions.value.xaxis.min = undefined
        ganttOptions.value.xaxis.max = undefined
      }
    }
  } catch (error) {
    console.error('加载甘特图数据失败:', error)
    MessagePlugin.error('加载甘特图失败')
  }
}

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
    backgroundColor: 'transparent',
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '10%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e6e8eb',
      borderWidth: 1,
      textStyle: {
        color: '#1f2937',
        fontSize: 13
      },
      padding: [12, 16],
      extraCssText: 'box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12); border-radius: 8px;',
      formatter: function(params) {
        const data = params[0]
        return `<div style="font-weight: 600; margin-bottom: 4px;">${data.name}</div>
                <div style="color: #0052d9;">📊 ${data.value} 个工作流</div>`
      }
    },
    xAxis: {
      type: 'category',
      data: trendData.labels || ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: {
        lineStyle: {
          color: '#e6e8eb',
          width: 1
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#86909c',
        fontSize: 12,
        fontWeight: 500,
        margin: 12
      },
      splitLine: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#86909c',
        fontSize: 12,
        fontWeight: 500
      },
      splitLine: {
        lineStyle: {
          color: '#f0f1f5',
          width: 1,
          type: 'dashed'
        }
      }
    },
    series: [{
      data: trendData.values || [0, 0, 0, 0, 0, 0, 0],
      type: 'line',
      smooth: true,
      smoothMonotone: 'x',
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [{
            offset: 0, color: '#667eea'
          }, {
            offset: 0.5, color: '#0052d9'
          }, {
            offset: 1, color: '#764ba2'
          }]
        },
        width: 3,
        shadowColor: 'rgba(0, 82, 217, 0.3)',
        shadowBlur: 8,
        shadowOffsetY: 2
      },
      itemStyle: {
        color: '#0052d9',
        borderColor: '#ffffff',
        borderWidth: 3,
        shadowColor: 'rgba(0, 82, 217, 0.4)',
        shadowBlur: 10
      },
      emphasis: {
        itemStyle: {
          color: '#0052d9',
          borderColor: '#ffffff',
          borderWidth: 4,
          shadowColor: 'rgba(0, 82, 217, 0.6)',
          shadowBlur: 15,
          scale: 1.2
        }
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(102, 126, 234, 0.25)'
          }, {
            offset: 0.3, color: 'rgba(0, 82, 217, 0.15)'
          }, {
            offset: 0.7, color: 'rgba(118, 75, 162, 0.08)'
          }, {
            offset: 1, color: 'rgba(118, 75, 162, 0.02)'
          }]
        },
        shadowColor: 'rgba(0, 82, 217, 0.1)',
        shadowBlur: 20
      }
    }],
    animationDuration: 1500,
    animationEasing: 'cubicOut'
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

// 重新计算甘特图时间范围
const recalculateGanttTimeRange = () => {
  if (ganttSeries.value.length > 0 && ganttSeries.value[0].data.length > 0) {
    const processedData = ganttSeries.value[0].data
    const allTimes = processedData.flatMap(d => d.y)
    const minTime = Math.min(...allTimes)
    const maxTime = Math.max(...allTimes)
    
    if (minTime && maxTime && minTime < maxTime) {
      const timeRange = maxTime - minTime
      const margin = Math.max(timeRange * 0.1, 24 * 60 * 60 * 1000)
      
      ganttOptions.value.xaxis.min = minTime - margin
      ganttOptions.value.xaxis.max = maxTime + margin
    }
  }
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
  
  // 甘特图会自动响应容器大小变化，但我们可以触发重新渲染
  if (ganttSeries.value.length > 0) {
    // 重新计算时间范围
    recalculateGanttTimeRange()
    // 触发甘特图重新渲染
    nextTick(() => {
      // ApexCharts会自动处理容器大小变化
    })
  }
}

// 组件挂载时初始化
onMounted(() => {
  if (checkAuth()) {
    loadDashboardData()
  }
  
  // 加载甘特图数据
  loadGantt()
  
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
  height: 95vh;
  display: flex;
  flex-direction: column;
  gap: 10px;
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

.gantt-row {
  flex: 1;
  margin: 0;
  padding: 0;
  min-height: 0;
  width: 100%;
}

.gantt-card {
  height: 100%;
  padding: 15px 15px 15px 25px;
  width: 100%;
  display: flex;
  flex-direction: column;
  margin: 0;
  box-sizing: border-box;
}

.gantt-card :deep(.t-card__body) {
  padding: 0;
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.gantt-chart-container {
  flex: 1;
  width: 100%;
  min-height: 500px;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.gantt-chart-container :deep(.apexcharts-canvas) {
  width: 100% !important;
}

.gantt-chart-container :deep(.apexcharts-svg) {
  width: 100% !important;
}

.gantt-chart-container :deep(.apexcharts-yaxis) {
  min-width: 200px;
}

.gantt-chart-container :deep(.apexcharts-yaxis-label) {
  white-space: nowrap;
  overflow: visible;
  text-overflow: unset;
}

.gantt-chart-container :deep(.apexcharts-xaxis-label) {
  white-space: nowrap;
  overflow: visible;
  text-overflow: unset;
}

.gantt-chart-container :deep(.apexcharts-xaxis) {
  min-height: 50px;
}

.gantt-no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 500px;
  color: #86909c;
  text-align: center;
}

.gantt-no-data .no-data-icon {
  margin-bottom: 20px;
  opacity: 0.6;
}

.gantt-no-data h4 {
  margin: 0 0 10px 0;
  font-size: 18px;
  font-weight: 500;
  color: #1f2937;
}

.gantt-no-data p {
  margin: 5px 0;
  font-size: 14px;
  line-height: 1.5;
}

.gantt-no-data .text-secondary {
  font-size: 12px;
  opacity: 0.7;
}

.recent-activities-section {
/* 上边距 */
  margin: 30px 0 0 0;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.dashboard-item {
  padding: 16px 20px;
  height: 90px;
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
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 82, 217, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.dashboard-chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #0052d9 50%, #764ba2 100%);
}

.dashboard-chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-color: rgba(0, 82, 217, 0.15);
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
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 10px;
  background: linear-gradient(135deg, #1f2937 0%, #0052d9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  display: inline-block;
}

.chart-title::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 30px;
  height: 2px;
  background: linear-gradient(90deg, #667eea 0%, #0052d9 100%);
  border-radius: 1px;
}

.chart-container {
  flex: 1;
  min-height: 200px;
  max-height: 280px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
}

.chart-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(0, 82, 217, 0.2) 50%, transparent 100%);
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
    height: 100vh;
  }

  .charts-row {
    height: 280px;
  }

  .dashboard-item {
    padding: 12px 16px;
    height: 80px;
  }

  .gantt-card {
    padding: 10px;
  }

  .gantt-chart-container {
    min-height: 400px;
  }

  .gantt-no-data {
    min-height: 400px;
  }
}

@media (max-width: 480px) {
  .page-content {
    padding: 5px;
    gap: 5px;
    height: 100vh;
  }

  .charts-row {
    height: 240px;
  }

  .dashboard-item {
    padding: 10px 12px;
    height: 70px;
  }

  .gantt-card {
    padding: 8px;
  }

  .gantt-chart-container {
    min-height: 350px;
  }

  .gantt-no-data {
    min-height: 350px;
  }

  .gantt-no-data h4 {
    font-size: 16px;
  }

  .gantt-no-data p {
    font-size: 12px;
  }
}
</style>
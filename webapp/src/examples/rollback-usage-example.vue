<template>
  <div class="rollback-usage-example">
    <h3>回溯历史功能使用示例</h3>
    
    <!-- 示例1: 在仪表板中显示待审批的回溯申请数量 -->
    <div class="example-section">
      <h4>示例1: 仪表板统计</h4>
      <p>待审批的回溯申请: {{ pendingRollbackCount }}</p>
      <t-button @click="loadPendingCount">刷新数据</t-button>
    </div>

    <!-- 示例2: 快速审批操作 -->
    <div class="example-section">
      <h4>示例2: 快速审批</h4>
      <t-button 
        theme="success" 
        @click="quickApprove"
        :disabled="!canApprove"
      >
        快速批准所有待审批申请
      </t-button>
    </div>

         <!-- 示例3: 获取用户相关的回溯申请 -->
     <div class="example-section">
       <h4>示例3: 用户相关申请</h4>
       <t-button @click="loadUserRollbacks">加载我的回溯申请</t-button>
       <div v-if="userRollbacks.length > 0">
         <p>我的回溯申请数量: {{ userRollbacks.length }}</p>
         <p>我的申请批准率: {{ calculateApprovalRate(userRollbacks) }}%</p>
         <ul>
           <li v-for="rollback in userRollbacks" :key="rollback.rollback_id">
             {{ rollback.workflow_id }} - {{ rollback.status }}
           </li>
         </ul>
       </div>
     </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { getRollbackHistory, approveRollback } from '@/api/rollback.js'

/**
 * 回溯历史功能使用示例
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// 响应式数据
const pendingRollbackCount = ref(0)
const userRollbacks = ref([])
const currentUser = ref(null)

// 计算属性
const canApprove = computed(() => {
  return currentUser.value?.role_key === 'admin'
})

// 方法
const loadPendingCount = async () => {
  try {
    const response = await getRollbackHistory({ status: 'pending' })
    pendingRollbackCount.value = response?.length || 0
    MessagePlugin.success('数据加载成功')
  } catch (error) {
    console.error('加载待审批数量失败:', error)
    MessagePlugin.error('加载失败')
  }
}

// 计算批准率的辅助函数
const calculateApprovalRate = (rollbacks) => {
  const approved = rollbacks.filter(item => item.status === 'approved').length
  const rejected = rollbacks.filter(item => item.status === 'rejected').length
  const processed = approved + rejected
  return processed > 0 ? Math.round((approved / processed) * 100) : 0
}

const quickApprove = async () => {
  if (!canApprove.value) {
    MessagePlugin.warning('您没有审批权限')
    return
  }

  try {
    const response = await getRollbackHistory({ status: 'pending' })
    if (!response || response.length === 0) {
      MessagePlugin.info('没有待审批的申请')
      return
    }

    // 批量批准所有待审批申请
    const approvePromises = response.map(rollback => 
      approveRollback(rollback.rollback_id, 'approved', '批量批准')
    )
    
    await Promise.all(approvePromises)
    MessagePlugin.success(`成功批准 ${response.length} 个申请`)
    
    // 刷新数据
    loadPendingCount()
  } catch (error) {
    console.error('批量批准失败:', error)
    MessagePlugin.error('批量批准失败')
  }
}

const loadUserRollbacks = async () => {
  try {
    const response = await getRollbackHistory()
    if (currentUser.value?.role_key === 'admin') {
      // 管理员可以看到所有申请
      userRollbacks.value = response || []
    } else {
      // 其他用户只能看到自己的申请
      userRollbacks.value = (response || []).filter(
        rollback => rollback.requester_name === currentUser.value?.full_name
      )
    }
    MessagePlugin.success('用户申请加载成功')
  } catch (error) {
    console.error('加载用户申请失败:', error)
    MessagePlugin.error('加载失败')
  }
}

// 生命周期
onMounted(() => {
  // 获取当前用户信息
  const user = localStorage.getItem('user') || localStorage.getItem('currentUser')
  if (user) {
    try {
      currentUser.value = JSON.parse(user)
    } catch (error) {
      console.error('解析用户信息失败:', error)
    }
  }

  // 初始化加载数据
  loadPendingCount()
})
</script>

<style lang="less" scoped>
.rollback-usage-example {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;

  h3 {
    color: var(--td-text-color-primary);
    margin-bottom: 24px;
  }

  .example-section {
    margin-bottom: 32px;
    padding: 16px;
    border: 1px solid var(--td-border-level-1-color);
    border-radius: var(--td-radius-medium);
    background: var(--td-bg-color-container);

    h4 {
      color: var(--td-text-color-primary);
      margin-bottom: 12px;
    }

    p {
      color: var(--td-text-color-secondary);
      margin-bottom: 8px;
    }

    ul {
      margin: 8px 0;
      padding-left: 20px;

      li {
        color: var(--td-text-color-secondary);
        margin-bottom: 4px;
      }
    }
  }
}
</style>

<template>
  <t-header class="dashboard-header">
    <div class="header-content">
      <div class="header-left">
        <h2 class="page-title">{{ pageTitle }}</h2>
      </div>
      <div class="header-right">
        <div class="user-info">
          <t-avatar size="small" class="user-avatar">
            {{ currentUser?.full_name?.charAt(0) || 'U' }}
          </t-avatar>
          <div class="user-details">
            <div class="user-name">{{ currentUser?.full_name || '用户' }}</div>
            <div class="user-role">{{ currentUser?.role_name || '角色' }}</div>
          </div>
        </div>
        <t-dropdown trigger="click">
          <t-button theme="default" variant="text" class="user-dropdown-btn">
            <t-icon name="chevron-down" />
          </t-button>
          <template #dropdown>
            <t-dropdown-item @click="handleLogout">
              <t-icon name="logout" />
              退出登录
            </t-dropdown-item>
          </template>
        </t-dropdown>
      </div>
    </div>
  </t-header>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

/**
 * 顶部导航栏组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const router = useRouter()
const route = useRoute()

// 响应式数据
const currentUser = ref(null)

// 页面标题映射
const pageTitles = {
  'dashboard': '仪表板',
  'restoration': '修复提交',
  'management': '修复管理',
  'evaluation': '评估修复',
  'rollback-history': '回溯历史',
  'evaluation-history': '评估历史',
  'profile': '个人中心'
}

// 响应式页面标题
const pageTitle = ref('')

// 更新页面标题的函数
const updatePageTitle = () => {
  pageTitle.value = getPageTitle()
}

// 获取页面标题的函数
const getPageTitle = () => {
  const path = route.path
  
  // 修复提交流程页面标题
  if (path.startsWith('/restoration-flow/')) {
    if (path.includes('/privacy')) return '修复提交流程 - 保密协议'
    if (path.includes('/form')) return '修复提交流程 - 表单填写'
    if (path.includes('/image-edit')) return '修复提交流程 - 图片编辑'
    if (path.includes('/confirm')) return '修复提交流程 - 信息确认'
    if (path.includes('/success')) return '修复提交流程 - 提交成功'
    return '修复提交流程'
  }
  
  // 普通页面标题
  if (path === '/dashboard') return '仪表板'
  if (path === '/restoration') return '修复提交'
  if (path === '/management') return '修复管理'
  if (path === '/evaluation') return '评估修复'
  if (path === '/rollback-history') return '回溯历史'
  if (path === '/evaluation-history') return '评估历史'
  if (path === '/profile') return '个人中心'
  return '仪表板'
}

// 方法
const handleLogout = () => {
  // 清除本地存储的认证信息
  localStorage.removeItem('authToken')
  localStorage.removeItem('currentUser')
  
  // 跳转到登录页
  router.push('/login')
}

// 监听路由变化，更新页面标题
watch(() => route.path, () => {
  updatePageTitle()
}, { immediate: true })

// 组件挂载时初始化
onMounted(() => {
  // 获取当前用户信息
  const user = localStorage.getItem('currentUser')
  if (user) {
    currentUser.value = JSON.parse(user)
  }
  
  // 初始化页面标题
  updatePageTitle()
})
</script>

<style scoped>
.dashboard-header {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #e7e7e7;
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 240px;
  right: 0;
  z-index: 999;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  background: #0052d9;
  color: #fff;
  font-weight: 600;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  line-height: 1.2;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.2;
}

.user-dropdown-btn {
  padding: 4px 8px;
  border: none;
  background: transparent;
  color: #6b7280;
  transition: all 0.2s ease;
}

.user-dropdown-btn:hover {
  background: #f5f5f5;
  color: #1f2937;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-header {
    left: 200px;
    padding: 0 16px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .user-details {
    display: none;
  }
}

@media (max-width: 480px) {
  .dashboard-header {
    left: 180px;
    padding: 0 12px;
  }
  
  .page-title {
    font-size: 16px;
  }
  
  .user-info {
    gap: 8px;
  }
}
</style>

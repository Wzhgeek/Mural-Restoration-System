<template>
  <t-aside class="dashboard-aside">
    <div class="sidebar-header">
      <div class="logo-container">
        <h3 class="logo-text">克孜尔壁画智慧修复系统</h3>
      </div>
    </div>
    <t-menu 
      theme="light" 
      :value="activeMenu" 
      :expanded="expandedMenus"
      @change="handleMenuChange"
      @expand="handleMenuExpand"
      class="sidebar-menu"
    >
      <t-menu-item value="/dashboard">
        <template #icon>
          <t-icon name="dashboard" />
        </template>
        概览
      </t-menu-item>
      
      <t-menu-item value="/restoration" v-if="canAccessRestoration">
        <template #icon>
          <t-icon name="edit" />
        </template>
        任务提交
      </t-menu-item>
      
      <t-menu-item value="/management" v-if="canAccessManagement">
        <template #icon>
          <t-icon name="star" />
        </template>
        任务管理
      </t-menu-item>
      
      <t-menu-item value="/evaluation" v-if="canAccessEvaluation">
        <template #icon>
          <t-icon name="setting" />
        </template>
        评估修复
      </t-menu-item>


      <!-- 质量管理分组 -->
      <t-submenu value="quality-management" v-if="canAccessQualityManagement">
        <template #title>
          <t-icon name="chart" />
          质量管理
        </template>
        <t-menu-item value="/rollback-approval" v-if="canAccessRollbackApproval">
          <template #icon>
            <t-icon name="check-circle" />
          </template>
          回溯审批
        </t-menu-item>
        <t-menu-item value="/rollback-history" v-if="canAccessRollbackHistory">
          <template #icon>
            <t-icon name="time" />
          </template>
          回溯历史
        </t-menu-item>
        <t-menu-item value="/evaluation-history" v-if="canAccessEvaluationHistory">
          <template #icon>
            <t-icon name="history" />
          </template>
          评估历史
        </t-menu-item>
      </t-submenu>
      
      <t-menu-item value="/work-archive">
        <template #icon>
          <t-icon name="folder" />
        </template>
        前期工作展示
      </t-menu-item>

      <t-menu-item value="/profile">
        <template #icon>
          <t-icon name="user" />
        </template>
        安全中心
      </t-menu-item>
       
      <t-menu-item value="logout" class="logout-item">
        <template #icon>
          <t-icon name="logout" />
        </template>
        退出登录
      </t-menu-item>
     </t-menu>
  </t-aside>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

/**
 * 侧边栏组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const router = useRouter()
const route = useRoute()

// 响应式数据
const currentUser = ref(null)
const activeMenu = ref('/dashboard')
const expandedMenus = ref([])

// 本地存储键名
const EXPANDED_KEY = 'sidebarExpanded'

// 计算属性 - 权限控制
const canAccessRestoration = computed(() => {
  return currentUser.value?.role_key === 'admin' || currentUser.value?.role_key === 'restorer'
})

const canAccessManagement = computed(() => {
  return currentUser.value?.role_key === 'admin'
})

const canAccessEvaluation = computed(() => {
  return currentUser.value?.role_key === 'admin' || currentUser.value?.role_key === 'evaluator'
})

const canAccessRollbackHistory = computed(() => {
  return currentUser.value?.role_key === 'admin' || currentUser.value?.role_key === 'restorer'
})

const canAccessRollbackApproval = computed(() => {
  return currentUser.value?.role_key === 'admin'
})

const canAccessEvaluationHistory = computed(() => {
  return currentUser.value?.role_key === 'admin' || currentUser.value?.role_key === 'evaluator'
})

const canAccessQualityManagement = computed(() => {
  return canAccessRollbackApproval.value || canAccessRollbackHistory.value || canAccessEvaluationHistory.value
})

// 方法
const handleLogout = () => {
  // 清除本地存储的认证信息
  localStorage.removeItem('authToken')
  localStorage.removeItem('currentUser')
  
  // 跳转到登录页
  router.push('/login')
}

const handleMenuChange = (value) => {
  // 如果是退出登录，直接处理
  if (value === 'logout') {
    handleLogout()
    return
  }
  
  // 更新活动菜单状态
  activeMenu.value = value
  
  // 进行路由跳转
  router.push(value)
}

const handleMenuExpand = (value) => {
  expandedMenus.value = value
  localStorage.setItem(EXPANDED_KEY, JSON.stringify(value))
}

// 根据当前路由设置活动菜单
const setActiveMenuFromRoute = () => {
  activeMenu.value = route.path
  // ❌ 不要在这里根据路由去改 expandedMenus
}

// 监听路由变化，自动更新活动菜单状态
watch(
  () => route.path,
  (newPath) => {
    activeMenu.value = newPath
    // ❌ 不要在这里自动展开/收起任何子菜单
  },
  { immediate: true }
)

// 组件挂载时初始化
onMounted(() => {
  // 恢复上次手动展开情况
  const saved = localStorage.getItem(EXPANDED_KEY)
  if (saved) {
    try { 
      expandedMenus.value = JSON.parse(saved) || [] 
    } catch {}
  }

  // 初始化当前用户 & 高亮（不展开）
  const user = localStorage.getItem('currentUser')
  if (user) {
    currentUser.value = JSON.parse(user)
  }
  
  setActiveMenuFromRoute()
})
</script>

<style scoped>
.dashboard-aside {
  width: 240px;
  background: #fff;
  border-right: 1px solid #e7e7e7;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #e7e7e7;
  background: #fafafa;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  text-align: center;
  line-height: 1.4;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
}

.sidebar-menu :deep(.t-menu-item) {
  margin: 4px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.sidebar-menu :deep(.t-menu-item:hover) {
  background: #f0f7ff;
  color: #0052d9;
}

.sidebar-menu :deep(.t-menu-item.t-is-active) {
  background: #0052d9;
  color: #fff;
}

.sidebar-menu :deep(.t-menu-item.t-is-active .t-icon) {
  color: #fff;
}

 .sidebar-menu :deep(.t-menu-item .t-icon) {
   margin-right: 8px;
   font-size: 16px;
 }

 .sidebar-menu :deep(.t-submenu) {
   margin: 4px 0;
   border-radius: 6px;
 }

 .sidebar-menu :deep(.t-submenu .t-submenu__title) {
   border-radius: 6px;
   transition: all 0.2s ease;
   color: #1f2937;
   margin: 0 12px;
 }

 .sidebar-menu :deep(.t-submenu .t-submenu__title:hover) {
   background: #f5f5f5;
   color: #1f2937;
 }

 .sidebar-menu :deep(.t-submenu .t-submenu__title .t-icon) {
   margin-right: 8px;
   font-size: 16px;
   color: #6b7280;
 }

 .sidebar-menu :deep(.t-submenu .t-menu-item) {
   margin: 2px 0;
   padding-left: 32px;
   border-radius: 4px;
   color: #1f2937;
 }

 .sidebar-menu :deep(.t-submenu .t-menu-item:hover) {
   background: #f5f5f5;
   color: #1f2937;
 }

 .sidebar-menu :deep(.t-submenu .t-menu-item.t-is-active) {
   background: #e5e7eb;
   color: #1f2937;
 }

 .logout-item {
   border-top: 1px solid #e7e7e7;
   margin-top: 8px;
   padding-top: 8px;
 }

 .logout-item :deep(.t-menu-item) {
   color: #dc3545;
 }

 .logout-item :deep(.t-menu-item:hover) {
   background: #f8d7da;
   color: #721c24;
 }

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-aside {
    width: 200px;
  }
  
  .logo-text {
    font-size: 14px;
  }
  
  .sidebar-header {
    padding: 16px 12px;
  }
}

@media (max-width: 480px) {
  .dashboard-aside {
    width: 180px;
  }
  
  .logo-text {
    font-size: 12px;
  }
}
</style>

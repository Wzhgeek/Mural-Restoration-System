import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Restoration from '../views/Restoration.vue'
import Evaluation from '../views/Evaluation.vue'
import Management from '../views/Management.vue'
import EvaluationHistory from '../views/EvaluationHistory.vue'
import RollbackHistory from '../views/RollbackHistory.vue'
import Profile from '../views/Profile.vue'

/**
 * 路由配置
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/restoration',
    name: 'Restoration',
    component: Restoration,
    meta: { requiresAuth: true }
  },
  {
    path: '/evaluation',
    name: 'Evaluation',
    component: Evaluation,
    meta: { requiresAuth: true }
  },
  {
    path: '/management',
    name: 'Management',
    component: Management,
    meta: { requiresAuth: true }
  },
  {
    path: '/evaluation-history',
    name: 'EvaluationHistory',
    component: EvaluationHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/rollback-history',
    name: 'RollbackHistory',
    component: RollbackHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('authToken')
  const user = localStorage.getItem('currentUser')
  
  // 如果访问需要认证的页面
  if (to.meta.requiresAuth) {
    if (!token || !user) {
      // 未登录，跳转到登录页
      next('/login')
    } else {
      // 已登录，允许访问
      next()
    }
  } else if (to.path === '/login') {
    // 如果已登录且访问登录页，跳转到Dashboard
    if (token && user) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    // 其他情况正常访问
    next()
  }
})

export default router


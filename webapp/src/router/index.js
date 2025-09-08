import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Restoration from '../views/Restoration.vue'
import Evaluation from '../views/Evaluation.vue'
import Management from '../views/Management.vue'
import EvaluationHistory from '../views/EvaluationHistory.vue'
import RollbackHistory from '../views/RollbackHistory.vue'
import RollbackApproval from '../views/RollbackApproval.vue'
import Profile from '../views/Profile.vue'

// 修复提交流程组件
import RestorationFlowLayout from '../components/RestorationFlowLayout.vue'
import RestorationPrivacy from '../views/RestorationPrivacy.vue'
import RestorationForm from '../views/RestorationForm.vue'
import RestorationImageEdit from '../views/RestorationImageEdit.vue'
import RestorationConfirm from '../views/RestorationConfirm.vue'
import RestorationSuccess from '../views/RestorationSuccess.vue'

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
    path: '/rollback-approval',
    name: 'RollbackApproval',
    component: RollbackApproval,
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
  },
  // 修复提交流程路由
  {
    path: '/restoration-flow/:workflowId',
    component: RestorationFlowLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: to => `/restoration-flow/${to.params.workflowId}/privacy`
      },
      {
        path: 'privacy',
        name: 'RestorationPrivacy',
        component: RestorationPrivacy,
        meta: { step: 0 }
      },
      {
        path: 'form',
        name: 'RestorationForm', 
        component: RestorationForm,
        meta: { step: 1 }
      },
      {
        path: 'image-edit',
        name: 'RestorationImageEdit',
        component: RestorationImageEdit,
        meta: { step: 2 }
      },
      {
        path: 'confirm',
        name: 'RestorationConfirm',
        component: RestorationConfirm,
        meta: { step: 3 }
      },
      {
        path: 'success',
        name: 'RestorationSuccess',
        component: RestorationSuccess,
        meta: { step: 4 }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录状态和修复流程权限
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('authToken')
  const user = localStorage.getItem('currentUser')
  
  // 如果访问需要认证的页面
  if (to.meta.requiresAuth) {
    if (!token || !user) {
      // 未登录，跳转到登录页
      next('/login')
      return
    }
  } else if (to.path === '/login') {
    // 如果已登录且访问登录页，跳转到Dashboard
    if (token && user) {
      next('/dashboard')
      return
    } else {
      next()
      return
    }
  }
  
  // 修复流程路由权限检查
  if (to.path.startsWith('/restoration-flow/')) {
    const workflowId = to.params.workflowId
    
    // 检查工作流ID是否有效
    if (!workflowId) {
      next('/restoration')
      return
    }
    
    // 动态导入 store （避免循环依赖）
    try {
      const { useRestorationFlowStore } = await import('@/stores/restorationFlow')
      const store = useRestorationFlowStore()
      
      // 如果store中没有当前工作流，初始化
      if (store.workflowId !== workflowId) {
        store.initFlow(workflowId)
      }
      
      // 检查步骤权限
      const targetStep = to.meta.step
      const currentStep = store.currentStep
      
      if (targetStep !== undefined) {
        // 不能跳过步骤（成功页面除外）
        if (targetStep !== 4 && targetStep > currentStep + 1) {
          // 重定向到当前应该访问的步骤
          const currentStepRoute = store.getCurrentStep.value
          next(`/restoration-flow/${workflowId}/${currentStepRoute}`)
          return
        }
        
        // 更新store中的当前步骤
        store.goToStep(targetStep)
      }
    } catch (error) {
      console.error('路由守卫错误:', error)
      next('/restoration')
      return
    }
  }
  
  // 其他情况正常访问
  next()
})

export default router


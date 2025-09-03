<template>
  <Layout>
    <div class="profile-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h2 class="page-title">个人信息</h2>
        <p class="page-description">查看和修改个人信息</p>
      </div>

      <!-- 主要内容 -->
      <t-row :gutter="[24, 24]">
        <!-- 左侧主要信息区域 -->
        <t-col :flex="3">
          <!-- 个人问候区域 -->
          <div class="user-greeting">
            <div class="greeting-content">
              <span class="greeting-text">Hi，{{ userInfo?.full_name || '用户' }}</span>
              <span class="greeting-time">祝您工作顺利！</span>
            </div>
            <div class="greeting-logo">
              <t-icon name="logo-tencent" size="120px" />
            </div>
          </div>

          <!-- 基本信息卡片 -->
          <t-card class="profile-info-card" :title="t('pages.profile.personalInfo')" :bordered="false">
            <template #actions>
              <t-button theme="default" shape="square" variant="text" @click="toggleEditMode" :disabled="profileLoading">
                <t-icon name="edit" />
              </t-button>
            </template>
            
            <!-- 加载状态 -->
            <div v-if="profileLoading" class="loading-container">
              <t-loading size="medium" text="加载中..." />
            </div>

            <!-- 显示模式 -->
            <div v-if="!editMode && !profileLoading" class="info-display">
              <t-descriptions :column="2" item-layout="vertical">
                <t-descriptions-item :label="t('pages.profile.username')">
                  {{ userInfo?.username || '-' }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.fullName')">
                  {{ userInfo?.full_name || '-' }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.email')">
                  {{ userInfo?.email || '-' }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.role')">
                  {{ userInfo?.role_name || '-' }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.phone')">
                  {{ userInfo?.phone || '-' }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.createdAt')">
                  {{ formatDate(userInfo?.created_at) }}
                </t-descriptions-item>
              </t-descriptions>
            </div>

            <!-- 编辑模式 -->
            <div v-else-if="editMode && !profileLoading" class="info-edit">
              <t-form
                ref="formRef"
                :data="formData"
                :rules="formRules"
                :label-width="120"
                @submit="handleUpdateProfile"
              >
                <t-form-item name="full_name" :label="t('pages.profile.fullName')">
                  <t-input
                    v-model="formData.full_name"
                    :placeholder="t('pages.profile.fullName')"
                    clearable
                  />
                </t-form-item>

                <t-form-item name="email" :label="t('pages.profile.email')">
                  <t-input
                    v-model="formData.email"
                    type="email"
                    :placeholder="t('pages.profile.email')"
                    clearable
                  />
                </t-form-item>

                <t-form-item name="phone" :label="t('pages.profile.phone')">
                  <t-input
                    v-model="formData.phone"
                    :placeholder="t('pages.profile.phone')"
                    clearable
                  />
                </t-form-item>

                <t-form-item class="form-actions">
                  <t-space>
                    <t-button theme="primary" type="submit" :loading="updateLoading">
                      {{ t('pages.profile.save') }}
                    </t-button>
                    <t-button theme="default" @click="cancelEdit">
                      {{ t('pages.profile.cancel') }}
                    </t-button>
                  </t-space>
                </t-form-item>
              </t-form>
            </div>
          </t-card>

          <!-- 密码修改区域 -->
          <t-card class="password-card" :title="t('pages.profile.changePassword')" :bordered="false">
            <t-form
              ref="passwordFormRef"
              :data="passwordFormData"
              :rules="passwordFormRules"
              :label-width="120"
              @submit="handleChangePassword"
            >
              <t-form-item name="currentPassword" :label="t('pages.profile.currentPassword')">
                <t-input
                  v-model="passwordFormData.currentPassword"
                  type="password"
                  :placeholder="t('pages.profile.currentPassword')"
                  clearable
                />
              </t-form-item>

              <t-form-item name="newPassword" :label="t('pages.profile.newPassword')">
                <t-input
                  v-model="passwordFormData.newPassword"
                  type="password"
                  :placeholder="t('pages.profile.newPassword')"
                  clearable
                />
              </t-form-item>

              <t-form-item name="confirmPassword" :label="t('pages.profile.confirmPassword')">
                <t-input
                  v-model="passwordFormData.confirmPassword"
                  type="password"
                  :placeholder="t('pages.profile.confirmPassword')"
                  clearable
                />
              </t-form-item>

              <t-form-item class="form-actions">
                <t-button theme="primary" type="submit" :loading="passwordLoading">
                  {{ t('pages.profile.updatePassword') }}
                </t-button>
              </t-form-item>
            </t-form>
          </t-card>
        </t-col>

        <!-- 右侧用户信息展示区域 -->
        <t-col :flex="1">
          <!-- 用户头像卡片 -->
          <t-card class="user-avatar-card" :bordered="false">
            <div class="avatar-container">
              <t-avatar
                size="80px"
                :alt="userInfo?.full_name || '用户'"
                class="user-avatar"
              >
                {{ userInfo?.full_name?.charAt(0) || '用' }}
              </t-avatar>
              <div class="user-info">
                <div class="user-name">{{ userInfo?.full_name || '用户' }}</div>
                <div class="user-role">{{ userInfo?.role_name || '角色' }}</div>
                <div class="user-status">
                  <t-tag theme="success" variant="light">在线</t-tag>
                </div>
              </div>
            </div>
          </t-card>

          <!-- 账户统计卡片 -->
          <t-card class="stats-card" :title="t('pages.profile.accountStats')" :bordered="false">
            <!-- 加载状态 -->
            <div v-if="statsLoading" class="loading-container">
              <t-loading size="medium" text="加载统计中..." />
            </div>
            
            <t-descriptions v-else :column="1" size="small">
              <!-- 管理员统计信息 -->
              <template v-if="userInfo?.role_key === 'admin'">
                <t-descriptions-item :label="t('pages.profile.totalWorkflows')">
                  {{ accountStats?.total_workflows || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.runningWorkflows')">
                  {{ accountStats?.running_workflows || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.finishedWorkflows')">
                  {{ accountStats?.finished_workflows || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.pendingEvaluations')">
                  {{ accountStats?.pending_evaluations || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.pendingRollbacks')">
                  {{ accountStats?.pending_rollbacks || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.completionRate')">
                  {{ accountStats?.completion_rate ? accountStats.completion_rate + '%' : '0%' }}
                </t-descriptions-item>
              </template>
              
              <!-- 修复专家统计信息 -->
              <template v-else-if="userInfo?.role_key === 'restorer'">
                <t-descriptions-item :label="t('pages.profile.myWorkflows')">
                  {{ accountStats?.my_workflows || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.myRunningWorkflows')">
                  {{ accountStats?.my_running_workflows || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.myFinishedWorkflows')">
                  {{ accountStats?.my_finished_workflows || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.myRollbackRequests')">
                  {{ accountStats?.my_rollback_requests || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.monthlySubmissions')">
                  {{ accountStats?.monthly_submissions || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.averageScore')">
                  {{ accountStats?.average_score ? accountStats.average_score + '分' : '0分' }}
                </t-descriptions-item>
              </template>
              
              <!-- 评估专家统计信息 -->
              <template v-else-if="userInfo?.role_key === 'evaluator'">
                <t-descriptions-item :label="t('pages.profile.pendingEvaluations')">
                  {{ accountStats?.pending_evaluations || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.completedEvaluations')">
                  {{ accountStats?.completed_evaluations || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.monthlyEvaluations')">
                  {{ accountStats?.monthly_evaluations || 0 }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.averageGivenScore')">
                  {{ accountStats?.average_given_score ? accountStats.average_given_score + '分' : '0分' }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.highScoreRate')">
                  {{ accountStats?.high_score_rate ? accountStats.high_score_rate + '%' : '0%' }}
                </t-descriptions-item>
                <t-descriptions-item :label="t('pages.profile.evaluationEfficiency')">
                  {{ accountStats?.evaluation_efficiency ? accountStats.evaluation_efficiency + '/天' : '0/天' }}
                </t-descriptions-item>
              </template>
              
              <!-- 通用信息 -->
              <t-descriptions-item :label="t('pages.profile.accountAge')">
                {{ accountAge || '未知' }}
              </t-descriptions-item>
            </t-descriptions>
          </t-card>
        </t-col>
      </t-row>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import Layout from '@/components/Layout.vue'
import { getUserProfile, updateUserProfile, changePassword, getAccountStats } from '@/api/profile.js'

// 作者信息
/**
 * 个人信息页面组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// 国际化函数（简化版）
const t = (key) => {
  const translations = {
    'pages.profile.personalInfo': '基本信息',
    'pages.profile.username': '用户名',
    'pages.profile.fullName': '姓名',
    'pages.profile.email': '邮箱',
    'pages.profile.role': '角色',
    'pages.profile.phone': '联系电话',
    'pages.profile.createdAt': '注册时间',
    'pages.profile.save': '保存修改',
    'pages.profile.cancel': '取消',
    'pages.profile.changePassword': '修改密码',
    'pages.profile.currentPassword': '当前密码',
    'pages.profile.newPassword': '新密码',
    'pages.profile.confirmPassword': '确认密码',
    'pages.profile.updatePassword': '更新密码',
    'pages.profile.accountStats': '账户统计',
    // 管理员统计
    'pages.profile.totalWorkflows': '总工作流数',
    'pages.profile.runningWorkflows': '进行中的工作流',
    'pages.profile.finishedWorkflows': '已完成的工作流',
    'pages.profile.pendingEvaluations': '待评估',
    'pages.profile.pendingRollbacks': '待审批回溯',
    'pages.profile.completionRate': '完成率',
    // 修复专家统计
    'pages.profile.myWorkflows': '我的工作流',
    'pages.profile.myRunningWorkflows': '进行中的工作流',
    'pages.profile.myFinishedWorkflows': '已完成的工作流',
    'pages.profile.myRollbackRequests': '我的回溯申请',
    'pages.profile.monthlySubmissions': '本月提交',
    'pages.profile.averageScore': '平均评分',
    // 评估专家统计
    'pages.profile.completedEvaluations': '已评估',
    'pages.profile.monthlyEvaluations': '本月评估',
    'pages.profile.averageGivenScore': '平均给分',
    'pages.profile.highScoreRate': '高分率',
    'pages.profile.evaluationEfficiency': '评估效率',
    // 通用
    'pages.profile.accountAge': '账户年龄'
  }
  return translations[key] || key
}

// 响应式数据
const userInfo = ref(null)
const accountStats = ref(null)
const editMode = ref(false)
const updateLoading = ref(false)
const passwordLoading = ref(false)
const profileLoading = ref(false)
const statsLoading = ref(false)

const formRef = ref()
const passwordFormRef = ref()

// 个人信息表单数据
const formData = reactive({
  full_name: '',
  email: '',
  phone: ''
})

// 个人信息表单验证规则
const formRules = {
  full_name: [
    { required: true, message: '请输入姓名', type: 'error' },
    { min: 2, message: '姓名至少2个字符', type: 'error' }
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', type: 'error' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码', type: 'error' }
  ]
}

// 密码表单数据
const passwordFormData = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码表单验证规则
const passwordFormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', type: 'error' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', type: 'error' },
    { min: 6, message: '密码长度不能少于6位', type: 'error' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', type: 'error' },
    {
      validator: (val) => val === passwordFormData.newPassword,
      message: '两次输入的密码不一致',
      type: 'error'
    }
  ]
}

// 计算属性
const accountAge = computed(() => {
  if (!userInfo.value?.created_at) return '未知'
  const createdDate = new Date(userInfo.value.created_at)
  const now = new Date()
  const diffTime = Math.abs(now - createdDate)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 30) {
    return `${diffDays}天`
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30)
    return `${months}个月`
  } else {
    const years = Math.floor(diffDays / 365)
    return `${years}年`
  }
})

// 方法
const loadUserProfile = async () => {
  profileLoading.value = true
  try {
    const response = await getUserProfile()
    // 根据前端对接文档，用户信息直接返回，不需要.data包装
    userInfo.value = response
    // 同步表单数据
    formData.full_name = response.full_name || ''
    formData.email = response.email || ''
    formData.phone = response.phone || ''
  } catch (error) {
    MessagePlugin.error('加载用户信息失败: ' + (error.message || '未知错误'))
    // 设置默认值避免页面崩溃
    userInfo.value = {
      username: '未知用户',
      full_name: '未知用户',
      email: '',
      phone: '',
      role_name: '未知角色',
      role_key: 'unknown',
      created_at: new Date().toISOString()
    }
  } finally {
    profileLoading.value = false
  }
}

const loadAccountStats = async () => {
  statsLoading.value = true
  try {
    const response = await getAccountStats()
    // 根据前端对接文档，仪表板数据直接返回，不需要.data包装
    accountStats.value = response
  } catch (error) {
    console.error('加载账户统计失败:', error)
    // 静默失败，不显示错误，避免影响用户体验
    // 设置默认值
    accountStats.value = {
      total_workflows: 0,
      running_workflows: 0,
      finished_workflows: 0,
      pending_evaluations: 0,
      pending_rollbacks: 0,
      completion_rate: 0,
      my_workflows: 0,
      my_running_workflows: 0,
      my_finished_workflows: 0,
      my_rollback_requests: 0,
      monthly_submissions: 0,
      average_score: 0,
      completed_evaluations: 0,
      monthly_evaluations: 0,
      average_given_score: 0,
      high_score_rate: 0,
      evaluation_efficiency: 0
    }
  } finally {
    statsLoading.value = false
  }
}

const toggleEditMode = () => {
  editMode.value = !editMode.value
  if (!editMode.value) {
    // 取消编辑时恢复原始数据
    formData.full_name = userInfo.value?.full_name || ''
    formData.email = userInfo.value?.email || ''
    formData.phone = userInfo.value?.phone || ''
  }
}

const cancelEdit = () => {
  toggleEditMode()
}

const handleUpdateProfile = async (context) => {
  if (context.validateResult !== true) {
    return
  }

  updateLoading.value = true
  try {
    // 根据前端对接文档，构建更新数据
    const updateData = {
      full_name: formData.full_name.trim()
    }
    
    // 只有当邮箱不为空时才添加
    if (formData.email && formData.email.trim()) {
      updateData.email = formData.email.trim()
    }
    
    // 只有当电话不为空时才添加
    if (formData.phone && formData.phone.trim()) {
      updateData.phone = formData.phone.trim()
    }

    const response = await updateUserProfile(updateData)

    MessagePlugin.success('个人信息更新成功')
    editMode.value = false

    // 重新加载用户信息
    await loadUserProfile()

    // 更新顶部导航栏的用户信息
    if (typeof window !== 'undefined' && window.parent) {
      const userNameElement = window.parent.document.getElementById('userName')
      if (userNameElement) {
        userNameElement.textContent = formData.full_name
      }
    }
  } catch (error) {
    
    // 处理422验证错误
    if (error.response && error.response.status === 422) {
      const errorData = error.response.data
      if (errorData && errorData.detail) {
        // 如果是数组形式的验证错误
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => {
            // 处理不同的错误格式
            if (typeof err === 'string') {
              return err
            } else if (err.msg) {
              return err.msg
            } else if (err.message) {
              return err.message
            } else if (err.loc && err.msg) {
              // FastAPI验证错误格式: {"loc": ["body", "field"], "msg": "error message", "type": "error_type"}
              return `${err.loc.join('.')}: ${err.msg}`
            } else {
              return JSON.stringify(err)
            }
          }).join('; ')
          MessagePlugin.error('数据验证失败: ' + errorMessages)
        } else {
          MessagePlugin.error('数据验证失败: ' + errorData.detail)
        }
      } else {
        MessagePlugin.error('数据格式不正确，请检查输入信息')
      }
    } else if (error.response && error.response.status === 400) {
      MessagePlugin.error('请求参数错误，请检查输入信息')
    } else if (error.response && error.response.status === 401) {
      MessagePlugin.error('登录已过期，请重新登录')
    } else {
      MessagePlugin.error(error.message || '更新失败，请稍后重试')
    }
  } finally {
    updateLoading.value = false
  }
}

const handleChangePassword = async (context) => {
  if (context.validateResult !== true) {
    return
  }

  passwordLoading.value = true
  try {
    await changePassword({
      current_password: passwordFormData.currentPassword,
      new_password: passwordFormData.newPassword
    })

    MessagePlugin.success('密码修改成功')

    // 清空表单
    passwordFormData.currentPassword = ''
    passwordFormData.newPassword = ''
    passwordFormData.confirmPassword = ''
  } catch (error) {
    console.error('修改密码失败:', error)
    
    // 处理422验证错误
    if (error.response && error.response.status === 422) {
      const errorData = error.response.data
      if (errorData && errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => err.msg || err.message || err).join('; ')
          MessagePlugin.error('密码验证失败: ' + errorMessages)
        } else {
          MessagePlugin.error('密码验证失败: ' + errorData.detail)
        }
      } else {
        MessagePlugin.error('密码格式不正确，请检查输入')
      }
    } else if (error.response && error.response.status === 400) {
      MessagePlugin.error('当前密码错误或新密码不符合要求')
    } else if (error.response && error.response.status === 401) {
      MessagePlugin.error('登录已过期，请重新登录')
    } else {
      MessagePlugin.error(error.message || '密码修改失败，请稍后重试')
    }
  } finally {
    passwordLoading.value = false
  }
}

// 工具方法
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadUserProfile()
  loadAccountStats()
})
</script>

<style lang="less" scoped>
.profile-container {
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

.user-greeting {
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
  font: var(--td-font-title-large);
  background: var(--td-bg-color-container);
  color: var(--td-text-color-primary);
  border-radius: var(--td-radius-medium);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  .greeting-content {
    .greeting-text {
      font-size: 28px;
      font-weight: 600;
    }

    .greeting-time {
      margin-left: var(--td-comp-margin-xl);
      font: var(--td-font-body-medium);
      color: var(--td-text-color-secondary);
    }
  }

  .greeting-logo {
    color: var(--td-brand-color);
    opacity: 0.8;
  }
}

.profile-info-card {
  margin-bottom: 24px;
  width: 100%;
  min-height: 320px;   /* 仅保证空态不太扁 */
  height: auto;        /* 让内容自己撑开 */

  :deep(.t-card__body) {
    padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
  }

  .info-display {
    .t-descriptions {
      margin-top: 24px;
    }
  }

  .info-edit {
    .form-actions {
      margin-top: 24px;
      text-align: left;
    }
  }
}

.password-card {
  margin-bottom: 24px;

  :deep(.t-card__body) {
    padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
  }

  .form-actions {
    margin-top: 24px;
    text-align: left;
  }
}

.user-avatar-card {
  margin-bottom: 24px;

  :deep(.t-card__body) {
    padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
  }

  .avatar-container {
    text-align: center;

    .user-avatar {
      margin-bottom: var(--td-comp-margin-xxl);
      background: var(--td-brand-color);
      color: var(--td-text-color-anti);
      font-size: 32px;
      font-weight: 600;
    }

    .user-info {
      .user-name {
        font: var(--td-font-title-large);
        margin-bottom: var(--td-comp-margin-s);
        color: var(--td-text-color-primary);
      }

      .user-role {
        font: var(--td-font-body-medium);
        margin-bottom: var(--td-comp-margin-l);
        color: var(--td-text-color-secondary);
      }

      .user-status {
        display: inline-block;
      }
    }
  }
}

.stats-card {
  :deep(.t-card__body) {
    padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
  }

  .t-descriptions {
    :deep(.t-descriptions-item__label) {
      font-weight: 500;
    }

    :deep(.t-descriptions-item__content) {
      font-size: 18px;
      font-weight: 600;
      color: var(--td-text-color-primary);
    }
  }
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 120px;
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
}

// 响应式设计
@media (max-width: 768px) {
  .profile-container {
    padding: 16px;
  }

  .user-greeting {
    flex-direction: column;
    text-align: center;
    gap: 16px;

    .greeting-content {
      .greeting-text {
        font-size: 24px;
      }
    }
  }

  .t-descriptions {
    :deep(.t-descriptions-item) {
      width: 100% !important;
    }
  }
}
</style>

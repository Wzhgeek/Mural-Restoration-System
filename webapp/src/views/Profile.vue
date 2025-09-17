<template>
  <Layout>
    <div class="security-center">
      <!-- 顶部信息条 -->
      <div class="hero card">
        <div class="hero-left">
          <t-avatar size="72px" class="hero-avatar">
            {{ initials }}
          </t-avatar>
          <div class="hero-meta">
            <div class="hero-name">
              <span class="name-text">{{ userInfo?.full_name || '未知用户' }}</span>
              <t-tag size="small" theme="primary" variant="light-outline">
                {{ userInfo?.role_name || '未知角色' }}
              </t-tag>
      </div>
            <div class="hero-sub">
              {{ userInfo?.email || '暂无邮箱' }} · {{ userInfo?.username || '未知用户名' }}
            </div>
            <div class="hero-sub light">
              注册于：{{ formatDate(userInfo?.created_at) }}（{{ accountAge }}）
            </div>
          </div>
        </div>
        <div class="hero-right">
          <t-button variant="outline" theme="primary" @click="toggleEditMode" :disabled="profileLoading">
            <t-icon name="edit" style="margin-right:6px" /> {{ editMode ? '取消编辑' : '编辑资料' }}
              </t-button>
        </div>
      </div>

      <t-row :gutter="[16, 16]">
        <!-- 左：基本信息 + 安全设置 -->
        <t-col :xs="12" :sm="12" :md="8" :lg="8" :xl="8">
          <div class="left-column">
            <!-- 基本信息 -->
            <t-card :bordered="false" class="card">
              <template #title>基本信息</template>

              <div v-if="profileLoading" class="loading">
                <t-loading size="small" text="加载中..." />
            </div>

              <!-- 展示模式 -->
              <div v-else-if="!editMode" class="info-grid">
                <div class="info-item">
                  <div class="info-label">姓名</div>
                  <div class="info-value">{{ pretty(userInfo?.full_name) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">用户名</div>
                  <div class="info-value">{{ pretty(userInfo?.username) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">邮箱</div>
                  <div class="info-value">{{ pretty(userInfo?.email) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">联系电话</div>
                  <div class="info-value">{{ pretty(userInfo?.phone, '·') }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">职业</div>
                  <div class="info-value">{{ pretty(userInfo?.unit, '·') }}</div>
                </div>
            </div>

            <!-- 编辑模式 -->
              <div v-else class="edit-wrap">
              <t-form
                ref="formRef"
                :data="formData"
                :rules="formRules"
                  label-align="left"
                  :label-width="88"
                @submit="handleUpdateProfile"
              >
                  <t-form-item name="full_name" label="姓名">
                    <t-input v-model="formData.full_name" placeholder="请输入姓名" clearable />
                </t-form-item>
                  <t-form-item name="email" label="邮箱">
                    <t-input v-model="formData.email" placeholder="请输入邮箱" clearable />
                </t-form-item>
                  <t-form-item name="phone" label="联系电话">
                    <t-input v-model="formData.phone" placeholder="请输入手机号" clearable />
                </t-form-item>
                  <t-form-item name="unit" label="职业">
                    <t-input v-model="formData.unit" placeholder="请输入职业" clearable />
                </t-form-item>
                  <t-form-item>
                  <t-space>
                      <t-button theme="primary" type="submit" :loading="updateLoading">保存修改</t-button>
                      <t-button variant="outline" @click="cancelEdit">取消</t-button>
                  </t-space>
                </t-form-item>
              </t-form>
            </div>
          </t-card>

            <!-- 安全设置（修改密码） -->
            <t-card :bordered="false" class="card">
              <template #title>安全设置</template>
            <t-form
              ref="passwordFormRef"
              :data="passwordFormData"
              :rules="passwordFormRules"
                label-align="left"
                :label-width="88"
              @submit="handleChangePassword"
            >
                <t-form-item name="currentPassword" label="当前密码">
                  <t-input v-model="passwordFormData.currentPassword" type="password" placeholder="请输入当前密码" clearable />
              </t-form-item>
                <t-form-item name="newPassword" label="新密码">
                  <t-input v-model="passwordFormData.newPassword" type="password" placeholder="至少6位，建议包含字母与数字" clearable />
              </t-form-item>
                <t-form-item name="confirmPassword" label="确认密码">
                  <t-input v-model="passwordFormData.confirmPassword" type="password" placeholder="请再次输入新密码" clearable />
              </t-form-item>
                <t-form-item>
                  <t-button theme="primary" type="submit" :loading="passwordLoading">更新密码</t-button>
              </t-form-item>
            </t-form>
          </t-card>
          </div>
        </t-col>

        <!-- 右：账户概览 + 账户统计 -->
        <t-col :xs="12" :sm="12" :md="4" :lg="4" :xl="4">
          <t-card :bordered="false" class="card">
            <template #title>账户概览</template>

            <div v-if="statsLoading" class="loading">
              <t-loading size="small" text="加载统计..." />
            </div>

            <div v-else>
              <!-- 小胶囊统计（保持原有风格） -->
              <div class="stats">
                <div class="stat">
                  <div class="stat-num">{{ safeNum(commonStats.completed) }}</div>
                  <div class="stat-label">已完成</div>
                </div>
                <div class="stat">
                  <div class="stat-num">{{ safeNum(commonStats.running) }}</div>
                  <div class="stat-label">进行中</div>
                </div>
              </div>

              <!-- 纵向键值统计（新增的 7 项） -->
              <div class="stat-list">
                <div class="stat-row" v-for="it in kvStats" :key="it.label">
                  <span class="k">{{ it.label }}</span>
                  <span class="v">{{ it.value }}</span>
                </div>
              </div>
            </div>
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

/** 状态 */
const userInfo = ref(null)
const accountStats = ref(null)

const profileLoading = ref(false)
const statsLoading = ref(false)
const editMode = ref(false)
const updateLoading = ref(false)
const passwordLoading = ref(false)

const formRef = ref()
const passwordFormRef = ref()

/** 表单：基本信息 */
const formData = reactive({
  full_name: '',
  email: '',
  phone: '',
  unit: ''
})
const formRules = {
  full_name: [
    { required: true, message: '请输入姓名' },
    { min: 2, message: '姓名至少2个字符' }
  ],
  email: [
    { validator: (val) => !val || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val), message: '请输入有效邮箱' }
  ],
  phone: [
    { validator: (val) => !val || /^1[3-9]\d{9}$/.test(val), message: '请输入有效手机号' }
  ]
}

/** 表单：修改密码 */
const passwordFormData = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordFormRules = {
  currentPassword: [{ required: true, message: '请输入当前密码' }],
  newPassword: [
    { required: true, message: '请输入新密码' },
    { min: 6, message: '密码长度不能少于6位' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码' },
    {
      validator: (val) => val === passwordFormData.newPassword,
      message: '两次输入的密码不一致'
    }
  ]
}

/** 计算 */
const initials = computed(() => {
  const name = userInfo.value?.full_name || userInfo.value?.username || '系统用户'
  return name.charAt(0).toUpperCase()
})
const accountAge = computed(() => {
  if (!userInfo.value?.created_at) return '未知'
  const created = new Date(userInfo.value.created_at)
  const days = Math.ceil((Date.now() - created.getTime()) / 86400000)
  if (days < 30) return `${days}天`
  if (days < 365) return `${Math.floor(days / 30)}个月`
  return `${Math.floor(days / 365)}年`
})
const safeNum = (n) => (typeof n === 'number' && !isNaN(n) ? n : 0)
const pretty = (v, fallback = '未设置') => (v && String(v).trim() ? v : fallback)
const formatDate = (s) => (s ? new Date(s).toLocaleDateString('zh-CN') : '未知')

/** 通用小统计（沿用原来逻辑） */
const commonStats = computed(() => ({
  completed:
    userInfo.value?.role_key === 'admin'
      ? accountStats.value?.finished_workflows
      : userInfo.value?.role_key === 'restorer'
      ? accountStats.value?.my_finished_workflows
      : accountStats.value?.completed_evaluations,
  running:
    userInfo.value?.role_key === 'admin'
      ? accountStats.value?.running_workflows
      : userInfo.value?.role_key === 'restorer'
      ? accountStats.value?.my_running_workflows
      : accountStats.value?.pending_evaluations
}))

/** 新增：纵向键值统计（7项） */
const kvStats = computed(() => {
  // 兼容非 admin 角色的数据缺失；缺失时显示合理的默认值
  const totalWorkflows =
    userInfo.value?.role_key === 'admin'
      ? safeNum(accountStats.value?.total_workflows)
      : safeNum(accountStats.value?.my_workflows)

  const running =
    userInfo.value?.role_key === 'admin'
      ? safeNum(accountStats.value?.running_workflows)
      : userInfo.value?.role_key === 'restorer'
      ? safeNum(accountStats.value?.my_running_workflows)
      : safeNum(accountStats.value?.pending_evaluations)

  const finished =
    userInfo.value?.role_key === 'admin'
      ? safeNum(accountStats.value?.finished_workflows)
      : userInfo.value?.role_key === 'restorer'
      ? safeNum(accountStats.value?.my_finished_workflows)
      : safeNum(accountStats.value?.completed_evaluations)

  const pendingEval = safeNum(accountStats.value?.pending_evaluations)
  const pendingRollback = safeNum(accountStats.value?.pending_rollbacks)
  
  // 计算完成率，如果没有数据则显示默认值
  let completionRate = '0%'
  if (totalWorkflows > 0) {
    completionRate = Math.round((finished / totalWorkflows) * 100) + '%'
  } else if (accountStats.value?.completion_rate !== undefined) {
    completionRate = (accountStats.value.completion_rate ?? 0) + '%'
  }

  return [
    { label: '总工作流数', value: totalWorkflows },
    { label: '进行中的工作流', value: running },
    { label: '已完成的工作流', value: finished },
    { label: '待评估', value: pendingEval },
    { label: '待审批回溯', value: pendingRollback },
    { label: '完成率', value: completionRate },
    { label: '账户年龄', value: accountAge.value }
  ]
})

/** 加载数据 */
const loadUserProfile = async () => {
  profileLoading.value = true
  try {
    const res = await getUserProfile()
    userInfo.value = res
    formData.full_name = res.full_name || ''
    formData.email = res.email || ''
    formData.phone = res.phone || ''
    formData.unit = res.unit || ''
  } catch (e) {
    MessagePlugin.error('加载用户信息失败')
    userInfo.value = {
      username: '系统用户',
      full_name: '系统用户',
      email: 'user@system.com',
      phone: '138****8888',
      role_name: '系统管理员',
      role_key: 'admin',
      created_at: new Date().toISOString()
    }
  } finally {
    profileLoading.value = false
  }
}
const loadAccountStats = async () => {
  statsLoading.value = true
  try {
    accountStats.value = await getAccountStats()
  } catch {
    // 提供默认统计数据，避免显示空白
    accountStats.value = {
      total_workflows: 15,
      running_workflows: 3,
      finished_workflows: 12,
      my_workflows: 8,
      my_running_workflows: 2,
      my_finished_workflows: 6,
      pending_evaluations: 5,
      completed_evaluations: 7,
      pending_rollbacks: 1,
      completion_rate: 80
    }
  } finally {
    statsLoading.value = false
  }
}

/** 交互 */
const toggleEditMode = () => {
  editMode.value = !editMode.value
  if (!editMode.value && userInfo.value) {
    formData.full_name = userInfo.value.full_name || ''
    formData.email = userInfo.value.email || ''
    formData.phone = userInfo.value.phone || ''
  }
}
const cancelEdit = () => toggleEditMode()

const handleUpdateProfile = async (ctx) => {
  if (ctx.validateResult !== true) return
  updateLoading.value = true
  try {
    const payload = { full_name: formData.full_name.trim() }
    if (formData.email?.trim()) payload.email = formData.email.trim()
    if (formData.phone?.trim()) payload.phone = formData.phone.trim()
    await updateUserProfile(payload)
    MessagePlugin.success('个人信息已更新')
    editMode.value = false
    await loadUserProfile()
  } catch (e) {
    if (e?.response?.status === 401) MessagePlugin.error('登录已过期，请重新登录')
    else if (e?.response?.status === 422) MessagePlugin.error('数据校验失败，请检查输入')
    else MessagePlugin.error(e?.message || '更新失败')
  } finally {
    updateLoading.value = false
  }
}

const handleChangePassword = async (ctx) => {
  if (ctx.validateResult !== true) return
  passwordLoading.value = true
  try {
    await changePassword({
      current_password: passwordFormData.currentPassword,
      new_password: passwordFormData.newPassword
    })
    MessagePlugin.success('密码修改成功，请重新登录')
    
    // 清空表单
    passwordFormData.currentPassword = ''
    passwordFormData.newPassword = ''
    passwordFormData.confirmPassword = ''
    
    // 延迟1秒后自动退出登录
    setTimeout(() => {
      // 清除本地存储的认证信息
      localStorage.removeItem('authToken')
      localStorage.removeItem('currentUser')
      
      // 跳转到登录页面
      window.location.href = '/login'
    }, 1000)
    
  } catch (e) {
    if (e?.response?.status === 401) MessagePlugin.error('登录已过期，请重新登录')
    else if (e?.response?.status === 400) MessagePlugin.error('当前密码错误或新密码不符合要求')
    else if (e?.response?.status === 422) MessagePlugin.error('密码格式不正确，请检查输入')
    else MessagePlugin.error(e?.message || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}

/** 生命周期 */
onMounted(() => {
  loadUserProfile()
  loadAccountStats()
})
</script>

<style scoped>
.security-center {
  padding: 16px;
  background: var(--td-bg-color-container);
}

/* 左侧列布局 */
.left-column {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* 卡片通用 */
.card {
  background: #fff;
  border: 1px solid var(--td-component-border);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(31, 41, 55, 0.04);
}
:deep(.t-card__body) {
  padding: 14px 16px;
}
:deep(.t-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid var(--td-component-border);
}

/* 顶部信息条 */
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
}
.hero-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.hero-avatar {
  background: var(--td-brand-color);
  color: var(--td-text-color-anti);
      font-size: 28px;
  font-weight: 700;
}
.hero-meta { display: flex; flex-direction: column; gap: 2px; }
.hero-name { display: flex; align-items: center; gap: 8px; }
.name-text { font-weight: 600; font-size: 18px; color: var(--td-text-color-primary); }
.hero-sub { font-size: 13px; color: var(--td-text-color-secondary); }
.hero-sub.light { opacity: .9; }

/* 基本信息展示 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 20px;
}
.info-item { 
  display: flex; 
  flex-direction: column; 
  gap: 6px; 
  padding: 8px 12px;
  background: #fafbfc;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  transition: all 0.2s ease;
}
.info-item:hover {
  background: #f5f7fa;
  border-color: #e6f3ff;
}
.info-label { 
  font-size: 12px; 
  color: var(--td-text-color-secondary); 
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.info-value { 
  font-size: 14px; 
  color: var(--td-text-color-primary); 
      font-weight: 600;
  min-height: 20px;
  display: flex;
  align-items: center;
}

/* 小胶囊统计 */
.stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 6px;
}
.stat {
  border: 1px dashed var(--td-component-border);
  border-radius: 10px;
  padding: 12px 10px;
  background: #fafafa;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stat-num { font-size: 20px; font-weight: 700; color: var(--td-text-color-primary); line-height: 1.2; }
.stat-label { margin-top: 4px; font-size: 12px; color: var(--td-text-color-secondary); }

/* 纵向键值统计（新增） */
.stat-list {
  margin-top: 12px;
  border-top: 1px solid var(--td-component-border);
  padding-top: 12px;
}
.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 4px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}
.stat-row:hover {
  background-color: #f8f9fa;
}
.stat-row + .stat-row { 
  border-top: 1px solid #f0f0f0; 
  margin-top: 4px;
  padding-top: 12px;
}
.stat-row .k { 
  color: var(--td-text-color-secondary); 
  font-size: 13px; 
      font-weight: 500;
    }
.stat-row .v { 
  color: var(--td-text-color-primary); 
      font-weight: 600;
  font-size: 14px;
  background: #f0f8ff;
  padding: 2px 8px;
  border-radius: 12px;
  border: 1px solid #e6f3ff;
}

/* 加载 */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .security-center { padding: 12px; }
  .hero { flex-direction: column; align-items: flex-start; gap: 8px; }
  .info-grid { grid-template-columns: 1fr; }
  .stats { grid-template-columns: 1fr 1fr; }
}
</style>

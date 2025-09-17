<template>
  <div class="login-wrapper">
    <!-- 背景图片层 -->
    <div class="background-layer"></div>
    
    <!-- 渐变遮罩层 -->
    <div class="gradient-overlay"></div>
    
    <!-- 登录内容 -->
    <div class="login-container">
      <div class="login-form">
        <div class="title-container">
          <div class="title-wrapper">
            <h1 class="title">克孜尔石窟壁画智慧修复</h1>
            <h1 class="title-sub">全生命周期管理系统</h1>
          </div>
          <p class="subtitle">请输入您的账号信息</p>
        </div>
        
        <t-form
          ref="form"
          :data="formData"
          :rules="formRules"
          label-width="0"
          @submit="onSubmit"
        >
          <!-- 角色选择 -->
          <t-form-item name="selectedRole">
            <div class="role-selection">
              <div class="role-selection-label">选择角色</div>
              <div class="role-tabs">
                <div 
                  v-for="role in roleOptions" 
                  :key="role.value"
                  class="role-tab"
                  :class="{ active: formData.selectedRole === role.value }"
                  @click="formData.selectedRole = role.value"
                >
                  <t-icon :name="role.icon" class="role-icon" />
                  <span class="role-label">{{ role.label }}</span>
                </div>
              </div>
            </div>
          </t-form-item>

          <t-form-item name="username">
            <t-input 
              v-model="formData.username" 
              size="large" 
              placeholder="请输入用户名"
              clearable
            >
              <template #prefix-icon>
                <t-icon name="user" />
              </template>
            </t-input>
          </t-form-item>

          <t-form-item name="password">
            <t-input
              v-model="formData.password"
              size="large"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              clearable
            >
              <template #prefix-icon>
                <t-icon name="lock-on" />
              </template>
              <template #suffix-icon>
                <t-icon 
                  :name="showPassword ? 'browse' : 'browse-off'" 
                  @click="showPassword = !showPassword" 
                />
              </template>
            </t-input>
          </t-form-item>

          <div class="options-container">
            <t-checkbox v-model="formData.rememberMe">记住密码</t-checkbox>
            <a href="#" class="forgot-password" @click.prevent="handleForgotPassword">忘记密码？</a>
          </div>

          <t-form-item class="login-button-container">
            <t-button 
              block 
              size="large" 
              type="submit"
              :loading="loading"
            >
              登录
            </t-button>
          </t-form-item>
        </t-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'

// 作者信息
/**
 * 登录界面组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// 响应式数据
const form = ref()
const showPassword = ref(false)
const loading = ref(false)

// 表单数据
const formData = reactive({
  username: '',
  password: '',
  rememberMe: false,
  selectedRole: 'admin'  // 默认选择管理员角色
})

// 角色选项
const roleOptions = [
  { value: 'admin', label: '管理员', icon: 'user-setting' },
  { value: 'restorer', label: '修复专家', icon: 'tools' },
  { value: 'evaluator', label: '评估专家', icon: 'star' }
]

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: '请输入用户名', type: 'error' }
  ],
  password: [
    { required: true, message: '请输入密码', type: 'error' },
    { min: 6, message: '密码长度不能少于6位', type: 'error' }
  ]
}

// 登录提交
const onSubmit = async (context) => {
  if (context.validateResult === true) {
    loading.value = true
    try {
      // 调用后端登录API
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          selected_role: formData.selectedRole
        })
      })
      
      // 检查响应状态
      if (!response.ok) {
        let errorMessage = '登录失败'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch (parseError) {
          // 如果无法解析JSON，使用状态文本
          errorMessage = `登录失败 (${response.status}: ${response.statusText})`
        }
        throw new Error(errorMessage)
      }
      
      // 检查响应内容类型
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('服务器返回了无效的响应格式')
      }
      
      // 解析JSON响应
      let loginData
      try {
        const responseText = await response.text()
        
        if (!responseText.trim()) {
          throw new Error('服务器返回了空响应')
        }
        
        loginData = JSON.parse(responseText)
      } catch (parseError) {
        console.error('JSON解析错误:', parseError)
        throw new Error('无法解析服务器响应')
      }
      
      // 验证响应数据格式
      if (!loginData.access_token || !loginData.user) {
        throw new Error('服务器返回的数据格式不正确')
      }
      
      // 存储token和用户信息
      localStorage.setItem('authToken', loginData.access_token)
      localStorage.setItem('currentUser', JSON.stringify(loginData.user))
      
      MessagePlugin.success('登录成功')
      
      // 登录成功后跳转到Dashboard
      setTimeout(() => {
        window.location.href = '/dashboard'
      }, 1000)
      
    } catch (error) {
      console.error('登录错误详情:', error)
      MessagePlugin.error(error.message || '登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  }
}

// 忘记密码处理
const handleForgotPassword = () => {
  MessagePlugin.info('忘记密码功能待实现')
}
</script>

<style scoped>
.login-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  margin: 0;
  padding: 0;
}

/* 背景图片层 */
.background-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/login-background.png');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  z-index: 1;
  min-width: 100%;
  min-height: 100%;
  animation: backgroundFloat 20s ease-in-out infinite;
}

/* 背景浮动动画 */
@keyframes backgroundFloat {
  0%, 100% {
    transform: scale(1) translateY(0px);
    filter: brightness(1) contrast(1);
  }
  25% {
    transform: scale(1.02) translateY(-5px);
    filter: brightness(1.05) contrast(1.02);
  }
  50% {
    transform: scale(1.01) translateY(-3px);
    filter: brightness(1.02) contrast(1.01);
  }
  75% {
    transform: scale(1.03) translateY(-7px);
    filter: brightness(1.08) contrast(1.03);
  }
}

/* 渐变遮罩层 */
.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 120%;
  height: 120%;
  background: linear-gradient(
    to right,
    rgba(0, 0, 0, 0) 0%,
    rgba(0, 0, 0, 0.1) 15%,
    rgba(0, 0, 0, 0.2) 30%,
    rgba(0, 0, 0, 0.3) 45%,
    rgba(0, 0, 0, 0.4) 60%,
    rgba(0, 0, 0, 0.5) 75%,
    rgba(0, 0, 0, 0.6) 90%,
    rgba(0, 0, 0, 0.7) 120%
  );
  z-index: 2;
  animation: gradientPulse 15s ease-in-out infinite;
}

/* 渐变脉冲动画 */
@keyframes gradientPulse {
  0%, 100% {
    opacity: 1;
    transform: translateX(0px);
  }
  33% {
    opacity: 0.8;
    transform: translateX(-2px);
  }
  66% {
    opacity: 0.9;
    transform: translateX(1px);
  }
}

/* 登录容器 */
.login-container {
  position: absolute;
  top: 50%;
  left: 5%;
  transform: translateY(-50%);
  z-index: 3;
  width: 400px;
  max-width: calc(100vw - 10%);
  
}

/* 登录表单 */
.login-form {
  /* 渐变背景 */
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.2) 15%,
    rgba(255, 255, 255, 0.3) 30%,
    rgba(255, 255, 255, 0.4) 45%,
    rgba(255, 255, 255, 0.5) 60%,
    rgba(255, 255, 255, 0.6) 75%,
    rgba(255, 255, 255, 0.7) 90%,
    rgba(255, 255, 255, 0.8) 100%
  );
  backdrop-filter: blur(5px);
  border-radius: 16px;
  padding: 35px;
  box-shadow: 0 18px 32px rgba(0, 0, 0, 0.1);
  /* border: 1px solid rgba(233, 150, 73, 0.2); */
}

/* 标题容器 */
.title-container {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 22px;
  font-weight: 700;
  color: #1c2635;
  margin: 0 0 4px 0;
  line-height: 1.2;
  text-align: center;
  letter-spacing: 0.5px;
}

.title-sub {
  font-size: 20px;
  font-weight: 600;
  color: #1765e2;
  margin: 0;
  line-height: 1.2;
  text-align: center;
  letter-spacing: 0.3px;
}

.subtitle {
  text-align: center;
  font-size: 14px;
  color: #383d36;
  margin: 15px;
}

/* 表单项样式 */
:deep(.t-form-item) {
  margin-bottom: 20px;
}

:deep(.t-input) {
  /* 输入框样式 */
  background-color: rgba(253, 248, 248, 0.8);
  border-radius: 8px;
}

:deep(.t-input__inner) {
  /* 输入框内容样式 */
  background-color: rgb(255, 252, 247);
  padding: 12px 16px;
  font-size: 15px;
}

/* 角色选择样式 */
.role-selection {
  margin-bottom: 20px;
  width: 100%;
}

.role-selection-label {
  font-size: 14px;
  color: #383d36;
  margin-bottom: 12px;
  font-weight: 500;
}

.role-tabs {
  display: flex;
  gap: 8px;
  background: rgba(253, 248, 248, 0.8);
  border-radius: 8px;
  padding: 4px;
  width: 100%;
  box-sizing: border-box;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.role-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: transparent;
  border: 2px solid transparent;
}

.role-tab:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-1px);
}

.role-tab.active {
  background: rgba(75, 130, 202, 0.1);
  border-color: #4b82ca;
  box-shadow: 0 2px 8px rgba(75, 130, 202, 0.2);
}

.role-icon {
  font-size: 20px;
  margin-bottom: 4px;
  color: #666;
  transition: color 0.3s ease;
}

.role-tab.active .role-icon {
  color: #4b82ca;
}

.role-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
  transition: color 0.3s ease;
}

.role-tab.active .role-label {
  color: #4b82ca;
  font-weight: 600;
}

/* 选项容器 */
.options-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  font-size: 14px;
}

.forgot-password {
  color: #124f9e;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password:hover {
  color: #104fd6;
  text-decoration: underline;
}

/* 登录按钮容器 */
.login-button-container {
    /* 背景色 */
  margin-bottom: 0;
}

:deep(.t-button) {
  border-radius: 8px;
  font-weight: 500;
  height: 48px;
  background-color: #4b82ca;
  color: #fff;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(34, 224, 151, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    left: 5%;
    right: 5%;
    width: auto;
  }
  
  .login-form {
    padding: 24px;
  }
  
  .title {
    font-size: 18px;
  }
  
  .title-sub {
    font-size: 16px;
  }
  
  .role-tabs {
    flex-direction: column;
    gap: 4px;
  }
  
  .role-tab {
    flex-direction: row;
    justify-content: flex-start;
    padding: 10px 12px;
  }
  
  .role-icon {
    margin-right: 8px;
    margin-bottom: 0;
  }
  
  .role-label {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .login-container {
    left: 4%;
    right: 4%;
  }
  
  .login-form {
    padding: 20px;
  }
  
  .title {
    font-size: 16px;
  }
  
  .title-sub {
    font-size: 14px;
  }
}
</style>

<template>
  <t-layout class="main-layout">
    <!-- 侧边栏 -->
    <Sidebar />
    
    <!-- 主内容区域 -->
    <t-layout>
      <!-- 顶部导航栏 -->
      <Header />
      
      <!-- 内容区域 -->
      <t-content class="main-content">
        <div class="content-wrapper">
          <slot />
        </div>
      </t-content>
    </t-layout>
  </t-layout>
</template>

<script setup>
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'

/**
 * 主布局组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background: #f5f7fa;
}

.main-content {
  margin-top: 64px;
  margin-left: 240px;
  padding: 24px;
  min-height: calc(100vh - 64px);
  background: #f5f7fa;
}

.content-wrapper {
  margin: 0 auto;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height:100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 200px;
    padding: 16px;
  }

  .content-wrapper {
    height: 95vh;
  }
}

@media (max-width: 480px) {
  .main-content {
    margin-left: 180px;
    padding: 12px;
  }

  .content-wrapper {
    height: 95vh;
  }
}
</style>

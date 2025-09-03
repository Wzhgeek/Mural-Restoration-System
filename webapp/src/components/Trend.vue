<template>
  <span :class="containerCls">
    <span :class="iconCls">
      <svg
        v-if="type === 'down'"
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M11.5 8L8 11.5L4.5 8" stroke="currentColor" stroke-width="1.5" />
        <path d="M8 11L8 4" stroke="currentColor" stroke-width="1.5" />
      </svg>
      <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4.5 8L8 4.5L11.5 8" stroke="currentColor" stroke-width="1.5" />
        <path d="M8 5V12" stroke="currentColor" stroke-width="1.5" />
      </svg>
    </span>
    <span>{{ describe }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

/**
 * 趋势组件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const props = defineProps({
  type: {
    type: String,
    default: '',
  },
  describe: {
    type: [String, Number],
    default: undefined,
  },
  isReverseColor: {
    type: Boolean,
    default: false,
  },
})

const containerCls = computed(() => {
  return [
    'trend-container',
    {
      'trend-container__reverse': props.isReverseColor,
      'trend-container__up': !props.isReverseColor && props.type === 'up',
      'trend-container__down': !props.isReverseColor && props.type === 'down',
    },
  ]
})

const iconCls = computed(() => ['trend-icon-container'])
</script>

<style scoped>
.trend-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
}

.trend-container__up {
  color: #e34d59;
}

.trend-container__up .trend-icon-container {
  background: #fde2e2;
  color: #e34d59;
}

.trend-container__down {
  color: #00a870;
}

.trend-container__down .trend-icon-container {
  background: #d1fae5;
  color: #00a870;
}

.trend-container__reverse {
  color: #fff;
}

.trend-container__reverse .trend-icon-container {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.trend-icon-container {
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-right: 8px;
}
</style>

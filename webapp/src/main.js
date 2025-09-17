import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import TDesign from 'tdesign-vue-next'
import 'tdesign-vue-next/es/style/index.css'
import VueApexCharts from 'vue3-apexcharts'
import VueKonva from 'vue-konva'

/**
 * 应用入口文件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const app = createApp(App)
app.use(VueApexCharts)
app.use(router)
app.use(pinia)
app.use(TDesign)
app.use(VueKonva)
app.mount('#app')

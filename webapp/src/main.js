import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import TDesign from 'tdesign-vue-next'
import 'tdesign-vue-next/es/style/index.css'

/**
 * 应用入口文件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const app = createApp(App)
app.use(router)
app.use(TDesign)
app.mount('#app')

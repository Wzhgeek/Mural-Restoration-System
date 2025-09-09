import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

/**
 * Vite配置文件
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

// https://vite.dev/config/
export default defineConfig({
  base: '/', // 关键配置
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    // 构建输出目录
    outDir: 'dist',
    // 静态资源目录
    assetsDir: 'assets',
    // 清空输出目录
    emptyOutDir: true,
    // 添加 manifest 文件生成
    manifest: true
  },
  server: {
    proxy: {
      // 代理API请求到后端服务器
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false
      }
    }
  }
})

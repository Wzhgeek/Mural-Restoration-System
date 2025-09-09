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
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  // 配置构建选项，使用相对路径
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // 确保生成的文件使用相对路径
    rollupOptions: {
      output: {
        // 确保资源文件使用相对路径
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js'
      }
    }
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

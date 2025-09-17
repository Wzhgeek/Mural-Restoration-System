<template>
  <Layout>
    <div class="work-archive">
    <div class="left">
      <div class="left-header">文件浏览器</div>
      <div class="tree-container">
        <div
          v-for="item in allTreeItems"
          :key="item.key"
          class="tree-item"
          :class="{ 
            'tree-item--folder': item.type === 'folder',
            'tree-item--file': item.type === 'file',
            'tree-item--active': selectedFile && selectedFile.path === item.path
          }"
          :style="{ paddingLeft: (item.level * 16 + 8) + 'px' }"
          @click="handleItemClick(item)"
        >
          <div class="tree-item-content">
            <t-icon 
              :name="item.type === 'folder' ? (item.expanded ? 'chevron-down' : 'chevron-right') : getFileIcon(item.ext || '')"
              class="tree-item-icon"
            />
            <span class="tree-item-label">{{ item.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="right">
      <!-- 搜索和筛选区域 -->
      <div class="search-panel">
        <div class="search-header">
          <h3>搜索和筛选</h3>
        </div>
          <div class="search-controls">
            <div class="search-input">
              <t-input
                v-model="keyword"
                placeholder="输入关键词搜索文件..."
                clearable
                @change="searchFiles"
                @clear="resetSearch"
              >
                <template #prefix-icon>
                  <t-icon name="search" />
                </template>
              </t-input>
            </div>
            <div class="filter-controls">
              <t-select
                v-model="category"
                placeholder="选择文件类型"
                clearable
                @change="searchFiles"
                @clear="resetSearch"
              >
                <t-option
                  v-for="option in categoryOptions"
                  :key="option.value"
                  :value="option.value"
                  :label="option.label"
                />
              </t-select>
            </div>
            <div class="search-actions">
              <t-button 
                theme="primary" 
                variant="outline" 
                size="small"
                @click="searchFiles"
                :disabled="!keyword && !category"
              >
                搜索
              </t-button>
              <t-button 
                theme="default" 
                variant="outline" 
                size="small"
                @click="resetSearch"
                :disabled="!keyword && !category"
              >
                重置
              </t-button>
            </div>
          </div>
      </div>

      <!-- 预览区域 -->
      <div class="preview-panel">
        <template v-if="selectedFile">
          <div class="preview-header">
            <div class="title" :title="selectedFile.name">{{ selectedFile.name }}</div>
            <t-button size="small" variant="outline" :href="selectedFile.url" target="_blank">打开 / 下载</t-button>
          </div>
          <div class="preview-body">
            <img v-if="selectedFile.category === 'image'" :src="selectedFile.url" class="preview-img" />
            <div v-else class="preview-placeholder">
              暂不支持该类型的内联预览。请点击"打开/下载"查看。
            </div>
          </div>
        </template>
        <div v-else class="preview-empty">
          <div class="empty-state">
            <div class="empty-icon">
              <t-icon name="folder-open" size="48px" />
            </div>
            <div class="empty-title">未选择文件</div>
            <div class="empty-description">
              在左侧目录树中点击文件夹展开，点击文件查看预览
            </div>
            <div class="empty-tips">
              <div class="tip-item">
                <t-icon name="image" size="16px" />
                <span>图片文件支持内嵌预览</span>
              </div>
              <div class="tip-item">
                <t-icon name="download" size="16px" />
                <span>其他文件类型提供打开/下载</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue"
import Layout from '@/components/Layout.vue'

type FolderNode = { label: string; key: string; children?: FolderNode[] }
type FileItem = {
  name: string; path: string; ext: string; size: number; mtime: string;
  category: "image"|"video"|"document"|"code"|"other"; url: string
}
type FolderItem = {
  label: string
  key: string
  level: number
  expanded: boolean
  hasChildren: boolean
}

type TreeItem = {
  label: string
  key: string
  path: string
  type: 'folder' | 'file'
  level: number
  expanded?: boolean
  ext?: string
  fileData?: FileItem
}

const treeData = ref<FolderNode[]>([])
const folderItems = ref<FolderItem[]>([])
const allTreeItems = ref<TreeItem[]>([])
const files = ref<FileItem[]>([])
const selectedFile = ref<FileItem | null>(null)
const currentDir = ref<string>("")
const keyword = ref<string>("")
const category = ref<string | undefined>(undefined)

const categoryOptions = [
  { label: "全部", value: undefined as unknown as string },
  { label: "图片", value: "image" },
  { label: "视频", value: "video" },
  { label: "文档", value: "document" },
  { label: "代码", value: "code" },
  { label: "其他", value: "other" },
]

function catLabel(c: FileItem["category"]): string {
  switch (c) {
    case "image": return "图片"
    case "video": return "视频"
    case "document": return "文档"
    case "code": return "代码"
    default: return "其他"
  }
}

function prettySize(n: number): string {
  if (n < 1024) return `${n} B`
  if (n < 1024 ** 2) return `${(n/1024).toFixed(1)} KB`
  if (n < 1024 ** 3) return `${(n/1024/1024).toFixed(1)} MB`
  return `${(n/1024/1024/1024).toFixed(1)} GB`
}

function getFileIcon(ext: string): string {
  const e = ext.toLowerCase()
  if (e === '.js' || e === '.ts') return 'code'
  if (e === '.vue' || e === '.html') return 'code'
  if (e === '.css') return 'code'
  if (e === '.json' || e === '.yaml' || e === '.yml') return 'code'
  if (e === '.py') return 'code'
  if (e === '.png' || e === '.jpg' || e === '.jpeg' || e === '.gif' || e === '.webp' || e === '.svg') return 'image'
  if (e === '.mp4' || e === '.mov' || e === '.avi' || e === '.mkv') return 'video'
  if (e === '.pdf') return 'file'
  if (e === '.doc' || e === '.docx') return 'file'
  if (e === '.txt' || e === '.md') return 'file'
  return 'file'
}

async function fetchFolders() {
  try {
    const token = localStorage.getItem('authToken')
    const res = await fetch("/api/work-archive/folders", {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`)
    }
    
    const folders = await res.json()
    
    // 构建文件夹树形结构
    const items: FolderItem[] = []
    
    function processFolders(folderNodes: FolderNode[], level: number = 0) {
      for (const node of folderNodes) {
        items.push({
          label: node.label,
          key: node.key,
          level,
          expanded: false,
          hasChildren: !!(node.children && node.children.length > 0)
        })
        
        // 处理子文件夹
        if (node.children && node.children.length > 0) {
          processFolders(node.children, level + 1)
        }
      }
    }
    
    processFolders(folders)
    folderItems.value = items
    
    // 构建完整的树形结构（只显示文件夹）
    buildTreeItems()
  } catch (error) {
    console.error('获取文件夹失败:', error)
    // 显示错误提示
    alert('获取文件夹失败，请检查网络连接')
  }
}

function buildTreeItems() {
  const treeItems: TreeItem[] = []
  
  function processFolders(folderNodes: FolderNode[], level: number = 0) {
    for (const node of folderNodes) {
      treeItems.push({
        label: node.label,
        key: node.key,
        path: node.key,
        type: 'folder',
        level,
        expanded: false
      })
      
      // 处理子文件夹
      if (node.children && node.children.length > 0) {
        processFolders(node.children, level + 1)
      }
    }
  }
  
  // 获取文件夹数据
  const folders = folderItems.value.reduce((acc, item) => {
    if (item.level === 0) {
      acc.push({
        label: item.label,
        key: item.key,
        children: []
      })
    }
    return acc
  }, [] as FolderNode[])
  
  processFolders(folders)
  allTreeItems.value = treeItems
}


async function handleItemClick(item: TreeItem) {
  if (item.type === 'folder') {
    // 切换文件夹展开状态
    item.expanded = !item.expanded
    
    // 如果展开文件夹，加载该文件夹下的文件并添加到树中
    if (item.expanded) {
      await loadFolderFiles(item)
    } else {
      // 如果收起文件夹，移除该文件夹下的所有文件和子文件夹
      removeFolderChildren(item.key)
    }
  } else if (item.type === 'file' && item.fileData) {
    // 选择文件
    selectedFile.value = item.fileData
  }
}

async function loadFolderFiles(folderItem: TreeItem) {
  try {
    const token = localStorage.getItem('authToken')
    const params = new URLSearchParams()
    params.set("dir", folderItem.key)
    
    const res = await fetch(`/api/work-archive/files?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`)
    }
    
    const files = await res.json()
    
    // 找到当前文件夹在树中的位置
    const folderIndex = allTreeItems.value.findIndex(item => item.key === folderItem.key)
    if (folderIndex === -1) return
    
    // 在该文件夹后插入文件和子文件夹
    const newItems: TreeItem[] = []
    
    // 收集子文件夹
    const subfolders = new Set<string>()
    for (const file of files) {
      const pathParts = file.path.split('/')
      const folderPath = folderItem.key
      const relativePath = file.path.replace(folderPath + '/', '')
      const relativeParts = relativePath.split('/')
      
      // 如果有子目录，添加子文件夹
      if (relativeParts.length > 1) {
        const subfolderName = relativeParts[0]
        const subfolderPath = `${folderPath}/${subfolderName}`
        
        if (!subfolders.has(subfolderPath)) {
          subfolders.add(subfolderPath)
          newItems.push({
            label: subfolderName,
            key: subfolderPath,
            path: subfolderPath,
            type: 'folder',
            level: folderItem.level + 1,
            expanded: false
          })
        }
      } else {
        // 直接在当前目录下的文件
        newItems.push({
          label: file.name,
          key: file.path,
          path: file.path,
          type: 'file',
          level: folderItem.level + 1,
          ext: file.ext,
          fileData: file
        })
      }
    }
    
    // 插入文件和子文件夹到树中
    allTreeItems.value.splice(folderIndex + 1, 0, ...newItems)
  } catch (error) {
    console.error('加载文件夹文件失败:', error)
    alert('加载文件夹文件失败，请检查网络连接')
  }
}

function removeFolderChildren(folderKey: string) {
  // 找到文件夹的位置
  const folderIndex = allTreeItems.value.findIndex(item => item.key === folderKey)
  if (folderIndex === -1) return
  
  // 移除该文件夹下的所有子项（文件和子文件夹）
  const itemsToRemove: number[] = []
  for (let i = folderIndex + 1; i < allTreeItems.value.length; i++) {
    const item = allTreeItems.value[i]
    if (item.level <= allTreeItems.value[folderIndex].level) {
      break // 遇到同级或上级项目，停止
    }
    itemsToRemove.push(i)
  }
  
  // 从后往前删除，避免索引变化
  for (let i = itemsToRemove.length - 1; i >= 0; i--) {
    allTreeItems.value.splice(itemsToRemove[i], 1)
  }
}

async function searchFiles() {
  try {
    const token = localStorage.getItem('authToken')
    const params = new URLSearchParams()
    
    if (keyword.value) {
      params.set("keyword", keyword.value)
    }
    
    if (category.value) {
      // 将前端分类映射到后端文件类型
      const typeMapping: { [key: string]: string } = {
        'image': 'jpg,png,jpeg,gif,webp,svg,tif,tiff',
        'video': 'mp4,mov,avi,mkv,webm,m4v',
        'document': 'pdf,doc,docx,txt,md,caj',
        'code': 'js,ts,vue,html,css,json,yaml,yml,py'
      }
      
      if (typeMapping[category.value]) {
        params.set("file_type", typeMapping[category.value])
      }
    }
    
    const res = await fetch(`/api/work-archive/files?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`)
    }
    
    const files = await res.json()
    
    // 清空当前树结构，只显示搜索结果
    allTreeItems.value = []
    
    // 将搜索结果添加到树中
    const searchItems: TreeItem[] = []
    for (const file of files) {
      searchItems.push({
        label: file.name,
        key: file.path,
        path: file.path,
        type: 'file',
        level: 0,
        ext: file.ext,
        fileData: file
      })
    }
    
    allTreeItems.value = searchItems
    
    console.log('搜索完成，找到', files.length, '个文件')
  } catch (error) {
    console.error('搜索文件失败:', error)
    alert('搜索文件失败，请检查网络连接')
  }
}

async function resetSearch() {
  // 清空搜索条件
  keyword.value = ""
  category.value = undefined
  
  // 重新加载文件夹结构
  await fetchFolders()
  
  // 清空选中的文件
  selectedFile.value = null
}


onMounted(async () => {
  await fetchFolders()
})
</script>

<style scoped>
.work-archive {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 16px;
  height: calc(100vh - 200px);
  padding: 12px;
  box-sizing: border-box;
}

.left {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  background: #fff;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.left-header {
  padding: 8px 12px;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 1px solid #d9d9d9;
  background: #f5f5f5;
  color: #333;
}

.tree-container {
  padding: 4px 0;
  overflow: auto;
  flex: 1;
  background: #fff;
}

.tree-item {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.1s ease;
}

.tree-item:hover {
  background-color: #f0f0f0;
}

.tree-item--active {
  background-color: #e6f7ff !important;
  color: #1890ff;
}

.tree-item-content {
  display: flex;
  align-items: center;
  padding: 2px 8px;
  height: 24px;
  font-size: 13px;
}

.tree-item-icon {
  margin-right: 4px;
  font-size: 12px;
  color: #666;
  width: 12px;
  text-align: center;
}

.tree-item--active .tree-item-icon {
  color: #1890ff;
}

.tree-item-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tree-item--folder .tree-item-label {
  font-weight: 500;
}

.tree-item--file .tree-item-label {
  font-weight: normal;
}

.right {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-panel {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  background: #fff;
  padding: 16px;
}

.search-header {
  margin-bottom: 12px;
}

.search-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.search-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  flex: 1;
}

.filter-controls {
  min-width: 150px;
}

.search-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.preview-panel {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  background: #fff;
  padding: 16px;
  overflow: auto;
  flex: 1;
}

.preview-header {
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.preview-header .title {
  font-weight: 600; 
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
  max-width: 70%;
  font-size: 16px;
  color: #333;
}

.preview-body { 
  height: calc(100% - 60px); 
}

.preview-img { 
  max-width: 100%; 
  max-height: 100%; 
  object-fit: contain; 
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.preview-placeholder {
  height: 100%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  text-align: center; 
  padding: 20px;
  color: #999;
  background: #fafafa;
  border-radius: 6px;
  border: 1px dashed #d9d9d9;
}

.preview-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 2px dashed #cbd5e1;
  position: relative;
  overflow: hidden;
}

.preview-empty::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.05) 0%, transparent 70%);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(-20px, -20px) rotate(180deg); }
}

.empty-state {
  text-align: center;
  position: relative;
  z-index: 1;
  max-width: 400px;
}

.empty-icon {
  margin-bottom: 24px;
  color: #3b82f6;
  opacity: 0.8;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
  letter-spacing: -0.025em;
}

.empty-description {
  font-size: 15px;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 24px;
}

.empty-tips {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  border: 1px solid rgba(203, 213, 225, 0.5);
  font-size: 13px;
  color: #475569;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

.tip-item:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.tip-item .t-icon {
  color: #3b82f6;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-empty {
    padding: 30px 16px;
    border-radius: 8px;
  }
  
  .empty-icon {
    margin-bottom: 20px;
  }
  
  .empty-title {
    font-size: 18px;
    margin-bottom: 10px;
  }
  
  .empty-description {
    font-size: 14px;
    margin-bottom: 20px;
  }
  
  .empty-tips {
    gap: 10px;
  }
  
  .tip-item {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>

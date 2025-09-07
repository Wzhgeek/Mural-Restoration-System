<template>
  <div class="image-edit-page">
    <div class="page-header">
      <h3>图片编辑与标注</h3>
      <p>对壁画图片进行标注、编辑处理（可选步骤）</p>
    </div>
    
    <div class="edit-container">
      <!-- 工具栏 -->
      <div class="toolbar" v-if="hasImage">
        <div class="tool-group">
          <h4>绘制工具</h4>
          <t-button-group>
            <t-button 
              :theme="currentTool === 'select' ? 'primary' : 'default'"
              @click="setTool('select')"
              size="small"
            >
              <template #icon><t-icon name="cursor" /></template>
              选择
            </t-button>
            <t-button 
              :theme="currentTool === 'draw' ? 'primary' : 'default'"
              @click="setTool('draw')"
              size="small"
            >
              <template #icon><t-icon name="edit" /></template>
              画笔
            </t-button>
            <t-button 
              :theme="currentTool === 'text' ? 'primary' : 'default'"
              @click="setTool('text')"
              size="small"
            >
              <template #icon><t-icon name="text-format" /></template>
              文字
            </t-button>
            <t-button 
              :theme="currentTool === 'shape' ? 'primary' : 'default'"
              @click="setTool('shape')"
              size="small"
            >
              <template #icon><t-icon name="rectangle" /></template>
              形状
            </t-button>
          </t-button-group>
        </div>
        
        <div class="tool-group">
          <h4>画笔设置</h4>
          <div class="brush-controls">
            <label>颜色:</label>
            <input type="color" v-model="brushColor" @change="updateBrushColor" />
            <label>粗细:</label>
            <t-slider 
              v-model="brushWidth" 
              :min="1" 
              :max="20" 
              @change="updateBrushWidth"
              style="width: 100px;"
            />
          </div>
        </div>
        
        <div class="tool-group">
          <h4>操作</h4>
          <t-button-group>
            <t-button @click="undo" size="small" :disabled="!canUndo">
              <template #icon><t-icon name="rollback" /></template>
              撤销
            </t-button>
            <t-button @click="redo" size="small" :disabled="!canRedo">
              <template #icon><t-icon name="rollfront" /></template>
              重做
            </t-button>
            <t-button @click="clearCanvas" size="small" theme="warning">
              <template #icon><t-icon name="delete" /></template>
              清除
            </t-button>
          </t-button-group>
        </div>
        
        <div class="tool-group">
          <h4>保存</h4>
          <t-button @click="saveEditedImage" theme="primary" size="small">
            <template #icon><t-icon name="save" /></template>
            保存编辑
          </t-button>
        </div>
      </div>
      
      <!-- 编辑区域 -->
      <div class="edit-area">
        <div v-if="!hasImage" class="no-image-placeholder">
          <t-icon name="image" size="64px" />
          <p>未上传图片，可直接进入下一步</p>
          <t-button @click="goToNextStep" theme="primary">
            跳过编辑，继续下一步
          </t-button>
        </div>
        
        <div v-else class="canvas-container">
          <canvas 
            ref="fabricCanvasRef"
            :width="canvasWidth"
            :height="canvasHeight"
            class="fabric-canvas"
          />
        </div>
      </div>
      
      <!-- 编辑状态 -->
      <div class="edit-status" v-if="hasImage">
        <div class="status-info">
          <t-icon name="info-circle" />
          <span v-if="hasChanges">已进行编辑，记得保存修改</span>
          <span v-else>未进行任何编辑</span>
        </div>
        
        <div class="canvas-info">
          画布尺寸: {{ canvasWidth }} × {{ canvasHeight }}px
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { useRouter } from 'vue-router'
import { useRestorationFlowStore } from '@/stores/restorationFlow'

/**
 * 图片编辑页面
 * @author 王梓涵
 * @email wangzh011031@163.com
 * @date 2025
 */

const store = useRestorationFlowStore()
const router = useRouter()

const fabricCanvasRef = ref(null)
const canvas = ref(null)
const currentTool = ref('select')
const brushColor = ref('#ff0000')
const brushWidth = ref(3)
const canvasWidth = ref(800)
const canvasHeight = ref(600)
const hasChanges = ref(false)
const canUndo = ref(false)
const canRedo = ref(false)

// 历史记录管理
const history = ref([])
const historyIndex = ref(-1)

// 计算属性
const hasImage = computed(() => {
  const imageFile = store.formData.image_file
  console.log('检查图片文件:', imageFile)
  return !!(imageFile && (
    imageFile instanceof File ||
    typeof imageFile === 'string' ||
    (imageFile && imageFile.raw) ||
    (imageFile && imageFile.url)
  )) || store.imageEditData.originalImage
})

// 设置工具
const setTool = (tool) => {
  currentTool.value = tool
  if (!canvas.value) return
  
  switch (tool) {
    case 'select':
      canvas.value.isDrawingMode = false
      canvas.value.selection = true
      break
    case 'draw':
      canvas.value.isDrawingMode = true
      canvas.value.selection = false
      // 确保画笔设置正确
      if (canvas.value.freeDrawingBrush) {
        canvas.value.freeDrawingBrush.color = brushColor.value
        canvas.value.freeDrawingBrush.width = brushWidth.value
      }
      break
    case 'text':
      canvas.value.isDrawingMode = false
      canvas.value.selection = true
      addText()
      break
    case 'shape':
      canvas.value.isDrawingMode = false
      canvas.value.selection = true
      addRectangle()
      break
  }
}

// 更新画笔颜色
const updateBrushColor = () => {
  if (canvas.value && canvas.value.freeDrawingBrush) {
    canvas.value.freeDrawingBrush.color = brushColor.value
  }
}

// 更新画笔粗细
const updateBrushWidth = () => {
  if (canvas.value && canvas.value.freeDrawingBrush) {
    canvas.value.freeDrawingBrush.width = brushWidth.value
  }
}

// 添加文字
const addText = () => {
  if (!canvas.value || !window.fabricClasses) return
  
  const text = new window.fabricClasses.IText('双击编辑文字', {
    left: canvasWidth.value / 2,
    top: canvasHeight.value / 2,
    fontFamily: 'Arial',
    fontSize: 20,
    fill: brushColor.value,
    textAlign: 'center',
    originX: 'center',
    originY: 'center'
  })
  
  canvas.value.add(text)
  canvas.value.setActiveObject(text)
  text.enterEditing()
}

// 添加矩形
const addRectangle = () => {
  if (!canvas.value || !window.fabricClasses) return
  
  const rect = new window.fabricClasses.Rect({
    left: canvasWidth.value / 2 - 50,
    top: canvasHeight.value / 2 - 25,
    width: 100,
    height: 50,
    fill: 'transparent',
    stroke: brushColor.value,
    strokeWidth: 2,
    selectable: true
  })
  
  canvas.value.add(rect)
  canvas.value.setActiveObject(rect)
}

// 撤销
const undo = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--
    const state = history.value[historyIndex.value]
    canvas.value.loadFromJSON(state, () => {
      canvas.value.renderAll()
      updateUndoRedoState()
    })
  }
}

// 重做
const redo = () => {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    const state = history.value[historyIndex.value]
    canvas.value.loadFromJSON(state, () => {
      canvas.value.renderAll()
      updateUndoRedoState()
    })
  }
}

// 清除画布
const clearCanvas = () => {
  if (!canvas.value) return
  
  const objects = canvas.value.getObjects()
  // 只清除绘制的对象，保留背景图片
  objects.forEach(obj => {
    if (obj.type !== 'image' || !obj.isBackground) {
      canvas.value.remove(obj)
    }
  })
  
  saveCanvasState()
}

// 保存画布状态到历史记录
const saveCanvasState = () => {
  if (!canvas.value) return
  
  const state = JSON.stringify(canvas.value.toJSON())
  
  // 清除当前位置之后的历史记录
  history.value = history.value.slice(0, historyIndex.value + 1)
  
  // 添加新状态
  history.value.push(state)
  historyIndex.value = history.value.length - 1
  
  // 限制历史记录数量
  if (history.value.length > 20) {
    history.value.shift()
    historyIndex.value--
  }
  
  updateUndoRedoState()
  hasChanges.value = true
}

// 更新撤销重做状态
const updateUndoRedoState = () => {
  canUndo.value = historyIndex.value > 0
  canRedo.value = historyIndex.value < history.value.length - 1
}

// 保存编辑后的图片
const saveEditedImage = () => {
  if (!canvas.value) return
  
  try {
    // 导出为数据URL
    const dataURL = canvas.value.toDataURL({
      format: 'png',
      quality: 0.9
    })
    
    // 保存到store
    store.saveImageEdit({
      editedImage: dataURL,
      fabricData: JSON.stringify(canvas.value.toJSON()),
      hasEdited: true
    })
    
    MessagePlugin.success('图片编辑已保存')
    hasChanges.value = false
  } catch (error) {
    console.error('保存编辑失败:', error)
    MessagePlugin.error('保存编辑失败: ' + error.message)
  }
}

// 初始化 Fabric.js 画布
const initFabricCanvas = async () => {
  if (!fabricCanvasRef.value) return
  
  try {
    // 动态导入 fabric.js
    const { Canvas, Image, IText, Rect } = await import('fabric')
    
    // 创建 Fabric 画布
    canvas.value = new Canvas(fabricCanvasRef.value, {
      width: canvasWidth.value,
      height: canvasHeight.value,
      backgroundColor: '#ffffff'
    })
    
    // 将 fabric 实例保存到 canvas 元素上，供外部访问
    fabricCanvasRef.value.fabric = canvas.value
    
    // 保存 fabric 类到全局，供其他方法使用
    window.fabricClasses = { Canvas, Image, IText, Rect }
    
    // 设置画布属性
    canvas.value.isDrawingMode = false
    
    // 设置绘制画笔属性（需要先检查是否存在）
    if (canvas.value.freeDrawingBrush) {
      canvas.value.freeDrawingBrush.color = brushColor.value
      canvas.value.freeDrawingBrush.width = brushWidth.value
    }
    
    // 监听画布事件
    canvas.value.on('path:created', saveCanvasState)
    canvas.value.on('object:added', saveCanvasState)
    canvas.value.on('object:removed', saveCanvasState)
    canvas.value.on('object:modified', saveCanvasState)
    
    // 加载图片和之前的编辑数据
    loadImageToCanvas()
    
    console.log('Fabric 画布初始化成功')
  } catch (error) {
    console.error('初始化 Fabric 画布失败:', error)
    MessagePlugin.error('图片编辑功能初始化失败，将跳过此步骤')
  }
}

// 加载图片到画布
const loadImageToCanvas = () => {
  if (!canvas.value || !window.fabricClasses) {
    console.log('画布或fabric类未初始化')
    return
  }
  
  // 清空画布中的现有内容
  canvas.value.clear()
  
  let imageUrl = null
  
  // 优先使用表单页面上传的原始图片，而不是之前编辑的图片
  if (store.formData.image_file) {
    // 处理不同类型的图片文件数据
    const imageFile = store.formData.image_file
    console.log('处理图片文件:', imageFile)
    
    if (imageFile instanceof File) {
      // 直接是File对象
      imageUrl = URL.createObjectURL(imageFile)
      console.log('File对象，创建URL:', imageUrl)
    } else if (typeof imageFile === 'string') {
      // 是URL字符串
      imageUrl = imageFile
      console.log('URL字符串:', imageUrl)
    } else if (imageFile && imageFile.raw) {
      // 是TDesign上传组件的文件对象
      imageUrl = URL.createObjectURL(imageFile.raw)
      console.log('TDesign文件对象，创建URL:', imageUrl)
    } else if (imageFile && imageFile.url) {
      // 有url属性
      imageUrl = imageFile.url
      console.log('带url属性的对象:', imageUrl)
    } else {
      console.warn('无法识别的图片文件格式:', imageFile)
      MessagePlugin.warning('图片格式不支持，请重新上传')
      return
    }
  } else if (store.imageEditData.editedImage) {
    // 如果没有新上传的图片，使用已编辑的图片
    imageUrl = store.imageEditData.editedImage
    console.log('使用已编辑的图片:', imageUrl)
  }
  
  if (!imageUrl) {
    console.log('没有找到图片文件')
    return
  }
  
  console.log('正在加载图片到画布:', imageUrl)
  
  window.fabricClasses.Image.fromURL(imageUrl).then((img) => {
    // 计算缩放比例以适应画布
    const scaleX = canvasWidth.value / img.width
    const scaleY = canvasHeight.value / img.height
    const scale = Math.min(scaleX, scaleY, 1) // 不放大，只缩小
    
    // 更新画布尺寸以匹配图片
    const newWidth = img.width * scale
    const newHeight = img.height * scale
    
    canvasWidth.value = newWidth
    canvasHeight.value = newHeight
    
    canvas.value.setDimensions({
      width: newWidth,
      height: newHeight
    })
    
    // 设置图片属性
    img.set({
      left: 0,
      top: 0,
      scaleX: scale,
      scaleY: scale,
      selectable: false,
      evented: false,
      isBackground: true
    })
    
    // 添加图片作为背景
    canvas.value.add(img)
    // 将图片移到最底层（Fabric.js 5+ 使用 moveTo）
    if (canvas.value.moveTo) {
      canvas.value.moveTo(img, 0)
    } else if (canvas.value.sendToBack) {
      canvas.value.sendToBack(img)
    }
    
    // 如果有之前的编辑数据，恢复它
    if (store.imageEditData.fabricData) {
      try {
        const fabricData = JSON.parse(store.imageEditData.fabricData)
        canvas.value.loadFromJSON(fabricData).then(() => {
          canvas.value.renderAll()
        })
      } catch (error) {
        console.error('恢复编辑数据失败:', error)
      }
    }
    
    // 保存初始状态
    nextTick(() => {
      saveCanvasState()
    })
  }).catch(error => {
    console.error('加载图片失败:', error)
    MessagePlugin.error('加载图片失败: ' + error.message)
  })
}

// 跳转到下一步
const goToNextStep = () => {
  // 自动保存当前的图片编辑内容
  if (canvas.value) {
    try {
      // 导出为数据URL
      const dataURL = canvas.value.toDataURL({
        format: 'png',
        quality: 0.9
      })
      
      // 保存到store
      store.saveImageEdit({
        editedImage: dataURL,
        fabricData: JSON.stringify(canvas.value.toJSON()),
        hasEdited: true
      })
      
      console.log('自动保存图片编辑内容')
    } catch (error) {
      console.error('自动保存编辑失败:', error)
      MessagePlugin.warning('保存编辑内容时出现错误，但将继续下一步')
    }
  }
  
  // 跳转到下一步
  if (store.nextStep()) {
    router.push(`/restoration-flow/${store.workflowId}/confirm`)
  }
}

onMounted(() => {
  console.log('图片编辑页面初始化，hasImage:', hasImage.value)
  console.log('store.formData.image_file:', store.formData.image_file)
  
  // 如果没有图片，显示占位符
  if (!hasImage.value) {
    MessagePlugin.info('未检测到上传的图片，可跳过编辑步骤')
  } else {
    // 等待 DOM 更新后初始化画布
    nextTick(() => {
      initFabricCanvas()
    })
  }
})

// 监听 store 中图片文件的变化
watch(
  () => store.formData.image_file,
  (newImageFile, oldImageFile) => {
    console.log('检测到图片文件变化:', { newImageFile, oldImageFile })
    
    // 如果画布已初始化且图片文件发生变化，重新加载图片
    if (canvas.value && newImageFile && newImageFile !== oldImageFile) {
      console.log('重新加载新图片到画布')
      loadImageToCanvas()
    }
  },
  { deep: true }
)

onUnmounted(() => {
  // 清理画布
  if (canvas.value) {
    canvas.value.dispose()
  }
  
  // 清理全局变量
  if (window.fabricClasses) {
    delete window.fabricClasses
  }
})
</script>

<style scoped>
.image-edit-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-header p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.edit-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e5e7eb;
}

.tool-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-group h4 {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.brush-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.brush-controls input[type="color"] {
  width: 32px;
  height: 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.brush-controls label {
  color: #6b7280;
  font-size: 12px;
}

.edit-area {
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
}

.no-image-placeholder {
  text-align: center;
  color: #6b7280;
}

.no-image-placeholder p {
  margin: 16px 0;
  font-size: 16px;
}

.canvas-container {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.fabric-canvas {
  border: 1px solid #ddd;
  cursor: crosshair;
}

.edit-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-top: 1px solid #e5e7eb;
  font-size: 14px;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
}

.canvas-info {
  color: #9ca3af;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 16px;
  }
  
  .tool-group {
    align-items: flex-start;
  }
  
  .edit-status {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .canvas-container {
    width: 100%;
    overflow-x: auto;
  }
}
</style>


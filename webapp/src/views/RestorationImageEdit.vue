<template>
  <div class="image-edit-page">
    <div class="page-header">
      <h3>图片编辑与标注</h3>
      <p>对壁画图片进行标注、编辑处理（可选步骤）</p>
    </div>
    
    <div class="edit-container">
      <!-- 编辑区域 -->
      <div class="edit-area">
        <div v-if="!hasImage" class="no-image-placeholder">
          <t-icon name="image" size="64px" />
          <p>未上传图片，可直接进入下一步</p>
          <t-button @click="goToNextStep" theme="primary">
            跳过编辑，继续下一步
          </t-button>
        </div>
        
        <div v-else class="edit-workspace">
          <!-- 左侧工具栏 -->
          <div class="left-toolbar">
            <!-- 基础工具 -->
            <div class="tool-section">
              <h4>基础工具</h4>
              <div class="tool-buttons">
                <t-button 
                  :theme="currentTool === 'select' ? 'primary' : 'default'"
                  @click="setTool('select')"
                  size="small"
                  title="选择工具 (S)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="cursor" /></template>
                  选择
                </t-button>
                <t-button 
                  :theme="currentTool === 'draw' ? 'primary' : 'default'"
                  @click="setTool('draw')"
                  size="small"
                  title="自由绘制 (D)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="edit" /></template>
                  画笔
                </t-button>
                <t-button 
                  :theme="currentTool === 'highlighter' ? 'primary' : 'default'"
                  @click="setTool('highlighter')"
                  size="small"
                  title="荧光笔 (H)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="highlight" /></template>
                  荧光笔
                </t-button>
              </div>
            </div>
            
            <!-- 形状工具 -->
            <div class="tool-section">
              <h4>形状工具</h4>
              <div class="tool-buttons">
                <t-button 
                  :theme="currentTool === 'rectangle' ? 'primary' : 'default'"
                  @click="setTool('rectangle')"
                  size="small"
                  title="矩形 (R)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="rectangle" /></template>
                  矩形
                </t-button>
                <t-button 
                  :theme="currentTool === 'circle' ? 'primary' : 'default'"
                  @click="setTool('circle')"
                  size="small"
                  title="圆形 (C)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="circle" /></template>
                  圆形
                </t-button>
                <t-button 
                  :theme="currentTool === 'ellipse' ? 'primary' : 'default'"
                  @click="setTool('ellipse')"
                  size="small"
                  title="椭圆 (O)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="ellipsis" /></template>
                  椭圆
                </t-button>
                <t-button 
                  :theme="currentTool === 'line' ? 'primary' : 'default'"
                  @click="setTool('line')"
                  size="small"
                  title="直线 (L)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="minus" /></template>
                  直线
                </t-button>
              </div>
            </div>
            
            <!-- 标注工具 -->
            <div class="tool-section">
              <h4>标注工具</h4>
              <div class="tool-buttons">
                <t-button 
                  :theme="currentTool === 'arrow' ? 'primary' : 'default'"
                  @click="setTool('arrow')"
                  size="small"
                  title="箭头 (A)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="arrow-right" /></template>
                  箭头
                </t-button>
                <t-button 
                  :theme="currentTool === 'text' ? 'primary' : 'default'"
                  @click="setTool('text')"
                  size="small"
                  title="文字 (T)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="text-format" /></template>
                  文字
                </t-button>
                <t-button 
                  :theme="currentTool === 'polygon' ? 'primary' : 'default'"
                  @click="setTool('polygon')"
                  size="small"
                  title="多边形 (P)"
                  class="tool-button"
                >
                  <template #icon><t-icon name="polygon" /></template>
                  多边形
                </t-button>
              </div>
            </div>
            
            <!-- 测量工具 -->
            <div class="tool-section">
              <h4>测量工具</h4>
              <div class="tool-buttons">
                <t-button 
                  :theme="currentTool === 'ruler' ? 'primary' : 'default'"
                  @click="setTool('ruler')"
                  size="small"
                  title="距离测量"
                  class="tool-button"
                >
                  <template #icon><t-icon name="ruler" /></template>
                  测距
                </t-button>
                <t-button 
                  :theme="currentTool === 'protractor' ? 'primary' : 'default'"
                  @click="setTool('protractor')"
                  size="small"
                  title="角度测量"
                  class="tool-button"
                >
                  <template #icon><t-icon name="compass" /></template>
                  测角
                </t-button>
              </div>
            </div>
            
            <!-- 画笔设置 -->
            <div class="tool-section">
              <h4>画笔设置</h4>
              <div class="brush-controls">
                <div class="control-item">
                  <label>颜色:</label>
                  <input type="color" v-model="brushColor" @change="updateBrushColor" />
                </div>
                <div class="control-item">
                  <label>粗细:</label>
                  <t-slider 
                    v-model="brushWidth" 
                    :min="1" 
                    :max="20" 
                    @change="updateBrushWidth"
                  />
                </div>
              </div>
            </div>
            
            <!-- 操作工具 -->
            <div class="tool-section">
              <h4>操作</h4>
              <div class="tool-buttons">
                <t-button @click="undo" size="small" :disabled="!canUndo" class="tool-button">
                  <template #icon><t-icon name="rollback" /></template>
                  撤销
                </t-button>
                <t-button @click="redo" size="small" :disabled="!canRedo" class="tool-button">
                  <template #icon><t-icon name="rollfront" /></template>
                  重做
                </t-button>
                <t-button @click="clearCanvas" size="small" theme="warning" class="tool-button">
                  <template #icon><t-icon name="delete" /></template>
                  清除
                </t-button>
              </div>
            </div>
            
            <!-- 保存工具 -->
            <div class="tool-section">
              <h4>保存</h4>
              <div class="tool-buttons">
                <t-button @click="saveEditedImage" theme="primary" size="small" class="tool-button">
                  <template #icon><t-icon name="save" /></template>
                  保存编辑
                </t-button>
              </div>
            </div>
            
            <!-- 视图控制 -->
            <div class="tool-section">
              <h4>视图</h4>
              <div class="tool-buttons">
                <t-button 
                  :theme="showLayerPanel ? 'primary' : 'default'"
                  @click="toggleLayerPanel"
                  size="small"
                  title="图层面板"
                  class="tool-button"
                >
                  <template #icon><t-icon name="layers" /></template>
                  图层
                </t-button>
                <t-button 
                  :theme="showPropertiesPanel ? 'primary' : 'default'"
                  @click="togglePropertiesPanel"
                  size="small"
                  title="属性面板"
                  class="tool-button"
                >
                  <template #icon><t-icon name="setting" /></template>
                  属性
                </t-button>
              </div>
            </div>
          </div>
          
          <!-- 中间画布区域 -->
          <div class="canvas-area">
            <div class="canvas-container">
              <canvas 
                ref="fabricCanvasRef"
                :width="canvasWidth"
                :height="canvasHeight"
                class="fabric-canvas"
              />
            </div>
          </div>
          
          <!-- 右侧面板区域 -->
          <div class="right-panels">
            <!-- 图层面板 -->
            <div class="panel-container" v-if="showLayerPanel">
              <div class="layer-panel">
                <div class="panel-header">
                  <h4>图层管理</h4>
                  <t-button size="small" @click="addNewLayer" title="新建图层">
                    <template #icon><t-icon name="add" /></template>
                  </t-button>
                </div>
                
                <div class="layer-list">
                  <div 
                    v-for="(layer, index) in layers" 
                    :key="layer.id"
                    :class="['layer-item', { active: layer.id === activeLayerId, dragging: dragState.isDragging && dragState.dragIndex === index }]"
                    :data-layer-id="layer.id"
                    @click="selectLayer(layer.id)"
                    @mousedown="layer.id !== 'background' ? startDrag($event, index) : null"
                    @dragover.prevent
                    @drop="onDrop($event, index)"
                    @contextmenu="showLayerContextMenu($event, layer)"
                    :draggable="layer.id !== 'background'"
                    @dragstart="layer.id !== 'background' ? onDragStart($event, index) : null"
                    @dragend="onDragEnd"
                  >
                    <div class="layer-controls">
                      <t-checkbox 
                        v-model="layer.visible"
                        @change="toggleLayerVisibility(layer.id)"
                        :disabled="layer.id === 'background'"
                        size="small"
                        :title="layer.id === 'background' ? '背景图层始终显示' : '显示/隐藏'"
                      />
                      <t-button 
                        size="small"
                        :theme="layer.locked ? 'warning' : 'default'"
                        @click="toggleLayerLock(layer.id)"
                        :title="layer.locked ? '解锁' : '锁定'"
                      >
                        <t-icon :name="layer.locked ? 'lock' : 'lock-off'" size="14px" />
                      </t-button>
                    </div>
                    
                    <div class="layer-info">
                      <input 
                        v-model="layer.name"
                        class="layer-name"
                        @blur="updateLayerName(layer.id, layer.name)"
                        @keyup.enter="$event.target.blur()"
                      />
                      <div class="layer-opacity">
                        <span class="opacity-label">透明度:</span>
                        <t-slider 
                          v-model="layer.opacity"
                          :min="0"
                          :max="100"
                          @change="updateLayerOpacity(layer.id, layer.opacity)"
                          size="small"
                        />
                        <span class="opacity-value">{{ layer.opacity }}%</span>
                      </div>
                    </div>
                    
                    <t-button 
                      size="small"
                      theme="danger"
                      @click="deleteLayer(layer.id)"
                      title="删除图层"
                      v-if="layer.id !== 'background'"
                    >
                      <t-icon name="delete" size="14px" />
                    </t-button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 属性面板 -->
            <div class="panel-container" v-if="showPropertiesPanel">
              <div class="properties-panel">
                <div class="panel-header">
                  <h4>属性设置</h4>
                </div>
                
                <div class="properties-content" v-if="selectedObject">
                  <!-- 通用属性 -->
                  <t-collapse v-model="activePropertyPanel">
                    <t-collapse-panel header="基础属性" value="basic">
                      <div class="property-group">
                        <div class="property-item">
                          <label>颜色:</label>
                          <input 
                            type="color" 
                            v-model="objectProperties.color" 
                            @change="updateObjectProperty('color', objectProperties.color)"
                          />
                        </div>
                        
                        <div class="property-item">
                          <label>透明度:</label>
                          <t-slider 
                            v-model="objectProperties.opacity"
                            :min="0" 
                            :max="100" 
                            @change="updateObjectProperty('opacity', objectProperties.opacity / 100)"
                          />
                          <span class="property-value">{{ objectProperties.opacity }}%</span>
                        </div>
                        
                        <div class="property-item" v-if="selectedObject.type !== 'text'">
                          <label>线条粗细:</label>
                          <t-input-number 
                            v-model="objectProperties.strokeWidth" 
                            :min="1" 
                            :max="50" 
                            @change="updateObjectProperty('strokeWidth', objectProperties.strokeWidth)"
                          />
                        </div>
                      </div>
                    </t-collapse-panel>
                    
                    <!-- 文字属性 -->
                    <t-collapse-panel header="文字属性" value="text" v-if="selectedObject?.type === 'text' || selectedObject?.type === 'i-text'">
                      <div class="property-group">
                        <div class="property-item">
                          <label>字体:</label>
                          <t-select 
                            v-model="objectProperties.fontFamily" 
                            :options="fontOptions"
                            @change="updateObjectProperty('fontFamily', objectProperties.fontFamily)"
                          />
                        </div>
                        
                        <div class="property-item">
                          <label>字号:</label>
                          <t-input-number 
                            v-model="objectProperties.fontSize" 
                            :min="8" 
                            :max="72" 
                            @change="updateObjectProperty('fontSize', objectProperties.fontSize)"
                          />
                        </div>
                        
                        <div class="property-item">
                          <label>字体样式:</label>
                          <t-checkbox-group v-model="objectProperties.fontStyles" @change="updateFontStyles">
                            <t-checkbox value="bold">粗体</t-checkbox>
                            <t-checkbox value="italic">斜体</t-checkbox>
                            <t-checkbox value="underline">下划线</t-checkbox>
                          </t-checkbox-group>
                        </div>
                      </div>
                    </t-collapse-panel>
                    
                    <!-- 形状属性 -->
                    <t-collapse-panel header="形状属性" value="shape" v-if="isShapeObject">
                      <div class="property-group">
                        <div class="property-item">
                          <label>填充颜色:</label>
                          <input 
                            type="color" 
                            v-model="objectProperties.fill" 
                            @change="updateObjectProperty('fill', objectProperties.fill)"
                          />
                        </div>
                        
                        <div class="property-item">
                          <label>边框样式:</label>
                          <t-select 
                            v-model="objectProperties.strokeDashArray" 
                            :options="strokeOptions"
                            @change="updateObjectProperty('strokeDashArray', objectProperties.strokeDashArray)"
                          />
                        </div>
                      </div>
                    </t-collapse-panel>
                  </t-collapse>
                </div>
                
                <div class="no-selection" v-else>
                  <p>请选择一个对象来编辑属性</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右键菜单 -->
      <div 
        v-show="contextMenu.visible"
        class="context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
        @click.stop
      >
        <div class="menu-item" @click="contextMenuActions.copy" v-if="contextMenu.targetObject">
          <t-icon name="file-copy" size="14px" />
          <span>复制</span>
        </div>
        <div class="menu-item" @click="contextMenuActions.paste" v-if="copiedObject">
          <t-icon name="file-paste" size="14px" />
          <span>粘贴</span>
        </div>
        <div class="menu-divider" v-if="contextMenu.targetObject || copiedObject"></div>
        <div class="menu-item" @click="contextMenuActions.bringToFront" v-if="contextMenu.targetObject">
          <t-icon name="arrow-up" size="14px" />
          <span>置于顶层</span>
        </div>
        <div class="menu-item" @click="contextMenuActions.sendToBack" v-if="contextMenu.targetObject">
          <t-icon name="arrow-down" size="14px" />
          <span>置于底层</span>
        </div>
        <div class="menu-divider" v-if="contextMenu.targetObject"></div>
        <div class="menu-item" @click="contextMenuActions.duplicate" v-if="contextMenu.targetObject">
          <t-icon name="file-copy" size="14px" />
          <span>复制对象</span>
        </div>
        <div class="menu-item danger" @click="contextMenuActions.delete" v-if="contextMenu.targetObject">
          <t-icon name="delete" size="14px" />
          <span>删除</span>
        </div>
      </div>
      
      <!-- 图层右键菜单 -->
      <div 
        class="layer-context-menu"
        v-show="layerContextMenu.visible"
        :style="{ left: layerContextMenu.x + 'px', top: layerContextMenu.y + 'px' }"
        @click.stop
      >
        <div class="menu-item" @click="layerContextMenuActions.duplicate" v-if="layerContextMenu.targetLayer && layerContextMenu.targetLayer.id !== 'background'">
          <t-icon name="file-copy" size="14px" />
          <span>复制图层</span>
        </div>
        <div class="menu-item" @click="layerContextMenuActions.rename" v-if="layerContextMenu.targetLayer && layerContextMenu.targetLayer.id !== 'background'">
          <t-icon name="edit" size="14px" />
          <span>重命名</span>
        </div>
        <div class="menu-divider" v-if="layerContextMenu.targetLayer && layerContextMenu.targetLayer.id !== 'background'"></div>
        <div class="menu-item" @click="layerContextMenuActions.mergeDown" v-if="canMergeDown && layerContextMenu.targetLayer && layerContextMenu.targetLayer.id !== 'background'">
          <t-icon name="merge-cells" size="14px" />
          <span>向下合并</span>
        </div>
        <div class="menu-item" @click="layerContextMenuActions.flatten" v-if="layerContextMenu.targetLayer && layerContextMenu.targetLayer.id !== 'background'">
          <t-icon name="layers" size="14px" />
          <span>拼合图层</span>
        </div>
        <div class="menu-divider" v-if="layerContextMenu.targetLayer && layerContextMenu.targetLayer.id !== 'background'"></div>
        <div class="menu-item danger" @click="layerContextMenuActions.delete" v-if="layerContextMenu.targetLayer && layerContextMenu.targetLayer.id !== 'background'">
          <t-icon name="delete" size="14px" />
          <span>删除图层</span>
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

// 面板显示状态
const showLayerPanel = ref(true)
const showPropertiesPanel = ref(false)
const activePropertyPanel = ref(['basic'])

// 性能优化工具函数
const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

const throttle = (func, limit) => {
  let inThrottle
  return function() {
    const args = arguments
    const context = this
    if (!inThrottle) {
      func.apply(context, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// 批量渲染优化
let renderQueue = []
let isRenderScheduled = false

const scheduleRender = () => {
  if (!isRenderScheduled && canvas.value) {
    isRenderScheduled = true
    requestAnimationFrame(() => {
      canvas.value.renderAll()
      renderQueue = []
      isRenderScheduled = false
    })
  }
}

const batchRender = (callback) => {
  if (callback) {
    renderQueue.push(callback)
    callback()
  }
  scheduleRender()
}

// 图层管理
const layers = ref([
  {
    id: 'background',
    name: '背景图片',
    visible: true,
    locked: true,
    opacity: 100,
    objects: []
  },
  {
    id: 'layer1',
    name: '标注图层 1',
    visible: true,
    locked: false,
    opacity: 100,
    objects: []
  }
])
const activeLayerId = ref('layer1')

// 图层右键菜单
const layerContextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  targetLayer: null
})

// 计算是否可以向下合并
const canMergeDown = computed(() => {
  if (!layerContextMenu.value.targetLayer) return false
  const currentIndex = layers.value.findIndex(l => l.id === layerContextMenu.value.targetLayer.id)
  return currentIndex < layers.value.length - 1 && layers.value[currentIndex + 1].id !== 'background'
})

// 拖拽状态
const dragState = ref({
  isDragging: false,
  dragIndex: -1,
  dropIndex: -1
})

// 选中对象和属性
const selectedObject = ref(null)
const objectProperties = ref({
  color: '#ff0000',
  opacity: 100,
  strokeWidth: 2,
  fill: 'transparent',
  strokeDashArray: null,
  fontFamily: 'Arial',
  fontSize: 20,
  fontStyles: []
})

// 字体选项
const fontOptions = [
  { label: 'Arial', value: 'Arial' },
  { label: '宋体', value: 'SimSun' },
  { label: '黑体', value: 'SimHei' },
  { label: '微软雅黑', value: 'Microsoft YaHei' },
  { label: 'Times New Roman', value: 'Times New Roman' },
  { label: 'Helvetica', value: 'Helvetica' }
]

// 边框样式选项
const strokeOptions = [
  { label: '实线', value: null },
  { label: '虚线', value: [5, 5] },
  { label: '点线', value: [2, 2] },
  { label: '点划线', value: [10, 5, 2, 5] }
]

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
  // 如果点击的是当前已选中的工具，则取消选择（切换到选择工具）
  if (currentTool.value === tool && tool !== 'select') {
    currentTool.value = 'select'
    tool = 'select'
  } else {
    currentTool.value = tool
  }
  
  if (!canvas.value) return
  
  // 重置画布状态
  canvas.value.isDrawingMode = false
  canvas.value.selection = true
  
  // 清除所有事件监听器（避免工具切换时的冲突）
  canvas.value.off('mouse:down')
  canvas.value.off('mouse:move')
  canvas.value.off('mouse:up')
  
  // 重新绑定基础事件监听器
  bindBasicCanvasEvents()
  
  switch (tool) {
    case 'select':
      // 选择工具 - 默认状态
      canvas.value.selection = true
      canvas.value.isDrawingMode = false
      break
      
    case 'draw':
      canvas.value.isDrawingMode = true
      canvas.value.selection = false
      setupBrush('PencilBrush')
      break
      
    case 'highlighter':
      canvas.value.isDrawingMode = true
      canvas.value.selection = false
      setupBrush('PencilBrush', { opacity: 0.5, width: brushWidth.value * 2 })
      break
      

    case 'text':
      canvas.value.selection = false
      addText()
      break
      
    case 'rectangle':
      canvas.value.selection = false
      enableShapeDrawing('rectangle')
      break
      
    case 'circle':
      canvas.value.selection = false
      enableShapeDrawing('circle')
      break
      
    case 'ellipse':
      canvas.value.selection = false
      enableShapeDrawing('ellipse')
      break
      
    case 'line':
      canvas.value.selection = false
      enableShapeDrawing('line')
      break
      
    case 'arrow':
      canvas.value.selection = false
      enableShapeDrawing('arrow')
      break
      
    case 'polygon':
      canvas.value.selection = false
      enablePolygonDrawing()
      break
      
    case 'ruler':
      canvas.value.selection = false
      enableMeasurementTool('distance')
      break
      
    case 'protractor':
      canvas.value.selection = false
      enableMeasurementTool('angle')
      break
  }
}

// 设置画笔
const setupBrush = (brushType, options = {}) => {
  if (!canvas.value || !window.fabricClasses) return
  
  const brushOptions = {
    color: options.color || brushColor.value,
    width: options.width || brushWidth.value,
    opacity: options.opacity || 1,
    ...options
  }
  
  switch (brushType) {
    case 'PencilBrush':
      if (window.fabricClasses.PencilBrush) {
        canvas.value.freeDrawingBrush = new window.fabricClasses.PencilBrush(canvas.value)
      }
      break

  }
  
  if (canvas.value.freeDrawingBrush) {
    canvas.value.freeDrawingBrush.color = brushOptions.color
    canvas.value.freeDrawingBrush.width = brushOptions.width
    if (brushOptions.opacity < 1) {
      canvas.value.freeDrawingBrush.color = hexToRgba(brushOptions.color, brushOptions.opacity)
    }
  }
}

// 颜色转换工具
const hexToRgba = (hex, alpha) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
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
  addObjectToLayer(text) // 将新对象添加到当前活动图层
  canvas.value.setActiveObject(text)
  text.enterEditing()
}

// 启用形状绘制模式
const enableShapeDrawing = (shapeType) => {
  if (!canvas.value) return
  
  // 移除之前的事件监听
  canvas.value.off('mouse:down', onShapeMouseDown)
  canvas.value.off('mouse:move', onShapeMouseMove)
  canvas.value.off('mouse:up', onShapeMouseUp)
  
  // 添加新的事件监听
  canvas.value.on('mouse:down', (e) => onShapeMouseDown(e, shapeType))
  canvas.value.on('mouse:move', (e) => onShapeMouseMove(e, shapeType))
  canvas.value.on('mouse:up', (e) => onShapeMouseUp(e, shapeType))
}

// 形状绘制状态
const shapeDrawing = ref({
  isDrawing: false,
  startPoint: null,
  currentShape: null
})

// 形状绘制 - 鼠标按下
const onShapeMouseDown = (event, shapeType) => {
  if (!canvas.value || !window.fabricClasses) return
  
  const pointer = canvas.value.getPointer(event.e)
  shapeDrawing.value.isDrawing = true
  shapeDrawing.value.startPoint = pointer
  
  // 创建对应的形状
  let shape = null
  
  switch (shapeType) {
    case 'rectangle':
      shape = new window.fabricClasses.Rect({
        left: pointer.x,
        top: pointer.y,
        width: 0,
        height: 0,
        fill: 'transparent',
        stroke: brushColor.value,
        strokeWidth: brushWidth.value,
        selectable: false
      })
      break
      
    case 'circle':
      shape = new window.fabricClasses.Circle({
        left: pointer.x,
        top: pointer.y,
        radius: 0,
        fill: 'transparent',
        stroke: brushColor.value,
        strokeWidth: brushWidth.value,
        selectable: false
      })
      break
      
    case 'ellipse':
      shape = new window.fabricClasses.Ellipse({
        left: pointer.x,
        top: pointer.y,
        rx: 0,
        ry: 0,
        fill: 'transparent',
        stroke: brushColor.value,
        strokeWidth: brushWidth.value,
        selectable: false
      })
      break
      
    case 'line':
      shape = new window.fabricClasses.Line([pointer.x, pointer.y, pointer.x, pointer.y], {
        stroke: brushColor.value,
        strokeWidth: brushWidth.value,
        selectable: false
      })
      break
      
    case 'arrow':
      shape = createArrow(pointer.x, pointer.y, pointer.x, pointer.y)
      break
  }
  
  if (shape) {
    canvas.value.add(shape)
    addObjectToLayer(shape) // 将新对象添加到当前活动图层
    shapeDrawing.value.currentShape = shape
  }
}

// 形状绘制 - 鼠标移动
const onShapeMouseMove = (event, shapeType) => {
  if (!shapeDrawing.value.isDrawing || !shapeDrawing.value.currentShape) return
  
  const pointer = canvas.value.getPointer(event.e)
  const startPoint = shapeDrawing.value.startPoint
  const shape = shapeDrawing.value.currentShape
  
  switch (shapeType) {
    case 'rectangle':
      const width = Math.abs(pointer.x - startPoint.x)
      const height = Math.abs(pointer.y - startPoint.y)
      shape.set({
        left: Math.min(startPoint.x, pointer.x),
        top: Math.min(startPoint.y, pointer.y),
        width: width,
        height: height
      })
      break
      
    case 'circle':
      const radius = Math.sqrt(
        Math.pow(pointer.x - startPoint.x, 2) + Math.pow(pointer.y - startPoint.y, 2)
      ) / 2
      shape.set({
        radius: radius,
        left: startPoint.x - radius,
        top: startPoint.y - radius
      })
      break
      
    case 'ellipse':
      const rx = Math.abs(pointer.x - startPoint.x) / 2
      const ry = Math.abs(pointer.y - startPoint.y) / 2
      shape.set({
        rx: rx,
        ry: ry,
        left: Math.min(startPoint.x, pointer.x),
        top: Math.min(startPoint.y, pointer.y)
      })
      break
      
    case 'line':
      shape.set({
        x2: pointer.x,
        y2: pointer.y
      })
      break
      
    case 'arrow':
      updateArrow(shape, startPoint.x, startPoint.y, pointer.x, pointer.y)
      break
  }
  
  canvas.value.renderAll()
}

// 图层拖拽排序功能
const startDrag = (event, index) => {
  // 防止点击事件和拖拽事件冲突
  if (event.button !== 0) return // 只响应左键
  
  dragState.value.isDragging = true
  dragState.value.dragIndex = index
}

const onDragStart = (event, index) => {
  dragState.value.dragIndex = index
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', index.toString())
}

const onDrop = (event, dropIndex) => {
  event.preventDefault()
  const dragIndex = parseInt(event.dataTransfer.getData('text/plain'))
  
  if (dragIndex !== dropIndex && dragIndex >= 0 && dropIndex >= 0) {
    moveLayer(dragIndex, dropIndex)
  }
  
  dragState.value.isDragging = false
  dragState.value.dragIndex = -1
}

const onDragEnd = () => {
  dragState.value.isDragging = false
  dragState.value.dragIndex = -1
}

// 移动图层位置
const moveLayer = (fromIndex, toIndex) => {
  if (fromIndex === toIndex || fromIndex < 0 || toIndex < 0) return
  
  const layersCopy = [...layers.value]
  const movedLayer = layersCopy[fromIndex]
  
  // 防止移动背景图层
  if (movedLayer.id === 'background') {
    MessagePlugin.warning('背景图层不能移动')
    return
  }
  
  // 防止其他图层移动到背景图层位置（最后一个位置）
  if (toIndex === layersCopy.length - 1) {
    MessagePlugin.warning('不能将图层移动到背景图层位置')
    return
  }
  
  const [removedLayer] = layersCopy.splice(fromIndex, 1)
  layersCopy.splice(toIndex, 0, removedLayer)
  
  layers.value = layersCopy
  
  // 更新canvas中对象的层级
  updateCanvasLayerOrder()
  
  MessagePlugin.success(`图层 "${removedLayer.name}" 已移动`)
}

// 更新canvas中对象的层级顺序
const updateCanvasLayerOrder = () => {
  if (!canvas.value) return
  
  // 按图层顺序重新排列canvas中的对象
  const allObjects = canvas.value.getObjects()
  const sortedObjects = []
  
  // 按图层顺序收集对象
  layers.value.forEach(layer => {
    layer.objects.forEach(objId => {
      const obj = allObjects.find(o => o.id === objId)
      if (obj) {
        sortedObjects.push(obj)
      }
    })
  })
  
  // 清空canvas并重新添加对象
  canvas.value.clear()
  sortedObjects.forEach(obj => {
    canvas.value.add(obj)
  })
  
  canvas.value.renderAll()
}

// 形状绘制 - 鼠标释放
const onShapeMouseUp = (event, shapeType) => {
  if (!shapeDrawing.value.isDrawing) return
  
  shapeDrawing.value.isDrawing = false
  
  if (shapeDrawing.value.currentShape) {
    shapeDrawing.value.currentShape.set({ selectable: true })
    canvas.value.setActiveObject(shapeDrawing.value.currentShape)
    saveCanvasState()
  }
  
  shapeDrawing.value.currentShape = null
  shapeDrawing.value.startPoint = null
}

// 创建箭头
const createArrow = (x1, y1, x2, y2) => {
  if (!window.fabricClasses) return null
  
  const arrowGroup = new window.fabricClasses.Group([], {
    selectable: false
  })
  
  // 箭头线
  const line = new window.fabricClasses.Line([x1, y1, x2, y2], {
    stroke: brushColor.value,
    strokeWidth: brushWidth.value
  })
  
  // 箭头头部
  const arrowHead = createArrowHead(x1, y1, x2, y2)
  
  arrowGroup.addWithUpdate(line)
  if (arrowHead) {
    arrowGroup.addWithUpdate(arrowHead)
  }
  
  return arrowGroup
}

// 创建箭头头部
const createArrowHead = (x1, y1, x2, y2) => {
  if (!window.fabricClasses) return null
  
  const angle = Math.atan2(y2 - y1, x2 - x1)
  const arrowLength = 15
  const arrowAngle = Math.PI / 6
  
  const x3 = x2 - arrowLength * Math.cos(angle - arrowAngle)
  const y3 = y2 - arrowLength * Math.sin(angle - arrowAngle)
  const x4 = x2 - arrowLength * Math.cos(angle + arrowAngle)
  const y4 = y2 - arrowLength * Math.sin(angle + arrowAngle)
  
  const arrowHead = new window.fabricClasses.Polygon([
    { x: x2, y: y2 },
    { x: x3, y: y3 },
    { x: x4, y: y4 }
  ], {
    fill: brushColor.value,
    stroke: brushColor.value,
    strokeWidth: 1
  })
  
  return arrowHead
}

// 更新箭头
const updateArrow = (arrowGroup, x1, y1, x2, y2) => {
  if (!arrowGroup || !arrowGroup._objects) return
  
  // 更新线条
  const line = arrowGroup._objects[0]
  if (line) {
    line.set({ x2: x2, y2: y2 })
  }
  
  // 更新箭头头部
  if (arrowGroup._objects[1]) {
    arrowGroup.removeWithUpdate(arrowGroup._objects[1])
  }
  
  const newArrowHead = createArrowHead(x1, y1, x2, y2)
  if (newArrowHead) {
    arrowGroup.addWithUpdate(newArrowHead)
  }
}

// 启用多边形绘制
const enablePolygonDrawing = () => {
  if (!canvas.value) return
  
  // 移除之前的事件监听
  canvas.value.off('mouse:down', onPolygonMouseDown)
  canvas.value.off('mouse:dblclick', onPolygonDoubleClick)
  
  // 添加多边形绘制事件
  canvas.value.on('mouse:down', onPolygonMouseDown)
  canvas.value.on('mouse:dblclick', onPolygonDoubleClick)
}

// 多边形绘制状态
const polygonDrawing = ref({
  isDrawing: false,
  points: [],
  currentPolygon: null,
  previewLine: null
})

// 多边形绘制 - 鼠标点击
const onPolygonMouseDown = (event) => {
  if (!canvas.value || !window.fabricClasses) return
  
  const pointer = canvas.value.getPointer(event.e)
  
  if (!polygonDrawing.value.isDrawing) {
    // 开始绘制多边形
    polygonDrawing.value.isDrawing = true
    polygonDrawing.value.points = [pointer]
    
    // 创建预览线
    polygonDrawing.value.previewLine = new window.fabricClasses.Line(
      [pointer.x, pointer.y, pointer.x, pointer.y],
      {
        stroke: brushColor.value,
        strokeWidth: 1,
        strokeDashArray: [5, 5],
        selectable: false,
        evented: false
      }
    )
    canvas.value.add(polygonDrawing.value.previewLine)
  } else {
    // 添加新的点
    polygonDrawing.value.points.push(pointer)
    
    // 更新多边形
    updatePolygonPreview()
  }
}

// 多边形绘制 - 双击完成
const onPolygonDoubleClick = (event) => {
  if (!polygonDrawing.value.isDrawing) return
  
  finishPolygon()
}

// 更新多边形预览
const updatePolygonPreview = () => {
  if (!canvas.value || !window.fabricClasses || polygonDrawing.value.points.length < 2) return
  
  // 移除旧的多边形预览
  if (polygonDrawing.value.currentPolygon) {
    canvas.value.remove(polygonDrawing.value.currentPolygon)
  }
  
  // 创建新的多边形预览
  const points = polygonDrawing.value.points.map(p => ({ x: p.x, y: p.y }))
  
  polygonDrawing.value.currentPolygon = new window.fabricClasses.Polygon(points, {
    fill: 'transparent',
    stroke: brushColor.value,
    strokeWidth: brushWidth.value,
    strokeDashArray: [5, 5],
    selectable: false,
    evented: false
  })
  
  canvas.value.add(polygonDrawing.value.currentPolygon)
  canvas.value.renderAll()
}

// 完成多边形绘制
const finishPolygon = () => {
  if (!canvas.value || !window.fabricClasses || polygonDrawing.value.points.length < 3) {
    cancelPolygonDrawing()
    return
  }
  
  // 移除预览元素
  if (polygonDrawing.value.previewLine) {
    canvas.value.remove(polygonDrawing.value.previewLine)
  }
  if (polygonDrawing.value.currentPolygon) {
    canvas.value.remove(polygonDrawing.value.currentPolygon)
  }
  
  // 创建最终的多边形
  const points = polygonDrawing.value.points.map(p => ({ x: p.x, y: p.y }))
  const finalPolygon = new window.fabricClasses.Polygon(points, {
    fill: 'transparent',
    stroke: brushColor.value,
    strokeWidth: brushWidth.value,
    selectable: true
  })
  
  canvas.value.add(finalPolygon)
  addObjectToLayer(finalPolygon) // 将新对象添加到当前活动图层
  canvas.value.setActiveObject(finalPolygon)
  
  // 重置状态
  resetPolygonDrawing()
  saveCanvasState()
}

// 取消多边形绘制
const cancelPolygonDrawing = () => {
  if (polygonDrawing.value.previewLine) {
    canvas.value.remove(polygonDrawing.value.previewLine)
  }
  if (polygonDrawing.value.currentPolygon) {
    canvas.value.remove(polygonDrawing.value.currentPolygon)
  }
  
  resetPolygonDrawing()
  canvas.value.renderAll()
}

// 重置多边形绘制状态
const resetPolygonDrawing = () => {
  polygonDrawing.value.isDrawing = false
  polygonDrawing.value.points = []
  polygonDrawing.value.currentPolygon = null
  polygonDrawing.value.previewLine = null
}

// 启用测量工具
const enableMeasurementTool = (measureType) => {
  if (!canvas.value) return
  
  // 移除之前的事件监听
  canvas.value.off('mouse:down', onMeasureMouseDown)
  canvas.value.off('mouse:move', onMeasureMouseMove)
  canvas.value.off('mouse:up', onMeasureMouseUp)
  
  // 添加测量事件
  canvas.value.on('mouse:down', (e) => onMeasureMouseDown(e, measureType))
  canvas.value.on('mouse:move', (e) => onMeasureMouseMove(e, measureType))
  canvas.value.on('mouse:up', (e) => onMeasureMouseUp(e, measureType))
}

// 测量工具状态
const measurementState = ref({
  isActive: false,
  type: null,
  points: [],
  currentLine: null,
  measureText: null
})

// 测量工具 - 鼠标按下
const onMeasureMouseDown = (event, measureType) => {
  if (!canvas.value || !window.fabricClasses) return
  
  const pointer = canvas.value.getPointer(event.e)
  
  if (measureType === 'distance') {
    if (!measurementState.value.isActive) {
      // 开始距离测量
      measurementState.value.isActive = true
      measurementState.value.type = 'distance'
      measurementState.value.points = [pointer]
      
      // 创建测量线
      measurementState.value.currentLine = new window.fabricClasses.Line(
        [pointer.x, pointer.y, pointer.x, pointer.y],
        {
          stroke: '#ff6b35',
          strokeWidth: 2,
          strokeDashArray: [5, 5],
          selectable: false,
          evented: false
        }
      )
      canvas.value.add(measurementState.value.currentLine)
    }
  } else if (measureType === 'angle') {
    measurementState.value.points.push(pointer)
    
    if (measurementState.value.points.length === 1) {
      measurementState.value.isActive = true
      measurementState.value.type = 'angle'
    } else if (measurementState.value.points.length === 3) {
      // 完成角度测量
      finishAngleMeasurement()
    }
  }
}

// 测量工具 - 鼠标移动
const onMeasureMouseMove = (event, measureType) => {
  if (!measurementState.value.isActive) return
  
  const pointer = canvas.value.getPointer(event.e)
  
  if (measureType === 'distance' && measurementState.value.currentLine) {
    measurementState.value.currentLine.set({
      x2: pointer.x,
      y2: pointer.y
    })
    
    // 计算并显示距离
    const distance = calculateDistance(measurementState.value.points[0], pointer)
    updateDistanceDisplay(distance, pointer)
    
    canvas.value.renderAll()
  }
}

// 显示图层右键菜单
const showLayerContextMenu = (event, layer) => {
  event.preventDefault()
  event.stopPropagation()
  
  layerContextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    targetLayer: layer
  }
  
  // 点击其他地方隐藏菜单
  document.addEventListener('click', hideLayerContextMenu, { once: true })
}

// 隐藏图层右键菜单
const hideLayerContextMenu = () => {
  layerContextMenu.value.visible = false
  layerContextMenu.value.targetLayer = null
}

// 图层右键菜单操作
const layerContextMenuActions = {
  // 复制图层
  duplicate: () => {
    const targetLayer = layerContextMenu.value.targetLayer
    if (!targetLayer) return
    
    const newLayerId = `layer${Date.now()}`
    const newLayer = {
      id: newLayerId,
      name: `${targetLayer.name} 副本`,
      visible: targetLayer.visible,
      locked: targetLayer.locked,
      opacity: targetLayer.opacity,
      objects: []
    }
    
    // 复制图层中的对象
    if (canvas.value && targetLayer.objects.length > 0) {
      targetLayer.objects.forEach(objId => {
        const originalObj = canvas.value.getObjects().find(o => o.id === objId)
        if (originalObj) {
          originalObj.clone((clonedObj) => {
            clonedObj.set({
              left: clonedObj.left + 10,
              top: clonedObj.top + 10
            })
            canvas.value.add(clonedObj)
            addObjectToLayer(clonedObj, newLayerId)
            canvas.value.renderAll()
          })
        }
      })
    }
    
    layers.value.push(newLayer)
    activeLayerId.value = newLayerId
    hideLayerContextMenu()
    MessagePlugin.success('图层复制成功')
  },
  
  // 重命名图层
  rename: () => {
    const targetLayer = layerContextMenu.value.targetLayer
    if (!targetLayer) return
    
    // 聚焦到图层名称输入框
    hideLayerContextMenu()
    nextTick(() => {
      const layerItem = document.querySelector(`[data-layer-id="${targetLayer.id}"] .layer-name`)
      if (layerItem) {
        layerItem.focus()
        layerItem.select()
      }
    })
  },
  
  // 向下合并
  mergeDown: () => {
    const targetLayer = layerContextMenu.value.targetLayer
    if (!targetLayer || !canMergeDown.value) return
    
    const currentIndex = layers.value.findIndex(l => l.id === targetLayer.id)
    const belowLayer = layers.value[currentIndex + 1]
    
    if (belowLayer && canvas.value) {
      // 将当前图层的对象移动到下层
      targetLayer.objects.forEach(objId => {
        moveObjectToLayer(objId, targetLayer.id, belowLayer.id)
      })
      
      // 删除当前图层
      layers.value.splice(currentIndex, 1)
      
      // 如果删除的是活动图层，切换到合并后的图层
      if (activeLayerId.value === targetLayer.id) {
        activeLayerId.value = belowLayer.id
      }
      
      hideLayerContextMenu()
      MessagePlugin.success('图层合并成功')
    }
  },
  
  // 拼合图层
  flatten: () => {
    if (!canvas.value) return
    
    // 将所有可见图层的对象合并到背景图层
    const backgroundLayer = layers.value.find(l => l.id === 'background')
    if (!backgroundLayer) return
    
    layers.value.forEach(layer => {
      if (layer.id !== 'background' && layer.visible) {
        layer.objects.forEach(objId => {
          moveObjectToLayer(objId, layer.id, 'background')
        })
      }
    })
    
    // 删除除背景图层外的所有图层
    layers.value = layers.value.filter(l => l.id === 'background')
    
    // 创建新的标注图层
    const newLayer = {
      id: 'layer1',
      name: '标注图层 1',
      visible: true,
      locked: false,
      opacity: 100,
      objects: []
    }
    layers.value.push(newLayer)
    activeLayerId.value = 'layer1'
    
    hideLayerContextMenu()
    MessagePlugin.success('图层拼合成功')
  },
  
  // 删除图层
  delete: () => {
    const targetLayer = layerContextMenu.value.targetLayer
    if (!targetLayer || targetLayer.id === 'background') return
    
    deleteLayer(targetLayer.id)
    hideLayerContextMenu()
  }
}

// 测量工具 - 鼠标释放
const onMeasureMouseUp = (event, measureType) => {
  if (!measurementState.value.isActive) return
  
  if (measureType === 'distance') {
    const pointer = canvas.value.getPointer(event.e)
    measurementState.value.points.push(pointer)
    
    // 完成距离测量
    finishDistanceMeasurement()
  }
}

// 计算距离
const calculateDistance = (point1, point2) => {
  const dx = point2.x - point1.x
  const dy = point2.y - point1.y
  return Math.sqrt(dx * dx + dy * dy)
}

// 更新距离显示
const updateDistanceDisplay = (distance, position) => {
  if (!canvas.value || !window.fabricClasses) return
  
  // 移除旧的文字
  if (measurementState.value.measureText) {
    canvas.value.remove(measurementState.value.measureText)
  }
  
  // 创建新的距离文字
  measurementState.value.measureText = new window.fabricClasses.Text(
    `${Math.round(distance)}px`,
    {
      left: position.x + 10,
      top: position.y - 20,
      fontSize: 14,
      fill: '#ff6b35',
      backgroundColor: 'rgba(255, 255, 255, 0.8)',
      selectable: false,
      evented: false
    }
  )
  
  canvas.value.add(measurementState.value.measureText)
}

// 完成距离测量
const finishDistanceMeasurement = () => {
  if (measurementState.value.currentLine) {
    measurementState.value.currentLine.set({ selectable: true })
  }
  if (measurementState.value.measureText) {
    measurementState.value.measureText.set({ selectable: true })
  }
  
  resetMeasurementState()
  saveCanvasState()
}

// 完成角度测量
const finishAngleMeasurement = () => {
  if (measurementState.value.points.length !== 3) return
  
  const [point1, vertex, point2] = measurementState.value.points
  const angle = calculateAngle(point1, vertex, point2)
  
  // 创建角度显示
  const angleText = new window.fabricClasses.Text(
    `${Math.round(angle)}°`,
    {
      left: vertex.x + 15,
      top: vertex.y - 15,
      fontSize: 14,
      fill: '#ff6b35',
      backgroundColor: 'rgba(255, 255, 255, 0.8)',
      selectable: true
    }
  )
  
  canvas.value.add(angleText)
  
  resetMeasurementState()
  saveCanvasState()
}

// 计算角度
const calculateAngle = (point1, vertex, point2) => {
  const angle1 = Math.atan2(point1.y - vertex.y, point1.x - vertex.x)
  const angle2 = Math.atan2(point2.y - vertex.y, point2.x - vertex.x)
  let angle = Math.abs(angle2 - angle1)
  
  if (angle > Math.PI) {
    angle = 2 * Math.PI - angle
  }
  
  return (angle * 180) / Math.PI
}

// 重置测量状态
const resetMeasurementState = () => {
  measurementState.value.isActive = false
  measurementState.value.type = null
  measurementState.value.points = []
  measurementState.value.currentLine = null
  measurementState.value.measureText = null
}

// 面板切换方法
const toggleLayerPanel = () => {
  showLayerPanel.value = !showLayerPanel.value
}

const togglePropertiesPanel = () => {
  showPropertiesPanel.value = !showPropertiesPanel.value
}

// 图层管理方法
const addNewLayer = () => {
  const newLayerId = `layer${Date.now()}`
  const newLayer = {
    id: newLayerId,
    name: `标注图层 ${layers.value.length}`,
    visible: true,
    locked: false,
    opacity: 100,
    objects: []
  }
  
  layers.value.push(newLayer)
  activeLayerId.value = newLayerId
  MessagePlugin.success('新建图层成功')
}

const selectLayer = (layerId) => {
  activeLayerId.value = layerId
  // 应用图层隔离模式
  updateLayerIsolation()
  
  // 取消当前选择的对象（如果不属于当前图层）
  if (canvas.value && selectedObject.value && selectedObject.value.layerId !== layerId) {
    batchRender(() => {
      canvas.value.discardActiveObject()
      selectedObject.value = null
    })
  }
}

const toggleLayerVisibility = (layerId) => {
  const layer = layers.value.find(l => l.id === layerId)
  if (!layer) return
  
  // 背景图层不允许隐藏，始终保持可见
  if (layerId === 'background') {
    MessagePlugin.warning('背景图层不能隐藏')
    return
  }
  
  layer.visible = !layer.visible
  
  // 批量更新画布中对应对象的可见性
  if (canvas.value) {
    batchRender(() => {
      layer.objects.forEach(objId => {
        const obj = canvas.value.getObjects().find(o => o.id === objId)
        if (obj) {
          obj.set('visible', layer.visible)
        }
      })
    })
  }
}

const toggleLayerLock = (layerId) => {
  const layer = layers.value.find(l => l.id === layerId)
  if (!layer) return
  
  layer.locked = !layer.locked
  
  // 批量更新画布中对应对象的选择性
  if (canvas.value) {
    batchRender(() => {
      layer.objects.forEach(objId => {
        const obj = canvas.value.getObjects().find(o => o.id === objId)
        if (obj) {
          obj.set('selectable', !layer.locked)
          obj.set('evented', !layer.locked)
        }
      })
    })
  }
}

const updateLayerName = (layerId, newName) => {
  const layer = layers.value.find(l => l.id === layerId)
  if (layer) {
    layer.name = newName
  }
}

// 防抖优化的透明度更新函数
const debouncedOpacityUpdate = debounce((layerId, opacity) => {
  const layer = layers.value.find(l => l.id === layerId)
  if (!layer || !canvas.value) return
  
  // 批量更新对象透明度
  batchRender(() => {
    layer.objects.forEach(objId => {
      const obj = canvas.value.getObjects().find(o => o.id === objId)
      if (obj) {
        obj.set('opacity', opacity / 100)
      }
    })
  })
}, 100)

const updateLayerOpacity = (layerId, opacity) => {
  const layer = layers.value.find(l => l.id === layerId)
  if (!layer) return
  
  layer.opacity = opacity
  debouncedOpacityUpdate(layerId, opacity)
}

const deleteLayer = (layerId) => {
  if (layerId === 'background') {
    MessagePlugin.warning('背景图层不能删除')
    return
  }
  
  const layerIndex = layers.value.findIndex(l => l.id === layerId)
  if (layerIndex === -1) return
  
  const layer = layers.value[layerIndex]
  
  // 删除画布中对应的对象
  if (canvas.value) {
    layer.objects.forEach(objId => {
      const obj = canvas.value.getObjects().find(o => o.id === objId)
      if (obj) {
        canvas.value.remove(obj)
      }
    })
    canvas.value.renderAll()
  }
  
  // 删除图层
  layers.value.splice(layerIndex, 1)
  
  // 如果删除的是当前活动图层，切换到其他图层
  if (activeLayerId.value === layerId) {
    activeLayerId.value = layers.value.length > 0 ? layers.value[layers.value.length - 1].id : null
  }
  
  MessagePlugin.success('图层删除成功')
  saveCanvasState()
}

// 将对象添加到指定图层
const addObjectToLayer = (obj, layerId = null) => {
  if (!obj) return
  
  const targetLayerId = layerId || activeLayerId.value
  const layer = layers.value.find(l => l.id === targetLayerId)
  
  if (!layer) {
    console.warn('目标图层不存在:', targetLayerId)
    return
  }
  
  // 为对象分配唯一ID
  if (!obj.id) {
    obj.id = `obj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  // 设置对象的图层信息
  obj.layerId = targetLayerId
  obj.set({
    opacity: layer.opacity / 100,
    visible: layer.visible,
    selectable: !layer.locked,
    evented: !layer.locked
  })
  
  // 将对象ID添加到图层的对象列表中
  if (!layer.objects.includes(obj.id)) {
    layer.objects.push(obj.id)
  }
  
  console.log(`对象 ${obj.id} 已添加到图层 ${layer.name}`)
}

// 从图层中移除对象
const removeObjectFromLayer = (obj) => {
  if (!obj || !obj.layerId) return
  
  const layer = layers.value.find(l => l.id === obj.layerId)
  if (layer) {
    const index = layer.objects.indexOf(obj.id)
    if (index > -1) {
      layer.objects.splice(index, 1)
    }
  }
}

// 移动对象到指定图层
const moveObjectToLayer = (obj, targetLayerId) => {
  if (!obj) return
  
  // 从原图层移除
  removeObjectFromLayer(obj)
  
  // 添加到目标图层
  addObjectToLayer(obj, targetLayerId)
}

// 获取当前活动图层的对象
const getActiveLayerObjects = () => {
  const activeLayer = layers.value.find(l => l.id === activeLayerId.value)
  if (!activeLayer || !canvas.value) return []
  
  return canvas.value.getObjects().filter(obj => obj.layerId === activeLayerId.value)
}

// 更新图层隔离模式
const updateLayerIsolation = () => {
  if (!canvas.value) return
  
  const allObjects = canvas.value.getObjects()
  const activeLayer = layers.value.find(l => l.id === activeLayerId.value)
  
  // 批量更新所有对象的选择性和事件响应性
  batchRender(() => {
    allObjects.forEach(obj => {
      if (obj.layerId) {
        const objLayer = layers.value.find(l => l.id === obj.layerId)
        if (objLayer) {
          // 只有当前活动图层的对象可以被选择和编辑
          const isActiveLayer = obj.layerId === activeLayerId.value
          const isLayerVisible = objLayer.visible
          const isLayerUnlocked = !objLayer.locked
          
          obj.set({
            selectable: isActiveLayer && isLayerVisible && isLayerUnlocked,
            evented: isActiveLayer && isLayerVisible && isLayerUnlocked,
            visible: isLayerVisible,
            opacity: objLayer.opacity / 100
          })
        }
      }
    })
  })
}

// 属性面板方法
const isShapeObject = computed(() => {
  if (!selectedObject.value) return false
  const shapeTypes = ['rect', 'circle', 'ellipse', 'polygon', 'line']
  return shapeTypes.includes(selectedObject.value.type)
})

const updateObjectProperty = (property, value) => {
  if (!selectedObject.value || !canvas.value) return
  
  const updates = {}
  updates[property] = value
  
  selectedObject.value.set(updates)
  canvas.value.renderAll()
  saveCanvasState()
}

const updateFontStyles = (styles) => {
  if (!selectedObject.value || !canvas.value) return
  
  selectedObject.value.set({
    fontWeight: styles.includes('bold') ? 'bold' : 'normal',
    fontStyle: styles.includes('italic') ? 'italic' : 'normal',
    underline: styles.includes('underline')
  })
  
  canvas.value.renderAll()
  saveCanvasState()
}

// 监听对象选择
const onObjectSelected = (event) => {
  const obj = event.selected?.[0] || event.target
  if (!obj) {
    selectedObject.value = null
    return
  }
  
  // 检查对象是否属于当前活动图层
  const activeLayer = layers.value.find(layer => layer.id === activeLayerId.value)
  if (activeLayer && !activeLayer.objects.includes(obj)) {
    // 如果对象不属于当前图层，取消选择
    canvas.value.discardActiveObject()
    canvas.value.renderAll()
    selectedObject.value = null
    return
  }
  
  selectedObject.value = obj
  
  // 更新属性面板数据
  objectProperties.value = {
    color: obj.stroke || obj.fill || '#000000',
    opacity: Math.round((obj.opacity || 1) * 100),
    strokeWidth: obj.strokeWidth || 1,
    fill: obj.fill || 'transparent',
    strokeDashArray: obj.strokeDashArray || null,
    fontFamily: obj.fontFamily || 'Arial',
    fontSize: obj.fontSize || 20,
    fontStyles: [
      ...(obj.fontWeight === 'bold' ? ['bold'] : []),
      ...(obj.fontStyle === 'italic' ? ['italic'] : []),
      ...(obj.underline ? ['underline'] : [])
    ]
  }
  
  // 自动打开属性面板
  if (!showPropertiesPanel.value) {
    showPropertiesPanel.value = true
  }
}

// 监听对象取消选择
const onSelectionCleared = () => {
  selectedObject.value = null
}

// 快捷键支持
const keyboardShortcuts = {
  'KeyS': () => setTool('select'),
  'KeyD': () => setTool('draw'),
  'KeyT': () => setTool('text'),
  'KeyR': () => setTool('rectangle'),
  'KeyC': () => setTool('circle'),
  'KeyA': () => setTool('arrow'),
  'KeyP': () => setTool('polygon'),
  'KeyL': () => setTool('line'),
  'KeyH': () => setTool('highlighter'),
  
  'Delete': () => deleteSelectedObject(),
  'Backspace': () => deleteSelectedObject(),
  'Escape': () => deselectAll()
}

// 处理键盘事件
const handleKeyDown = (event) => {
  // 如果正在输入文字，不处理快捷键
  if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
    return
  }
  
  const key = event.code
  const isCtrl = event.ctrlKey || event.metaKey
  
  if (isCtrl) {
    switch (key) {
      case 'KeyZ':
        event.preventDefault()
        if (event.shiftKey) {
          redo()
        } else {
          undo()
        }
        break
      case 'KeyY':
        event.preventDefault()
        redo()
        break
      case 'KeyS':
        event.preventDefault()
        saveEditedImage()
        break
      case 'KeyA':
        event.preventDefault()
        selectAll()
        break
      case 'KeyC':
        event.preventDefault()
        copySelectedObject()
        break
      case 'KeyV':
        event.preventDefault()
        pasteObject()
        break
    }
  } else if (keyboardShortcuts[key]) {
    event.preventDefault()
    keyboardShortcuts[key]()
  }
}

// 删除选中对象
const deleteSelectedObject = () => {
  if (!canvas.value || !selectedObject.value) return
  
  canvas.value.remove(selectedObject.value)
  selectedObject.value = null
  canvas.value.renderAll()
  saveCanvasState()
}

// 取消选择所有对象
const deselectAll = () => {
  if (!canvas.value) return
  canvas.value.discardActiveObject()
  canvas.value.renderAll()
}

// 选择所有对象
const selectAll = () => {
  if (!canvas.value) return
  
  const objects = canvas.value.getObjects().filter(obj => !obj.isBackground)
  if (objects.length === 0) return
  
  if (objects.length === 1) {
    canvas.value.setActiveObject(objects[0])
  } else {
    const selection = new window.fabricClasses.ActiveSelection(objects, {
      canvas: canvas.value
    })
    canvas.value.setActiveObject(selection)
  }
  canvas.value.renderAll()
}

// 复制选中对象
const copySelectedObject = () => {
  if (!canvas.value || !selectedObject.value) return
  
  selectedObject.value.clone((cloned) => {
    copiedObject.value = cloned
    MessagePlugin.success('对象已复制')
  })
}

// 粘贴对象
const pasteObject = () => {
  if (!canvas.value || !copiedObject.value) return
  
  copiedObject.value.clone((cloned) => {
    cloned.set({
      left: cloned.left + 10,
      top: cloned.top + 10,
      evented: true,
      selectable: true
    })
    
    canvas.value.add(cloned)
    canvas.value.setActiveObject(cloned)
    canvas.value.renderAll()
    saveCanvasState()
  })
}

// 复制的对象
const copiedObject = ref(null)

// 绑定基础画布事件监听器
const bindBasicCanvasEvents = () => {
  if (!canvas.value) return
  
  // 监听画布基础事件
  canvas.value.on('path:created', (event) => {
    // 将新创建的路径添加到当前活动图层
    if (event.path) {
      addObjectToLayer(event.path)
    }
    saveCanvasState()
  })
  canvas.value.on('object:added', saveCanvasState)
  canvas.value.on('object:removed', (event) => {
    // 从图层中移除对象
    if (event.target) {
      removeObjectFromLayer(event.target)
    }
    saveCanvasState()
  })
  canvas.value.on('object:modified', saveCanvasState)
  
  // 监听对象选择事件
  canvas.value.on('selection:created', onObjectSelected)
  canvas.value.on('selection:updated', onObjectSelected)
  canvas.value.on('selection:cleared', onSelectionCleared)
  
  // 监听右键菜单事件
  canvas.value.on('mouse:down', (event) => {
    if (event.e.button === 2) { // 右键
      showContextMenu(event)
    } else {
      hideContextMenu()
      
      // 检查点击的对象是否属于当前活动图层
      const target = canvas.value.findTarget(event.e)
      if (target) {
        const activeLayer = layers.value.find(layer => layer.id === activeLayerId.value)
        if (activeLayer && !activeLayer.objects.includes(target)) {
          // 如果对象不属于当前图层，阻止选择
          event.e.preventDefault()
          canvas.value.discardActiveObject()
          canvas.value.renderAll()
          return false
        }
      }
    }
  })
}

// 右键菜单
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  targetObject: null
})

// 显示右键菜单
const showContextMenu = (event) => {
  event.preventDefault()
  
  const pointer = canvas.value.getPointer(event.e)
  const target = canvas.value.findTarget(event.e)
  
  contextMenu.value = {
    visible: true,
    x: event.e.clientX,
    y: event.e.clientY,
    targetObject: target
  }
}

// 隐藏右键菜单
const hideContextMenu = () => {
  contextMenu.value.visible = false
}

// 右键菜单操作
const contextMenuActions = {
  copy: () => {
    if (contextMenu.value.targetObject) {
      canvas.value.setActiveObject(contextMenu.value.targetObject)
      copySelectedObject()
    }
    hideContextMenu()
  },
  
  paste: () => {
    pasteObject()
    hideContextMenu()
  },
  
  delete: () => {
    if (contextMenu.value.targetObject) {
      canvas.value.remove(contextMenu.value.targetObject)
      canvas.value.renderAll()
      saveCanvasState()
    }
    hideContextMenu()
  },
  
  duplicate: () => {
    if (contextMenu.value.targetObject) {
      canvas.value.setActiveObject(contextMenu.value.targetObject)
      copySelectedObject()
      setTimeout(() => pasteObject(), 100)
    }
    hideContextMenu()
  },
  
  bringToFront: () => {
    if (contextMenu.value.targetObject) {
      canvas.value.bringToFront(contextMenu.value.targetObject)
      canvas.value.renderAll()
      saveCanvasState()
    }
    hideContextMenu()
  },
  
  sendToBack: () => {
    if (contextMenu.value.targetObject) {
      canvas.value.sendToBack(contextMenu.value.targetObject)
      canvas.value.renderAll()
      saveCanvasState()
    }
    hideContextMenu()
  }
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
    const { 
      Canvas, 
      Image, 
      IText, 
      Text,
      Rect, 
      Circle, 
      Ellipse, 
      Line, 
      Polygon, 
      Group,
      PencilBrush
    } = await import('fabric')
    
    // 创建 Fabric 画布
    canvas.value = new Canvas(fabricCanvasRef.value, {
      width: canvasWidth.value,
      height: canvasHeight.value,
      backgroundColor: '#ffffff',
      selection: true,
      preserveObjectStacking: true
    })
    
    // 将 fabric 实例保存到 canvas 元素上，供外部访问
    fabricCanvasRef.value.fabric = canvas.value
    
    // 保存 fabric 类到全局，供其他方法使用
    window.fabricClasses = { 
      Canvas, 
      Image, 
      IText, 
      Text,
      Rect, 
      Circle, 
      Ellipse, 
      Line, 
      Polygon, 
      Group,
      PencilBrush
    }
    
    // 设置画布属性
    canvas.value.isDrawingMode = false
    
    // 设置绘制画笔属性（需要先检查是否存在）
    if (canvas.value.freeDrawingBrush) {
      canvas.value.freeDrawingBrush.color = brushColor.value
      canvas.value.freeDrawingBrush.width = brushWidth.value
    }
    
    // 绑定基础画布事件监听器
    bindBasicCanvasEvents()
    
    // 加载图片和之前的编辑数据
    loadImageToCanvas()
    
    // 初始化图层隔离模式
    nextTick(() => {
      updateLayerIsolation()
    })
    
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
      id: 'background-image',
      layerId: 'background',
      left: 0,
      top: 0,
      scaleX: scale,
      scaleY: scale,
      selectable: false,
      evented: false,
      moveable: false,
      isBackground: true,
      lockMovementX: true,
      lockMovementY: true,
      lockRotation: true,
      lockScalingX: true,
      lockScalingY: true,
      lockUniScaling: true,
      hasControls: false,
      hasBorders: false
    })

    // 添加图片作为背景
    canvas.value.add(img)
    // 将图片移到最底层（Fabric.js 5+ 使用 moveTo）
    if (canvas.value.moveTo) {
      canvas.value.moveTo(img, 0)
    } else if (canvas.value.sendToBack) {
      canvas.value.sendToBack(img)
    }
    
    // 将背景图片添加到背景图层
    const backgroundLayer = layers.value.find(l => l.id === 'background')
    if (backgroundLayer) {
      backgroundLayer.objects = ['background-image']
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
  
  // 添加键盘事件监听
  document.addEventListener('keydown', handleKeyDown)
  
  // 添加全局点击事件监听（隐藏右键菜单）
  document.addEventListener('click', hideContextMenu)
  
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
  // 移除事件监听器
  document.removeEventListener('keydown', handleKeyDown)
  document.removeEventListener('click', hideContextMenu)
  
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
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
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

.edit-area {
  padding: 0;
  min-height: 600px;
}

.no-image-placeholder {
  text-align: center;
  color: #6b7280;
  padding: 40px;
}

.no-image-placeholder p {
  margin: 16px 0;
  font-size: 16px;
}

.edit-workspace {
  display: flex;
  height: 750px;
  width: 100%;
  gap: 0;
}

/* 左侧工具栏 */
.left-toolbar {
  width: 200px;
  background: #f8f9fa;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tool-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-section h4 {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tool-buttons {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tool-button {
  width: 100%;
  justify-content: flex-start;
  font-size: 12px;
  padding: 8px 12px;
  height: auto;
  min-height: 32px;
}

.brush-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.control-item label {
  font-size: 11px;
  color: #6b7280;
  font-weight: 500;
}

.control-item input[type="color"] {
  width: 100%;
  height: 32px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  padding: 0;
}

/* 中间画布区域 */
.canvas-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.canvas-container {
  flex: 1;
  border: 1px solid #e5e7eb;
  border-left: none;
  border-right: none;
  overflow: hidden;
  background: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
}

/* 右侧面板区域 */
.right-panels {
  width: 320px;
  background: #fff;
  border-left: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.left-panel, .right-panel {
  width: 100%;
  height: 100%;
  background: #fff;
  border: none;
  border-radius: 0;
  overflow: hidden;
}

/* 图层面板样式 */
.layer-panel, .properties-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.panel-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.layer-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  min-height: 0;
}

.layer-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.layer-item:hover {
  background: #f3f4f6;
}

.layer-item.active {
  background: #e0f2fe;
  border-color: #0ea5e9;
}

.layer-item.dragging {
  opacity: 0.5;
  transform: scale(0.95);
}

.layer-item[draggable="true"] {
  cursor: grab;
}

.layer-item[draggable="true"]:active {
  cursor: grabbing;
}

/* 背景图层特殊样式 */
.layer-item[data-layer-id="background"] {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  cursor: default;
}

.layer-item[data-layer-id="background"]:hover {
  background: #f1f5f9;
}

.layer-item[data-layer-id="background"].active {
  background: #e0f2fe;
  border-color: #0ea5e9;
}

.layer-item[data-layer-id="background"] .layer-name {
  color: #64748b;
  font-style: italic;
}

.layer-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.layer-info {
  flex: 1;
  min-width: 0;
}

.layer-name {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 3px;
  transition: background 0.2s;
}

.layer-name:focus {
  background: #fff;
  outline: 1px solid #0ea5e9;
}

.layer-opacity {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.opacity-label {
  font-size: 10px;
  color: #6b7280;
  white-space: nowrap;
}

.opacity-value {
  font-size: 10px;
  color: #6b7280;
  min-width: 30px;
}

/* 属性面板样式 */
.properties-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  min-height: 0;
}

.property-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.property-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.property-item label {
  font-size: 12px;
  font-weight: 500;
  color: #374151;
}

.property-item input[type="color"] {
  width: 40px;
  height: 28px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
}

.property-value {
  font-size: 12px;
  color: #6b7280;
  margin-left: 8px;
}

.no-selection {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 14px;
  text-align: center;
  padding: 20px;
}

.fabric-canvas {
  border: 1px solid #ddd;
  cursor: crosshair;
  max-width: 100%;
  max-height: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 160px;
  padding: 4px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background: #f3f4f6;
}

.menu-item.danger {
  color: #dc2626;
}

.menu-item.danger:hover {
  background: #fef2f2;
}

.menu-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 4px 0;
}

/* 图层右键菜单样式 */
.layer-context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  min-width: 160px;
  padding: 4px 0;
}

.layer-context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  transition: background-color 0.2s;
}

.layer-context-menu .menu-item:hover {
  background: #f3f4f6;
}

.layer-context-menu .menu-item.danger {
  color: #dc2626;
}

.layer-context-menu .menu-item.danger:hover {
  background: #fef2f2;
}

.layer-context-menu .menu-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 4px 0;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .image-edit-page {
    max-width: 1400px;
  }
  
  .edit-workspace {
    height: 650px;
  }
  
  .left-toolbar {
    width: 180px;
  }
  
  .right-panels {
    width: 300px;
  }
}

@media (max-width: 1200px) {
  .image-edit-page {
    max-width: 1200px;
  }
  
  .edit-workspace {
    height: 500px;
  }
  
  .left-toolbar {
    width: 180px;
  }
  
  .right-panels {
    width: 280px;
  }
}

@media (max-width: 992px) {
  .edit-workspace {
    height: 450px;
  }
  
  .left-toolbar {
    width: 160px;
    padding: 12px 8px;
  }
  
  .tool-section h4 {
    font-size: 11px;
  }
  
  .tool-button {
    font-size: 11px;
    padding: 6px 8px;
    min-height: 28px;
  }
  
  .right-panels {
    width: 260px;
  }
}

@media (max-width: 768px) {
  .edit-workspace {
    flex-direction: column;
    height: auto;
    min-height: 600px;
  }
  
  .left-toolbar {
    width: 100%;
    height: auto;
    max-height: 200px;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .tool-section {
    flex: 1;
    min-width: 120px;
  }
  
  .tool-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .tool-button {
    flex: 1;
    min-width: 60px;
  }
  
  .canvas-area {
    height: 400px;
  }
  
  .right-panels {
    width: 100%;
    height: 300px;
    border-left: none;
    border-top: 1px solid #e5e7eb;
    flex-direction: row;
  }
  
  .panel-container {
    flex: 1;
    min-width: 0;
  }
  
  .edit-status {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .left-toolbar {
    max-height: 150px;
  }
  
  .tool-section {
    min-width: 100px;
  }
  
  .tool-button {
    font-size: 10px;
    padding: 4px 6px;
    min-height: 24px;
  }
  
  .canvas-area {
    height: 300px;
  }
  
  .right-panels {
    height: 250px;
    flex-direction: column;
  }
}
</style>


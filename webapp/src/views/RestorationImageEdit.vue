<template>
  <t-card class="page-card">
    <div class="header">
      <div class="title">图片编辑与标注</div>
      <div class="desc">对需要处理的图片进行标注、编辑（必须完成此步骤）</div>
    </div>

    <div v-if="!hasFiles" class="empty-wrap">
      <t-empty description="请先返回上一步上传图片">
        <t-button theme="primary" @click="goPrev">返回上一步上传图片</t-button>
      </t-empty>
    </div>

    <div v-else class="editor-wrap">
      <!-- 左侧缩略图 -->
      <div class="thumbs">
        <div
          v-for="f in normFiles" :key="f.id"
          class="thumb" :class="{active: currentId===f.id}" @click="switchTo(f.id)"
        >
          <t-image :src="f.url" :style="{width:'100%',height:'90px'}" fit="cover" />
          <div class="thumb-name" :title="f.name">{{ f.name }}</div>
        </div>
      </div>

      <!-- 右侧：内联标注器（vue-konva） -->
      <div class="canvas">
        <div ref="wrapRef" class="stage-wrap" :class="{ moving:isMoveMode }" @mousedown="closeFillMenu">
          <v-stage
            ref="stageRef"
            :config="{ width: cw, height: ch, draggable: isPanning, scaleX: scale, scaleY: scale }"
            @wheel="onWheel" @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp"
          >
            <v-layer ref="bgLayer">
              <v-image v-if="img" :image="img" :width="imgW" :height="imgH"/>
            </v-layer>

            <v-layer ref="drawLayer">
              <component
                v-for="n in nodes"
                :key="n.id + '-' + historyVer"
                :is="getShapeComponent(n.type)"
                :config="{
                  ...n.attrs,
                  // 仅在移到模式下可拖拽；若节点被锁（attrs.draggable===false），依然不可拖
                  draggable: isMoveMode && n.attrs.draggable !== false
                }"
                @mousedown="selectNode(n.id, $event)"
                @dragend="onDragEnd(n.id, $event)"
                @transformend="onTransformEnd(n.id, $event)"
                @dblclick="toggleLock(n.id)"
              />
              <!-- 临时绘制 -->
              <v-line  v-if="tempLine && currentTool !== '箭头'" :config="tempLine" :listening="false" />
              <v-arrow v-if="tempLine && currentTool === '箭头'" :config="tempLine" :listening="false" />
              <v-rect v-if="tempRect" :config="tempRect" />
              <v-circle v-if="tempCircle" :config="tempCircle" />
            </v-layer>
          </v-stage>

          <!-- ▶ 点击圈选图形后弹出的下拉框（选择内部纹理/填充） -->
          <div v-if="fillMenu.visible" class="fill-menu"
               :style="{ left: fillMenu.x + 'px', top: fillMenu.y + 'px' }"
               @mousedown.stop>
            <t-select v-model="fillMenu.value"
                      :options="FILL_OPTIONS"
                      placeholder="选择纹理/填充"
                      @change="applyFillFromMenu" />
          </div>
        </div>

        <!-- 工具栏 -->
        <div class="toolbar">
          <button v-for="t in tools" :key="t" class="tool" :class="{active: currentTool===t}" @click="selectTool(t)">
            {{ t }}
          </button>

          <button class="tool" @click="undo" :disabled="!canUndo">撤销</button>
          <button class="tool" @click="redo" :disabled="!canRedo">重做</button>
          <button class="tool" @click="fit">自适应</button>

          <label class="tool">线宽
            <input type="number" v-model.number="strokeWidth" min="1" max="12" />
          </label>

          <button class="tool" @click="toggleMoveMode" :class="{active: isMoveMode}">
            移到
          </button>

          <button class="tool" @click="clearAllChanges" :disabled="nodes.length === 0">
            清除所有更改
          </button>
        </div>

        <div class="tips">
          "圈选填充"画出区域后会自动弹出下拉选择内部纹理。
          <br>点击"移到"按钮激活移到模式，然后才能拖拽移动图形位置。
          <br>点击"清除所有更改"按钮可清空所有绘图痕迹。
        </div>
      </div>
    </div>

    <!-- 验证状态提示 -->
    <div class="validation-status" v-if="!canProceed">
      <div class="validation-message">
        <t-icon name="info-circle" />
        <span>请先上传图片并完成编辑后才能继续下一步</span>
      </div>
    </div>
  </t-card>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted, onBeforeUnmount, nextTick, computed as vComputed } from 'vue'
import Konva from 'konva'
import { useRestorationFlowStore } from '@/stores/restorationFlow'

const store = useRestorationFlowStore()
const emit = defineEmits(['next','skip','prev'])

/** ========= 从store获取文件数据 ========= */
const files = computed(() => {
  const imageFiles = store.formData.image_file || []
  return imageFiles
})

/** ========= 统一文件结构 ========= */
const normFiles = computed(()=> {
  const processedFiles = (files.value||[]).map((f,idx)=>({
    id: f.uid || f.response?.id || f.id || `${idx}-${f.name || 'img'}`,
    url: f.url || f.response?.url || f.raw?.url || f.originUrl || f.response?.data?.url,
    name: f.name || `图片${idx+1}`,
  })).filter(x=>!!x.url)
  return processedFiles
})
const hasFiles = computed(()=> normFiles.value.length>0)
const currentId = ref(null)
watch(normFiles, (arr)=>{ if(arr.length && !currentId.value) currentId.value = arr[0].id }, { immediate:true })
const currentUrl = computed(()=> normFiles.value.find(f=>f.id===currentId.value)?.url || '')
function switchTo(id){ currentId.value = id; closeFillMenu() }

// 检查是否可以继续下一步
const hasEdits = ref(false)
const canProceed = computed(() => {
  // 与 store 中的 canGoNext 逻辑保持一致
  const hasFiles = !!(store.formData.image_file &&
                     Array.isArray(store.formData.image_file) &&
                     store.formData.image_file.length > 0)
  const hasEditedImage = !!store.imageEditData.editedImage
  return hasFiles && hasEditedImage
})

/** ========= 形状组件映射 ========= */
function getShapeComponent(type) {
  return {
    rect: 'v-rect',
    circle: 'v-circle',
    line: 'v-line',
    lasso: 'v-line',                  // 自由圈选闭合多边形
    arrow: 'v-arrow',
    text: 'v-text',
    'regular-polygon': 'v-regular-polygon'
  }[type] || 'v-line'
}

/** ========= 每张图片的标注 JSON 与 PNG 快照 ========= */
const annotations = reactive({})   // { [imgId]: { nodes:[...] } }
const snapshots   = reactive({})   // { [imgId]: 'data:image/png;base64,...' }
async function exportCurrent(){
  const out = await doExport()
  if (!currentId.value) return
  annotations[currentId.value] = out.json
  snapshots[currentId.value]   = out.png
}

/** ========= 画布尺寸/缩放 ========= */
const wrapRef = ref(null), stageRef = ref(null)
const cw = ref(0), ch = ref(0), scale = ref(1)
const MIN_SCALE = 0.2, MAX_SCALE = 8
const panHeld = ref(false)
const isPanning = vComputed(() => currentTool.value === '手掌' || panHeld.value)

const img = ref(null), imgW = ref(0), imgH = ref(0)
watch(currentUrl, loadImage, { immediate: true })
function loadImage() {
  if (!currentUrl.value) return
  const image = new window.Image()
  image.onload = () => {
    img.value = image; imgW.value = image.width; imgH.value = image.height
    fit()
    const json = annotations[currentId.value]
    nodes.splice(0, nodes.length, ...(json?.nodes || []))
    rebuildPatterns()
  }
  image.crossOrigin = 'anonymous'
  image.src = currentUrl.value
}
function fit() {
  if (!wrapRef.value || !imgW.value) return
  const w = wrapRef.value.clientWidth, h = wrapRef.value.clientHeight
  cw.value = w; ch.value = h
  const s = Math.min(w / imgW.value, h / imgH.value)
  scale.value = Math.max(MIN_SCALE, Math.min(1, s))
  const st = stageRef.value.getNode()
  st.position({ x: (w - imgW.value*scale.value)/2, y: (h - imgH.value*scale.value)/2 })
}
function onWheel(e){
  e.evt.preventDefault()
  const st = stageRef.value.getNode(), oldScale = scale.value
  const pointer = st.getPointerPosition()
  const mousePointTo = { x: (pointer.x - st.x())/oldScale, y: (pointer.y - st.y())/oldScale }
  const dir = e.evt.deltaY > 0 ? -1 : 1
  const newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, oldScale * (1 + dir*0.1)))
  scale.value = newScale
  st.position({ x: pointer.x - mousePointTo.x * newScale, y: pointer.y - mousePointTo.y * newScale })
  st.batchDraw()
}

/** ========= 图例与工具 ========= */
const LEGEND = reactive({
  '默认':        { stroke: '#ff2d55', pattern: null },
  '裂缝':        { stroke: '#ff2d55', dash: [8,4] },
  '鼓包/空鼓':   { stroke: '#ff2d55', fillPattern: 'dots' },
  '盐霜/粉化':   { stroke: '#ff2d55', fillPattern: 'hatch' },
  '网状剥落':    { stroke: '#ff2d55', fillPattern: 'grid' },
  '修补范围':    { stroke: '#ff2d55', fill: 'rgba(255,45,85,0.08)' },
})
const tools = ['选择','手掌','矩形','圆形','自由线','圈选填充','箭头']
const currentTool = ref('选择')
const strokeWidth = ref(3)

/** ========= 移到功能状态 ========= */
const isMoveMode = ref(false)


/** ========= 区域纹理贴图 ========= */
const patternCache = new Map()
function makePatternTile(kind) {
  if (!kind) return null
  // 缓存仍可复用（按需）
  if (patternCache.has(kind)) return patternCache.get(kind)

  const c = document.createElement('canvas')
  c.width = 24; c.height = 24
  const ctx = c.getContext('2d')
  ctx.strokeStyle = '#ff2d55'
  ctx.fillStyle = '#ff2d55'
  ctx.lineWidth = 1.2

  if (kind === 'dots') {
    ctx.beginPath(); ctx.arc(6,6,2,0,Math.PI*2); ctx.fill()
    ctx.beginPath(); ctx.arc(18,18,2,0,Math.PI*2); ctx.fill()
  } else if (kind === 'hatch') {
    for(let i=-24;i<48;i+=6){ ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i+24,24); ctx.stroke() }
  } else if (kind === 'grid') {
    for(let i=0;i<=24;i+=6){ ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,24); ctx.stroke()
      ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(24,i); ctx.stroke() }
  }

  patternCache.set(kind, c)       // ✅ 缓存"瓷砖画布"本身
  return c
}
function rebuildPatterns() {
  nodes.forEach(n=>{
    if (['rect','circle','regular-polygon','lasso'].includes(n.type) && n.attrs.fillPatternKind) {
      n.attrs.fillPatternImage = makePatternTile(n.attrs.fillPatternKind)  // ✅
      n.attrs.fillPatternRepeat = 'repeat'                                  // ✅ 保险
    }
  })
}

/** ========= 历史（响应式） ========= */
const nodes = reactive([])  // {id,type,attrs}
let idSeq = 1
const history = ref([])
const hPtr = ref(-1)
const historyVer = ref(0)

async function pushHistory() {
  const snap = JSON.stringify({ nodes: JSON.parse(JSON.stringify(nodes)) })
  history.value.splice(hPtr.value + 1)
  history.value.push(snap)
  hPtr.value = history.value.length - 1
  
  // 强制更新编辑状态
  nextTick(async () => {
    const newHasEdits = nodes.length > 0
    hasEdits.value = newHasEdits
    
    // 如果有编辑内容，自动保存编辑后的图片到 store
    if (newHasEdits) {
      try {
        const editedImageData = await exportPNG()
        store.saveImageEdit({
          editedImage: editedImageData,
          hasEdited: true
        })
      } catch (error) {
        console.error('自动保存编辑图片失败:', error)
      }
    }
  })
}

const canUndo = computed(()=> hPtr.value > 0)
const canRedo = computed(()=> hPtr.value < history.value.length - 1)

function loadHistory(s){
  const data = JSON.parse(s)
  nodes.splice(0, nodes.length, ...data.nodes)
  rebuildPatterns()
  historyVer.value++
  stageRef.value?.getNode()?.batchDraw()
}
function undo(){ if(!canUndo.value) return; hPtr.value--; loadHistory(history.value[hPtr.value]) }
function redo(){ if(!canRedo.value) return; hPtr.value++; loadHistory(history.value[hPtr.value]) }

// 监听编辑状态
watch(nodes, () => { 
  const newHasEdits = nodes.length > 0
  hasEdits.value = newHasEdits 
}, { deep: true, immediate: true })

// 监听文件变化，确保状态正确更新
watch(normFiles, () => {
  // 强制触发 canProceed 重新计算
  nextTick(() => {
    // 确保状态同步
  })
}, { immediate: true })


function selectNode(id, evt){
  // Konva 事件 or 原生事件
  const domEvt = evt?.evt || evt
  const n = nodes.find(x=>x.id===id)

  // 仅在【选择工具】且【不是移到模式】且【lasso】时弹菜单
  if (currentTool.value === '选择' && !isMoveMode.value && n && n.type === 'lasso') {
    openFillMenuAt(domEvt?.clientX, domEvt?.clientY, id, n)
  } else {
    closeFillMenu()
  }
}


/** ========= 下拉框（选择圈选内部填充） ========= */
const FILL_OPTIONS = [
  { label: '无填充', value: 'none' },
  { label: '纯色（修补范围）', value: 'solid' },
  { label: '点阵（鼓包/空鼓）', value: 'dots' },
  { label: '斜线（盐霜/粉化）', value: 'hatch' },
  { label: '网格（网状剥落）', value: 'grid' },
]
const fillMenu = reactive({ visible:false, x:0, y:0, targetId:null, value:'none' })

function openFillMenuAt(clientX, clientY, id, node){
  const host = wrapRef.value?.getBoundingClientRect()
  if (!host) return
  
  // 如果传入的是画布坐标，需要转换为相对于容器的坐标
  let L, T
  if (typeof clientX === 'number' && typeof clientY === 'number') {
    // 检查是否是画布坐标（通常小于容器尺寸）
    if (clientX < host.width && clientY < host.height) {
      // 画布坐标，直接使用
      L = Math.max(8, Math.min(clientX, host.width - 188))
      T = Math.max(8, Math.min(clientY, host.height - 56))
    } else {
      // 屏幕坐标，需要减去容器偏移
      L = Math.max(8, Math.min((clientX - host.left), host.width - 188))
      T = Math.max(8, Math.min((clientY - host.top), host.height - 56))
    }
  } else {
    // 默认位置
    L = 100; T = 100
  }
  
  fillMenu.x = L; fillMenu.y = T
  fillMenu.targetId = id
  // 初始值：根据当前节点填充状态回填
  if (node.attrs.fillPatternKind) fillMenu.value = node.attrs.fillPatternKind
  else if (node.attrs.fill)       fillMenu.value = 'solid'
  else                            fillMenu.value = 'none'
  fillMenu.visible = true
}
function closeFillMenu(){ fillMenu.visible = false; fillMenu.targetId = null }

async function applyFillFromMenu(val){
  const id = fillMenu.targetId
  if (!id) return
  const n = nodes.find(x=>x.id===id)
  if (!n) return

  delete n.attrs.fill; delete n.attrs.fillPatternKind; delete n.attrs.fillPatternImage; delete n.attrs.fillPatternRepeat
  if (val === 'none') {
    // no fill
  } else if (val === 'solid') {
    const solid = LEGEND['修补范围']?.fill || 'rgba(255,45,85,0.08)'
    n.attrs.fill = solid
  } else {
    n.attrs.fillPatternKind = val
    n.attrs.fillPatternImage = makePatternTile(val)   // ✅
    n.attrs.fillPatternRepeat = 'repeat'              // ✅
  }
  if (n.type === 'lasso') n.attrs.closed = true

  rebuildPatterns()
  await pushHistory()
  stageRef.value?.getNode()?.batchDraw()
  closeFillMenu()
}

/** ========= 交互（绘制） ========= */
let isDrawing=false, startPos=null
const tempRect=ref(null), tempCircle=ref(null), tempLine=ref(null)

function styleNow(){
  const lg = LEGEND['默认']
  const base = { stroke: lg.stroke||'#ff2d55', strokeWidth: strokeWidth.value, lineCap:'round', lineJoin:'round', dash: lg.dash||null }
  return { lg, base }
}
function arrowHeadFor(sw){
  const s = Math.max(1, sw || strokeWidth.value)
  return { pointerLength: Math.max(12, s*4), pointerWidth: Math.max(10, s*2.5) }
}

async function onMouseDown(e){
  closeFillMenu()

  const st = stageRef.value.getNode()
  if (!st) return
  const pos = st.getPointerPosition()
  if (!pos) return
  const x = st.x(), y = st.y()
  const relativePos = { x: (pos.x - x) / scale.value, y: (pos.y - y) / scale.value }

  const { base } = styleNow()

  if (currentTool.value==='矩形') {
    isDrawing=true; startPos=relativePos
    tempRect.value={...base,x:relativePos.x,y:relativePos.y,width:0,height:0,draggable:true}
  }
  else if (currentTool.value==='圆形') {
    isDrawing=true; startPos=relativePos
    tempCircle.value={...base,x:relativePos.x,y:relativePos.y,radius:0,draggable:true}
  }
  else if (currentTool.value==='自由线') {
    isDrawing=true
    tempLine.value={...base,points:[relativePos.x,relativePos.y],draggable:false,lineCap:'round',lineJoin:'round',hitStrokeWidth:Math.max(10, strokeWidth.value*2)}
  }
  else if (currentTool.value==='圈选填充') {
    isDrawing=true
    tempLine.value={...base,points:[relativePos.x,relativePos.y],draggable:false,lineCap:'round',lineJoin:'round',hitStrokeWidth:Math.max(10, strokeWidth.value*2)}
  }
  else if (currentTool.value==='箭头') {
    isDrawing=true
    const head = arrowHeadFor(strokeWidth.value)
    tempLine.value={...base,...head,points:[relativePos.x,relativePos.y,relativePos.x,relativePos.y],draggable:false,fill:base.stroke,hitStrokeWidth:Math.max(10, strokeWidth.value*2)}
  }
}
function onMouseMove(){
  if(!isDrawing) return
  const st = stageRef.value.getNode()
  if (!st) return
  const pos = st.getPointerPosition()
  if (!pos) return
  const x = st.x(), y = st.y()
  const relativePos = { x: (pos.x - x) / scale.value, y: (pos.y - y) / scale.value }

  if (tempRect.value){
    tempRect.value.width = relativePos.x-startPos.x
    tempRect.value.height = relativePos.y-startPos.y
  }
  else if (tempCircle.value){
    const dx=relativePos.x-startPos.x, dy=relativePos.y-startPos.y
    tempCircle.value.radius = Math.sqrt(dx*dx+dy*dy)
  }
  else if (tempLine.value && currentTool.value === '自由线') {
    const pts = (tempLine.value.points || []).slice()
    pts.push(relativePos.x, relativePos.y)
    tempLine.value = { ...tempLine.value, points: pts }
    stageRef.value.getNode().batchDraw()
  }
  else if (tempLine.value && currentTool.value === '圈选填充') {
    const pts = (tempLine.value.points || []).slice()
    pts.push(relativePos.x, relativePos.y)
    tempLine.value = { ...tempLine.value, points: pts }
    stageRef.value.getNode().batchDraw()
  }
  else if (tempLine.value && currentTool.value==='箭头'){
    tempLine.value.points=[tempLine.value.points[0],tempLine.value.points[1],relativePos.x,relativePos.y]
  }
}
async function onMouseUp(){
  if(!isDrawing) return
  const { lg } = styleNow()

  if (tempRect.value){
    const attrs = {
      ...tempRect.value,
      x: Math.min(tempRect.value.x, tempRect.value.x+tempRect.value.width),
      y: Math.min(tempRect.value.y, tempRect.value.y+tempRect.value.height),
      width: Math.abs(tempRect.value.width),
      height: Math.abs(tempRect.value.height),
      draggable:true
    }
    if (lg.fillPattern){ 
      attrs.fillPatternKind = lg.fillPattern
      attrs.fillPatternImage = makePatternTile(lg.fillPattern)   // ✅ 用 Canvas 瓷砖
      attrs.fillPatternRepeat = 'repeat'                         // ✅ 指定重复
    }
    else if (lg.fill){ attrs.fill=lg.fill }
    nodes.push({ id:idSeq++, type:'rect', attrs })
  }
  else if (tempCircle.value){
    const attrs = { ...tempCircle.value, draggable:true }
    if (lg.fillPattern){ 
      attrs.fillPatternKind = lg.fillPattern
      attrs.fillPatternImage = makePatternTile(lg.fillPattern)   // ✅ 用 Canvas 瓷砖
      attrs.fillPatternRepeat = 'repeat'                         // ✅ 指定重复
    }
    else if (lg.fill){ attrs.fill=lg.fill }
    nodes.push({ id:idSeq++, type:'circle', attrs })
  }
  else if (tempLine.value && currentTool.value==='自由线'){
    nodes.push({ id:idSeq++, type:'line', attrs:{ ...tempLine.value, tension:0.2, draggable:true } })
  }
  else if (tempLine.value && currentTool.value==='圈选填充'){
    const simplified = rdpSimplify(tempLine.value.points, 1.2)
    // 确保路径闭合
    if (simplified.length >= 4 &&
        (simplified[0] !== simplified[simplified.length-2] ||
         simplified[1] !== simplified[simplified.length-1])) {
      simplified.push(simplified[0], simplified[1])
    }
    const attrs = { ...tempLine.value, points: simplified, closed: true, draggable: true }
    if (lg.fillPattern){ 
      attrs.fillPatternKind = lg.fillPattern
      attrs.fillPatternImage = makePatternTile(lg.fillPattern)   // ✅ 用 Canvas 瓷砖
      attrs.fillPatternRepeat = 'repeat'                         // ✅ 指定重复
    }
    else if (lg.fill){ attrs.fill=lg.fill }
    else { attrs.fill='rgba(255,45,85,0.08)' }
    const newNode = { id:idSeq++, type:'lasso', attrs }
    nodes.push(newNode)
    
    // 绘制完成后自动弹出填充菜单
    await nextTick()
    const st = stageRef.value.getNode()
    if (st) {
      const pos = st.getPointerPosition()
      if (pos) {
        // 使用鼠标当前位置作为菜单显示位置
        openFillMenuAt(pos.x, pos.y, newNode.id, newNode)
      }
    }
  }
  else if (tempLine.value && currentTool.value==='箭头'){
    const head = arrowHeadFor(tempLine.value.strokeWidth)
    nodes.push({ id:idSeq++, type:'arrow', attrs:{ ...tempLine.value, ...head, draggable:true } })
  }

  tempRect.value=null; tempCircle.value=null; tempLine.value=null
  isDrawing=false; startPos=null; await pushHistory()
}

/** 锁定/解锁 */
async function toggleLock(id){ const n=nodes.find(x=>x.id===id); if(!n) return; n.attrs.draggable=!n.attrs.draggable; await pushHistory() }


/** ========= 导出 ========= */
function exportJSON(){ return { nodes: JSON.parse(JSON.stringify(nodes)).map(n=>{ if(n.attrs?.fillPatternImage) delete n.attrs.fillPatternImage; return n }) } }
async function exportPNG(){ return stageRef.value.getNode().toDataURL({ pixelRatio: 2 }) }
async function doExport(){ return { json: exportJSON(), png: await exportPNG() } }

/** ========= 页面按钮 ========= */
function goPrev(){ emit('prev') }

async function goNext(){
  if (!canProceed.value) return
  await exportCurrent()
  if (nodes.length > 0) {
    try {
      const editedImageData = await exportPNG()
      // 保存编辑后的图片到 store，这样 canGoNext 就能检测到
      store.saveImageEdit({
        editedImage: editedImageData,
        hasEdited: true
      })
    } catch (error) { console.error('保存编辑后图片失败:', error) }
  }
  emit('next', { annotations: JSON.parse(JSON.stringify(annotations)), snapshots: JSON.parse(JSON.stringify(snapshots)) })
}

/** ========= 自适应 & 快捷键 ========= */
function handleKey(e){
  // 撤销 / 重做（Ctrl/Cmd+Z / Ctrl+Shift+Z / Ctrl+Y）
  const isMeta = e.ctrlKey || e.metaKey
  const key = e.key.toLowerCase()
  if (isMeta && key === 'z') { e.shiftKey ? redo() : undo(); e.preventDefault() }
  if (isMeta && key === 'y') { redo(); e.preventDefault() }
}
onMounted(async ()=>{ 
  await nextTick()
  await pushHistory()
  if (wrapRef.value) { const ro = new ResizeObserver(()=>fit()); ro.observe(wrapRef.value) }
  const down = (e) => { if (e.code === 'Space') panHeld.value = true }
  const up   = (e) => { if (e.code === 'Space') panHeld.value = false }
  window.addEventListener('keydown', down)
  window.addEventListener('keyup', up)
  window.addEventListener('keydown', handleKey)
})
onBeforeUnmount(()=>{ window.removeEventListener('keydown', handleKey) })

/** 当前图片切换时，把上一张的状态保存一下（可选） */
watch(currentId, async (newId, oldId) => {
  closeFillMenu()
  if (oldId && nodes.length) {
    const out = await doExport()
    annotations[oldId] = out.json
    snapshots[oldId]   = out.png
  }
})

/** ========= RDP 简化（圈选路径平滑） ========= */
function rdpSimplify(points, tolerance = 1.0) {
  if (!points || points.length <= 4) return points
  const pts = []
  for (let i = 0; i < points.length; i += 2) pts.push({ x: points[i], y: points[i+1] })
  const keep = new Array(pts.length).fill(false)
  keep[0] = keep[pts.length - 1] = true
  function sqr(x){ return x*x }
  function dist2(a,b){ return sqr(a.x-b.x)+sqr(a.y-b.y) }
  function distToSeg2(p,a,b){
    const l2 = dist2(a,b); if (l2 === 0) return dist2(p,a)
    let t = ((p.x-a.x)*(b.x-a.x)+(p.y-a.y)*(b.y-a.y))/l2
    t = Math.max(0, Math.min(1, t))
    return dist2(p, { x: a.x + t*(b.x-a.x), y: a.y + t*(b.y-a.y) })
  }
  const tol2 = tolerance*tolerance
  const stack = [[0, pts.length-1]]
  while (stack.length) {
    const [s,e] = stack.pop()
    let idx = -1, maxd = 0
    for (let i=s+1;i<e;i++){
      const d = distToSeg2(pts[i], pts[s], pts[e])
      if (d > maxd){ idx = i; maxd = d }
    }
    if (maxd > tol2 && idx !== -1){
      keep[idx] = true
      stack.push([s, idx], [idx, e])
    }
  }
  const out = []
  for (let i=0;i<pts.length;i++){ if (keep[i]) { out.push(pts[i].x, pts[i].y) } }
  if (out.length >= 4 && (out[0] !== out[out.length-2] || out[1] !== out[out.length-1])) {
    out.push(out[0], out[1])
  }
  return out
}



/** ========= 移到功能 ========= */
async function onDragEnd(id, evt) {
  const n = nodes.find(x => x.id === id)
  if (!n) return
  const k = evt?.target
  if (!k) return

  // 不同图形通用：Konva 会更新 x/y，记录下来即可
  n.attrs.x = k.x()
  n.attrs.y = k.y()

  // 线/箭头如果你允许缩放或画布有 scale，也可以根据需要写 points（此处先不改 points）
  await pushHistory()
  stageRef.value?.getNode()?.batchDraw()
}

async function onTransformEnd(id, evt) {
  const n = nodes.find(x => x.id === id)
  if (!n) return
  const k = evt?.target
  if (!k) return

  // 根据类型把变形后的属性写回 attrs
  if (n.type === 'rect') {
    // 读取缩放后的新宽高，并重置 scale，把变形固化到宽高上
    const scaleX = k.scaleX(); const scaleY = k.scaleY()
    n.attrs.x = k.x(); n.attrs.y = k.y()
    n.attrs.width  = Math.max(1, (n.attrs.width  || k.width())  * scaleX)
    n.attrs.height = Math.max(1, (n.attrs.height || k.height()) * scaleY)
    k.scaleX(1); k.scaleY(1)
  } else if (n.type === 'circle') {
    const scaleX = k.scaleX()
    n.attrs.x = k.x(); n.attrs.y = k.y()
    n.attrs.radius = Math.max(1, (n.attrs.radius || 0) * scaleX)
    k.scaleX(1); k.scaleY(1)
  } else {
    // 其它类型：至少把位移持久化
    n.attrs.x = k.x(); n.attrs.y = k.y()
  }

  await pushHistory()
  stageRef.value?.getNode()?.batchDraw()
}

function toggleMoveMode() {
  isMoveMode.value = !isMoveMode.value
  if (isMoveMode.value) {
    currentTool.value = '选择'
    historyVer.value++       // 让 draggable 生效
  } else {
    historyVer.value++       // 还原 draggable
  }
}

/** ========= 清除所有更改功能 ========= */
async function clearAllChanges() {
  if (nodes.length === 0) return
  
  // 确认对话框
  if (confirm('确定要清除所有绘图痕迹吗？此操作不可撤销。')) {
    // 清空所有节点
    nodes.splice(0, nodes.length)
    
    // 退出移到模式
    isMoveMode.value = false
    
    // 关闭填充菜单
    closeFillMenu()
    
    // 保存到历史记录
    await pushHistory()
    
    // 强制重绘
    stageRef.value?.getNode()?.batchDraw()
  }
}

/** 工具切换 & 其它 */
function selectTool(tool) {
  currentTool.value = tool
  if (!['矩形','圆形','自由线','圈选填充','箭头'].includes(tool)) {
    isDrawing = false; tempRect.value = null; tempCircle.value = null; tempLine.value = null
  }
  // 切换到其他工具时退出移到模式
  if (isMoveMode.value && tool !== '选择') {
    isMoveMode.value = false
    historyVer.value++       // 还原 draggable
  }
}
</script>

<style scoped>
.page-card { width:100%; }
.header { margin-bottom: 12px; }
.title { font-size:16px; font-weight:600; }
.desc { color:#8c8c8c; margin-top:4px; }
.empty-wrap { padding: 48px 0; }

.validation-status { margin-top: 20px; padding: 12px 16px; background: #fff7e6; border: 1px solid #ffd591; border-radius: 6px; }
.validation-message { display: flex; align-items: center; gap: 8px; color: #d46b08; font-size: 14px; }

.editor-wrap { display:flex; gap:12px; min-height: 560px; }
.thumbs { width: 220px; border:1px solid #eee; border-radius:12px; padding:8px; overflow:auto; background:#fff; }
.thumb { border:1px solid transparent; border-radius:10px; padding:6px; cursor:pointer; }
.thumb + .thumb { margin-top:8px; }
.thumb.active { border-color:#1677ff; background:#f0f6ff; }
.thumb-name { margin-top:6px; font-size:12px; color:#666; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; }

.canvas { flex:1; min-width:0; position: relative; }
.stage-wrap { position:relative; width:100%; height: 520px; background:#f7f7f7; border:1px solid #eee; border-radius:12px; overflow:hidden; }
.stage-wrap.moving { cursor: move; }

/* 下拉菜单UI */
.fill-menu {
  position: absolute;
  z-index: 20;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 10px;
  padding: 8px;
  width: 200px;
  box-shadow: 0 10px 24px rgba(0,0,0,.12);
}

.toolbar { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-top:8px; }
.tool {
  padding:6px 10px; border:1px solid #ddd; background:#fff; border-radius:8px;
  cursor:pointer; color:#333; font-size:14px; font-weight:500; transition: all 0.2s ease;
}
.tool:hover { background:#f5f5f5; border-color:#999; }
.tool.active { border-color:#ff2d55; background:#fff5f5; color:#ff2d55; }
.tool:disabled { opacity:0.5; cursor:not-allowed; }

.toolbar select.tool { min-width: 120px; color:#333; font-size:14px; }
.toolbar label.tool { display: flex; align-items: center; gap: 4px; color:#333; font-size:14px; }
.toolbar label.tool input { width: 50px; padding: 2px 4px; border: 1px solid #ddd; border-radius: 4px; text-align: center; }

.tips { margin-top:8px; color:#8c8c8c; font-size:12px; }
.footer { display:flex; justify-content:space-between; align-items:center; margin-top:16px; }
.right { display:flex; gap:8px; }
</style>

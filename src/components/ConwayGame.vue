<template>
  <el-row justify="end" class="help">
    <el-affix target=".help">
      <HelpIcon @click="showHelp" />
    </el-affix>
  </el-row>
  <el-row justify="center">
    <div class="p5-container" ref="p5Canvas"></div>
  </el-row>
  <el-row justify="center">
    <el-button type="primary" @click="toggleRun">{{ isRunning ? 'Pause' : 'Start' }}</el-button>
    <el-button type="primary" @click="randomize">Randomize</el-button>
    <el-button type="primary" @click="clear">Clear</el-button>
  </el-row>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import p5 from 'p5'
import { ElMessage, ElMessageBox } from 'element-plus'
import HelpIcon from '@/components/icons/IconHelp.vue'
import shaderCode from '@/conway.wgsl?raw'

const p5Canvas = ref<HTMLElement | null>(null)
let sketch: p5
let port: number | null = null
const cellSize = 20
let columnCount: number
let rowCount: number
let currentCells: number[][] = []
let nextCells: number[][] = []

const isRunning = ref(false)
const deviceRef = ref<GPUDevice | null>(null)

const initP5 = () => {
  if (p5Canvas.value === null) {
    return
  }
  sketch = new p5((p: p5) => {
    p.setup = async () => {
      port = await window.electronAPI.getPort()
      p.frameRate(10)
      p.createCanvas(600, 600)
      columnCount = p.width / cellSize
      rowCount = p.height / cellSize
      for (let i = 0; i < columnCount; i++) {
        currentCells[i] = Array(rowCount).fill(0)
        nextCells[i] = Array(rowCount).fill(0)
      }
      p.noLoop()
      refresh()
    }
    p.draw = async () => {
      await generateGPU()
      refresh()
      await send()
    }
    p.mousePressed = () => {
      if (!isRunning.value) {
        const col = Math.floor(p.mouseX / cellSize)
        const row = Math.floor(p.mouseY / cellSize)
        if (col >= 0 && col < columnCount && row >= 0 && row < rowCount) {
          currentCells[col][row] = currentCells[col][row] ? 0 : 1
          p.fill(currentCells[col][row] ? 0 : 255)
          p.rect(col * cellSize, row * cellSize, cellSize, cellSize)
          send()
        }
      }
    }
  }, p5Canvas.value)
}
const toggleRun = () => {
  if (isRunning.value) {
    sketch.noLoop()
  } else {
    sketch.loop()
  }
  isRunning.value = !isRunning.value
}
const randomize = async () => {
  for (let i = 0; i < columnCount; i++) {
    for (let j = 0; j < rowCount; j++) {
      currentCells[i][j] = sketch.random([0, 1])
    }
  }
  refresh()
  await send()
}
const clear = async () => {
  for (let i = 0; i < columnCount; i++) {
    currentCells[i].fill(0)
  }
  isRunning.value = false
  sketch.noLoop()
  refresh()
  await send()
}
const refresh = () => {
  for (let i = 0; i < columnCount; i++) {
    for (let j = 0; j < rowCount; j++) {
      sketch.fill(currentCells[i][j] ? 0 : 255)
      sketch.stroke(0)
      sketch.rect(i * cellSize, j * cellSize, cellSize, cellSize)
    }
  }
}
const getMiddleMatrix = () => {
  const midCol = Math.floor(columnCount / 2)
  const midRow = Math.floor(rowCount / 2)
  const startCol = Math.max(midCol - 8, 0)
  const startRow = Math.max(midRow - 8, 0)
  return currentCells.slice(startCol, startCol + 16).map(row => row.slice(startRow, startRow + 16))
}
const send = async () => {
  const middleMatrix = getMiddleMatrix()
  const response = await fetch(`http://localhost:${port}/api/conway`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ matrix: middleMatrix })
  })
  if (!response.ok) {
    const errorData = await response.json()
    ElMessage.warning('The COM port is currently unavailable, use Visual Connection.')
    console.error(errorData.detail || 'Unknown Error')
  }
}
const initGPU = async () => {
  if (!navigator.gpu) {
    console.warn('WebGPU not supported.')
    return
  }
  try {
    const adapter = await navigator.gpu.requestAdapter()
    if (!adapter) {
      console.warn('No GPU adapter found.')
      return
    }
    const device = await adapter.requestDevice()
    deviceRef.value = device
  } catch (error) {
    console.error('Failed to initialize WebGPU:', error)
  }
}

const generateGPU = async () => {
  if (!deviceRef.value) {
    console.warn('GPU device not initialized.')
    return
  }
  const device = deviceRef.value

  // 将二维数组打平：currentCells -> Float32Array
  const flattenedCurrent = new Float32Array(columnCount * rowCount)
  for (let i = 0; i < columnCount; i++) {
    for (let j = 0; j < rowCount; j++) {
      flattenedCurrent[i * rowCount + j] = currentCells[i][j]
    }
  }

  // 创建 GPUBuffer
  const currentBuffer = device.createBuffer({
    size: flattenedCurrent.byteLength,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST
  })
  const nextBuffer = device.createBuffer({
    size: flattenedCurrent.byteLength,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC
  })

  // 构建着色器
  const bindGroupLayout = device.createBindGroupLayout({
    entries: [
      {
        binding: 0,
        visibility: GPUShaderStage.COMPUTE,
        buffer: { type: 'read-only-storage' }
      },
      {
        binding: 1,
        visibility: GPUShaderStage.COMPUTE,
        buffer: { type: 'storage' }
      },
      {
        binding: 2,
        visibility: GPUShaderStage.COMPUTE,
        buffer: { type: 'uniform' }
      }
    ]
  })
  const pipelineLayout = device.createPipelineLayout({
    bindGroupLayouts: [bindGroupLayout]
  })

  // 上传 currentCells
  device.queue.writeBuffer(currentBuffer, 0, flattenedCurrent)

  // Uniform buffer: [columnCount, rowCount]
  const dimensionBuffer = device.createBuffer({
    size: 8,
    usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST
  })
  const dimensionData = new Uint32Array([columnCount, rowCount])
  device.queue.writeBuffer(dimensionBuffer, 0, dimensionData)

  // 创建着色器模块 & 管线
  const shaderModule = device.createShaderModule({ code: shaderCode })
  const pipeline = device.createComputePipeline({
    layout: pipelineLayout,
    compute: {
      module: shaderModule,
      entryPoint: 'main'
    }
  })

  // 绑定资源
  const bindGroup = device.createBindGroup({
    layout: pipeline.getBindGroupLayout(0),
    entries: [
      { binding: 0, resource: { buffer: currentBuffer } },
      { binding: 1, resource: { buffer: nextBuffer } },
      { binding: 2, resource: { buffer: dimensionBuffer } }
    ]
  })

  // 执行计算
  const commandEncoder = device.createCommandEncoder()
  const passEncoder = commandEncoder.beginComputePass()
  passEncoder.setPipeline(pipeline)
  passEncoder.setBindGroup(0, bindGroup)
  passEncoder.dispatchWorkgroups(
    Math.ceil(columnCount / 16),
    Math.ceil(rowCount / 16)
  )
  passEncoder.end()
  device.queue.submit([commandEncoder.finish()])

  // 读取结果
  const readBuffer = device.createBuffer({
    size: flattenedCurrent.byteLength,
    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ
  })
  const copyEncoder = device.createCommandEncoder()
  copyEncoder.copyBufferToBuffer(nextBuffer, 0, readBuffer, 0, flattenedCurrent.byteLength)
  device.queue.submit([copyEncoder.finish()])

  await readBuffer.mapAsync(GPUMapMode.READ)
  const newData = new Float32Array(readBuffer.getMappedRange())
  // 更新 nextCells & currentCells
  for (let i = 0; i < columnCount; i++) {
    for (let j = 0; j < rowCount; j++) {
      nextCells[i][j] = newData[i * rowCount + j]
    }
  }
  readBuffer.unmap()

  // 交换
  const temp = currentCells
  currentCells = nextCells
  nextCells = temp
}

onMounted(() => {
  initP5()
  initGPU()
})
const showHelp = () => {
  sketch.noLoop()
  isRunning.value = true
  ElMessageBox.alert(
    `<div>
       <p>Conway's Game of Life is a zero-player game that simulates the birth and death of cells based on simple rules.</p>
       <p>The rules are as follows:</p>
       <ol>
         <li>Any live cell with fewer than two live neighbours dies, as if by underpopulation.</li>
         <li>Any live cell with two or three live neighbours lives on to the next generation.</li>
         <li>Any live cell with more than three live neighbours dies, as if by overpopulation.</li>
         <li>Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.</li>
       </ol>
       <p>For more information, please visit <a href="https://en.wikipedia.org/wiki/Conway's_Game_of_Life" target="_blank">Wikipedia</a>。</p>
     </div>`,
    'Help',
    {
      dangerouslyUseHTMLString: true,
      callback: () => {
        isRunning.value = false
      }
    }
  )
}
</script>

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

const p5Canvas = ref<HTMLElement | null>(null)
let sketch: p5
let port: number | null = null
const cellSize = 20
let columnCount: number
let rowCount: number
let currentCells: number[][] = []
let nextCells: number[][] = []

const isRunning = ref(false)

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
    }
    p.draw = async () => {
      generate()
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
    const generate = () => {
      for (let i = 0; i < columnCount; i++) {
        for (let j = 0; j < rowCount; j++) {
          const neighbors = countNeighbors(i, j)
          if (currentCells[i][j] === 1) {
            if (neighbors < 2 || neighbors > 3) {
              nextCells[i][j] = 0
            } else {
              nextCells[i][j] = 1
            }
          } else {
            if (neighbors === 3) {
              nextCells[i][j] = 1
            } else {
              nextCells[i][j] = 0
            }
          }
        }
      }
      const temp = currentCells
      currentCells = nextCells
      nextCells = temp
    }
    const countNeighbors = (x: number, y: number) => {
      let sum = 0
      for (let i = -1; i < 2; i++) {
        for (let j = -1; j < 2; j++) {
          const col = (x + i + columnCount) % columnCount
          const row = (y + j + rowCount) % rowCount
          sum += currentCells[col][row]
        }
      }
      sum -= currentCells[x][y]
      return sum
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
onMounted(() => {
  initP5()
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

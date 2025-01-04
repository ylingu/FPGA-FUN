<template>
  <el-row justify="center">
    <canvas id="number" width="512px" height="512px" />
  </el-row>
  <el-row class="spacer-2"></el-row>
  <el-row justify="center">
    <el-button-group>
      <el-button type="primary" @click="clear">Clear</el-button>
      <el-button type="primary" @click="predict">Predict</el-button>
    </el-button-group>
  </el-row>
  <el-row justify="center">
    <el-text v-if="prediction !== null" size="large" type="info">Prediction: {{ prediction }}</el-text>
  </el-row>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Canvas, PencilBrush } from 'fabric'
import { dataURLtoBlob } from '@/utils'
import { ElMessage } from 'element-plus'

let canvas: Canvas | null = null
let port: number | null = null
const prediction = ref<number | null>(null)

onMounted(() => {
  canvas = new Canvas('number', { isDrawingMode: true })
  canvas.backgroundColor = 'white'
  canvas.freeDrawingBrush = new PencilBrush(canvas)
  canvas.freeDrawingBrush.width = 30
  canvas.freeDrawingBrush.color = 'black'
})

const clear = () => {
  canvas?.clear()
  canvas!.backgroundColor = 'white'
  prediction.value = null
}

const predict = async () => {
  port = await window.electronAPI.getPort()
  const dataURL = canvas!.toDataURL({
    format: 'png',
    quality: 1,
    multiplier: 0.0625 // 将512x512转为32x32，减小传输时延便于后端预测
  })
  let blob: Blob
  try {
    blob = dataURLtoBlob(dataURL)
  } catch (error) {
    console.error('Error converting data URL to blob:', error)
    return
  }
  const formData = new FormData()
  formData.append('file', blob, 'canvas.png')

  try {
    const response = await fetch(`http://localhost:${port}/api/predict`, {
      method: 'POST',
      body: formData
    })
    if (!response.ok) {
      const errorData = await response.json()
      ElMessage.warning('The COM port is currently unavailable, use Visual Connection.')
      throw new Error(errorData.detail || 'Unknown Error')
    }
    const data = await response.json()
    prediction.value = data.result
  } catch (error) {
    console.error(error)
  }
}
</script>

<style scoped>
canvas {
  border: 2px solid #000;
}

.spacer-2 {
  height: 2vh;
}
</style>

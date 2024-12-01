<template>
  <canvas id="number" width="512px" height="512px"></canvas>
  <el-button-group>
    <el-button type="primary" @click="clear">Clear</el-button>
    <el-button type="primary" @click="predict">Predict</el-button>
  </el-button-group>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Canvas, PencilBrush } from 'fabric'

let canvas: Canvas | null = null
let port: number | null = null

onMounted(() => {
  canvas = new Canvas('number', { isDrawingMode: true })
  canvas.backgroundColor = 'white'
  canvas.freeDrawingBrush = new PencilBrush(canvas)
  canvas.freeDrawingBrush.width = 30
  canvas.freeDrawingBrush.color = 'black'
})

const dataURLtoBlob = (dataurl: string): Blob => {
  const arr = dataurl.split(',');
  const mimeMatch = arr[0].match(/:(.*?);/);
  if (!mimeMatch) {
    throw new Error('Invalid data URL');
  }
  const mime = mimeMatch[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);

  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }

  return new Blob([u8arr], { type: mime });
}

const clear = () => {
  canvas?.clear()
  canvas!.backgroundColor = 'white'
}

const predict = async () => {
  port = await window.electronAPI.getPort()
  const dataURL = canvas!.toDataURL({
    format: 'png',
    quality: 1,
    multiplier: 1
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
    await fetch(`http://localhost:${port}/api/predict`, {
      method: 'POST',
      body: formData
    })
  } catch (error) {
    console.error('Error uploading image:', error)

  }
}
</script>

<style scoped>
canvas {
  border: 2px solid #000;
}
</style>

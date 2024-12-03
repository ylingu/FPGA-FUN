<template>
  <el-main class="home-container">
    <el-row justify="center">
      <el-text tag="h1">FPGA FUN</el-text>
    </el-row>
    <el-row class="spacer-20"></el-row>
    <el-row justify="center">
      <el-col :span="11"><el-text tag="h2">Select a serial port to start</el-text></el-col>
    </el-row>
    <el-row class="spacer-2"></el-row>
    <el-row justify="center">
      <el-col :span="7">
        <el-select v-model="com" placeholder="Select" @focus="fetchSerialPorts">
          <el-option v-for="serialPort in serialPorts" :key="serialPort" :label="serialPort" :value="serialPort" />
        </el-select>
      </el-col>
      <el-col :span="3" :offset="1">
        <el-button type="primary" :icon="Cpu" @click="() => {
          $router.push('/apps/number')
          createCom()
        }">Start</el-button>
      </el-col>
    </el-row>
  </el-main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Cpu } from '@element-plus/icons-vue'

const serialPorts = ref<string[]>([])
const com = ref('')

const fetchSerialPorts = async () => {
  const port = await window.electronAPI.getPort()
  try {
    const response = await fetch(`http://localhost:${port}/api/serial_ports`, {
      method: 'GET',
    })
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Unknown Error')
    }
    const data = await response.json()
    serialPorts.value = data.serial_ports
  }
  catch (error) {
    console.error(error)
  }
}

const createCom = async () => {
  const port = await window.electronAPI.getPort()
  try {
    const response = await fetch(`http://localhost:${port}/api/create_com/${com.value}`, {
      method: 'POST',
    })
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Unknown Error')
    }
  }
  catch (error) {
    console.error(error)
  }
}

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Space+Grotesk:wght@300..700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Funnel+Sans:ital,wght@0,300..800;1,300..800&family=Silkscreen:wght@400;700&family=Space+Grotesk:wght@300..700&display=swap');

.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #9fb1ff 0%, hwb(256 41% 0%) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.spacer-20 {
  height: 20vh;
}

.spacer-2 {
  height: 2vh;
}

h1 {
  font-family: "Silkscreen", sans-serif;
  font-weight: 500;
  font-size: 10vw;
  user-select: none;
  color: #bcff3fc9;
}

h2 {
  font-family: "Funnel Sans", sans-serif;
  font-size: 2vw;
  user-select: none;
  color: #000000de;
}
</style>

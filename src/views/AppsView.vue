<template>
  <el-aside>
    <el-menu default-active="1">
      <el-menu-item index="1" @click="$router.push('/apps/number')">
        <el-icon>
          <Counter8Icon />
        </el-icon>
        Handwritten Digit Recognition
      </el-menu-item>
      <el-menu-item index="2" @click="$router.push('/apps/conway')">
        <el-icon>
          <SmartToyIcon />
        </el-icon>
        Conway's Game of Life
      </el-menu-item>
    </el-menu>
  </el-aside>
  <el-main>
    <RouterView />
  </el-main>
</template>

<script setup lang="ts">
import Counter8Icon from '@/components/icons/IconCounter8.vue'
import SmartToyIcon from '@/components/icons/IconSmartToy.vue'
</script>

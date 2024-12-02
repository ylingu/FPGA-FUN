<template>
  <el-aside>
    <el-menu default-active="1">
      <el-menu-item index="1" @click="$router.push('/apps/number')">
        <el-icon>
          <Counter8Icon />
        </el-icon>
        Handwritten digit recognition
      </el-menu-item>
    </el-menu>
  </el-aside>
  <el-main>
    <RouterView />
  </el-main>
</template>

<script setup lang="ts">
import Counter8Icon from '@/components/icons/IconCounter8.vue'
</script>

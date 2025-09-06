<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  try {
    // 初始化应用
    if (authStore.initializeAuth && typeof authStore.initializeAuth === 'function') {
      await authStore.initializeAuth()
    }
  } catch (error) {
    console.error('初始化认证失败:', error)
  }
})
</script>

<style>
#app {
  height: 100vh;
  width: 100vw;
}
</style>

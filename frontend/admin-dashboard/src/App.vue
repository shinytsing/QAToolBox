<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // 初始化应用
  authStore.initializeAuth()
})
</script>

<style>
#app {
  height: 100vh;
  width: 100vw;
}
</style>

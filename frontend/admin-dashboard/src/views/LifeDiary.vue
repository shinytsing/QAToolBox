<template>
  <div class="life-diary">
    <div class="page-header">
      <h2>日记管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增日记
      </el-button>
    </div>
    <el-card>
      <p>生活日记管理功能开发中...</p>
      <el-button type="primary" @click="$router.back()">返回</el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const showCreateDialog = ref(false)
</script>

<style scoped>
.life-diary { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
</style>

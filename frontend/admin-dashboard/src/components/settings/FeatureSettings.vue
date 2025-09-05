<template>
  <div class="feature-settings">
    <el-form :model="features" label-width="120px">
      <el-form-item label="健身模块">
        <el-switch v-model="features.fitness" />
      </el-form-item>
      <el-form-item label="生活工具">
        <el-switch v-model="features.lifeTools" />
      </el-form-item>
      <el-form-item label="极客工具">
        <el-switch v-model="features.geekTools" />
      </el-form-item>
      <el-form-item label="社交娱乐">
        <el-switch v-model="features.social" />
      </el-form-item>
      <el-form-item label="分享功能">
        <el-switch v-model="features.share" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSave">保存设置</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const features = reactive({
  fitness: true,
  lifeTools: true,
  geekTools: true,
  social: true,
  share: true
})

const handleSave = () => {
  ElMessage.success('功能设置保存成功')
}

const handleReset = () => {
  Object.assign(features, {
    fitness: true,
    lifeTools: true,
    geekTools: true,
    social: true,
    share: true
  })
  ElMessage.info('功能设置已重置')
}
</script>

<style scoped>
.feature-settings {
  padding: 20px;
}
</style>

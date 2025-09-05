<template>
  <div class="api-settings">
    <el-form :model="api" label-width="120px">
      <el-form-item label="API版本">
        <el-input v-model="api.version" />
      </el-form-item>
      <el-form-item label="API限流">
        <el-switch v-model="api.rateLimit" />
      </el-form-item>
      <el-form-item label="每分钟请求数">
        <el-input-number v-model="api.requestsPerMinute" :min="10" :max="1000" />
      </el-form-item>
      <el-form-item label="API文档">
        <el-switch v-model="api.documentation" />
      </el-form-item>
      <el-form-item label="调试模式">
        <el-switch v-model="api.debug" />
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

const api = reactive({
  version: 'v1',
  rateLimit: true,
  requestsPerMinute: 100,
  documentation: true,
  debug: false
})

const handleSave = () => {
  ElMessage.success('API设置保存成功')
}

const handleReset = () => {
  Object.assign(api, {
    version: 'v1',
    rateLimit: true,
    requestsPerMinute: 100,
    documentation: true,
    debug: false
  })
  ElMessage.info('API设置已重置')
}
</script>

<style scoped>
.api-settings {
  padding: 20px;
}
</style>

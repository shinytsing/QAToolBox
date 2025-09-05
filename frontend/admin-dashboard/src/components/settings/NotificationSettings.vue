<template>
  <div class="notification-settings">
    <el-form :model="notifications" label-width="120px">
      <el-form-item label="邮件通知">
        <el-switch v-model="notifications.email" />
      </el-form-item>
      <el-form-item label="短信通知">
        <el-switch v-model="notifications.sms" />
      </el-form-item>
      <el-form-item label="推送通知">
        <el-switch v-model="notifications.push" />
      </el-form-item>
      <el-form-item label="系统通知">
        <el-switch v-model="notifications.system" />
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

const notifications = reactive({
  email: true,
  sms: false,
  push: true,
  system: true
})

const handleSave = () => {
  ElMessage.success('通知设置保存成功')
}

const handleReset = () => {
  Object.assign(notifications, {
    email: true,
    sms: false,
    push: true,
    system: true
  })
  ElMessage.info('通知设置已重置')
}
</script>

<style scoped>
.notification-settings {
  padding: 20px;
}
</style>

<template>
  <div class="security-settings">
    <el-form :model="security" label-width="120px">
      <el-form-item label="密码最小长度">
        <el-input-number v-model="security.minPasswordLength" :min="6" :max="20" />
      </el-form-item>
      <el-form-item label="登录失败锁定">
        <el-switch v-model="security.loginLock" />
      </el-form-item>
      <el-form-item label="锁定次数">
        <el-input-number v-model="security.lockCount" :min="3" :max="10" />
      </el-form-item>
      <el-form-item label="锁定时间(分钟)">
        <el-input-number v-model="security.lockTime" :min="5" :max="60" />
      </el-form-item>
      <el-form-item label="启用双因素认证">
        <el-switch v-model="security.twoFactor" />
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

const security = reactive({
  minPasswordLength: 8,
  loginLock: true,
  lockCount: 5,
  lockTime: 15,
  twoFactor: false
})

const handleSave = () => {
  ElMessage.success('安全设置保存成功')
}

const handleReset = () => {
  Object.assign(security, {
    minPasswordLength: 8,
    loginLock: true,
    lockCount: 5,
    lockTime: 15,
    twoFactor: false
  })
  ElMessage.info('安全设置已重置')
}
</script>

<style scoped>
.security-settings {
  padding: 20px;
}
</style>

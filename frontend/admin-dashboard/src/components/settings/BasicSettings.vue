<template>
  <div class="basic-settings">
    <el-form :model="settings" label-width="120px">
      <el-form-item label="网站名称">
        <el-input v-model="settings.siteName" />
      </el-form-item>
      <el-form-item label="网站描述">
        <el-input v-model="settings.siteDescription" type="textarea" />
      </el-form-item>
      <el-form-item label="网站Logo">
        <el-input v-model="settings.siteLogo" />
      </el-form-item>
      <el-form-item label="联系邮箱">
        <el-input v-model="settings.contactEmail" />
      </el-form-item>
      <el-form-item label="联系电话">
        <el-input v-model="settings.contactPhone" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSave">保存设置</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const settings = reactive({
  siteName: 'QAToolBox',
  siteDescription: '多功能工具箱平台',
  siteLogo: '/logo.png',
  contactEmail: 'contact@qatoolbox.com',
  contactPhone: '400-123-4567'
})

const handleSave = () => {
  ElMessage.success('设置保存成功')
}

const handleReset = () => {
  Object.assign(settings, {
    siteName: 'QAToolBox',
    siteDescription: '多功能工具箱平台',
    siteLogo: '/logo.png',
    contactEmail: 'contact@qatoolbox.com',
    contactPhone: '400-123-4567'
  })
  ElMessage.info('设置已重置')
}
</script>

<style scoped>
.basic-settings {
  padding: 20px;
}
</style>

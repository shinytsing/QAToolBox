<template>
  <div class="debug-container">
    <h2>调试登录页面</h2>
    
    <el-form :model="form" label-width="100px">
      <el-form-item label="用户名">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" />
      </el-form-item>
      <el-form-item label="设备类型">
        <el-input v-model="form.device_type" placeholder="web" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="testLogin" :loading="loading">测试登录</el-button>
        <el-button @click="clearLog">清除日志</el-button>
      </el-form-item>
    </el-form>
    
    <div class="log-container">
      <h3>调试日志</h3>
      <pre>{{ log }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const form = ref({
  username: 'testuser',
  password: 'testpass123',
  device_type: 'web'
})

const loading = ref(false)
const log = ref('')

const addLog = (message: string) => {
  log.value += `[${new Date().toLocaleTimeString()}] ${message}\n`
}

const clearLog = () => {
  log.value = ''
}

const testLogin = async () => {
  loading.value = true
  addLog('开始测试登录...')
  
  try {
    addLog(`发送请求到: /api/v1/auth/login/`)
    addLog(`请求数据: ${JSON.stringify(form.value, null, 2)}`)
    
    const response = await axios.post('/api/v1/auth/login/', form.value, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    addLog(`响应状态: ${response.status}`)
    addLog(`响应数据: ${JSON.stringify(response.data, null, 2)}`)
    
    if (response.data.success) {
      addLog('✅ 登录成功!')
    } else {
      addLog('❌ 登录失败: ' + response.data.message)
    }
    
  } catch (error: any) {
    addLog(`❌ 请求错误: ${error.message}`)
    if (error.response) {
      addLog(`错误状态: ${error.response.status}`)
      addLog(`错误数据: ${JSON.stringify(error.response.data, null, 2)}`)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.debug-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.log-container {
  margin-top: 20px;
  border: 1px solid #ddd;
  padding: 10px;
  background-color: #f5f5f5;
  max-height: 400px;
  overflow-y: auto;
}

pre {
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 12px;
}
</style>

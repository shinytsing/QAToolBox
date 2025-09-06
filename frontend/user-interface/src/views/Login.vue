<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-left">
        <div class="welcome-text">
          <h1>欢迎来到 QAToolBox</h1>
          <p>多功能工具箱平台，让生活更简单</p>
          <div class="features">
            <div class="feature-item">
              <el-icon><Trophy /></el-icon>
              <span>健身管理</span>
            </div>
            <div class="feature-item">
              <el-icon><Tools /></el-icon>
              <span>极客工具</span>
            </div>
            <div class="feature-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>社交娱乐</span>
            </div>
            <div class="feature-item">
              <el-icon><Sunny /></el-icon>
              <span>生活助手</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="login-right">
        <div class="login-form-container">
          <div class="login-header">
            <img src="/logo.svg" alt="QAToolBox" class="logo" />
            <h2>登录账号</h2>
            <p>使用您的账号登录 QAToolBox</p>
          </div>
          
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名或邮箱"
                size="large"
                prefix-icon="User"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            
            <el-form-item>
              <div class="login-options">
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                <el-link type="primary" :underline="false">忘记密码？</el-link>
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="authStore.loading"
                @click="handleLogin"
                class="login-btn"
              >
                {{ authStore.loading ? '登录中...' : '登录' }}
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="login-footer">
            <p>还没有账号？<el-link type="primary" @click="showRegister = true">立即注册</el-link></p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 注册对话框 -->
    <el-dialog
      v-model="showRegister"
      title="注册新账号"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="first_name">
          <el-input v-model="registerForm.first_name" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" @click="handleRegister" :loading="authStore.loading">
          注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import type { LoginCredentials, RegisterData } from '@/types/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()
const showRegister = ref(false)
const rememberMe = ref(false)

// 登录表单
const loginForm = reactive<LoginCredentials>({
  username: '',
  password: ''
})

// 注册表单
const registerForm = reactive<RegisterData>({
  username: '',
  email: '',
  password: '',
  first_name: ''
})

// 登录验证规则
const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 注册验证规则
const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能少于3位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      const result = await authStore.login(loginForm)
      if (result.success) {
        ElMessage.success('登录成功')
        router.push('/')
      } else {
        ElMessage.error(result.error || '登录失败')
      }
    }
  })
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      const result = await authStore.register(registerForm)
      if (result.success) {
        ElMessage.success('注册成功，请登录')
        showRegister.value = false
        // 清空注册表单
        Object.assign(registerForm, {
          username: '',
          email: '',
          password: '',
          first_name: ''
        })
      } else {
        ElMessage.error(result.error || '注册失败')
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  max-width: 1000px;
  width: 100%;
  min-height: 600px;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.welcome-text h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.welcome-text p {
  font-size: 18px;
  margin-bottom: 32px;
  opacity: 0.9;
}

.features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  font-size: 16px;
}

.feature-item .el-icon {
  font-size: 20px;
  margin-right: 12px;
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-form-container {
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.login-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-form {
  margin-bottom: 24px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.login-footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
}

@media (max-width: 768px) {
  .login-content {
    flex-direction: column;
    max-width: 400px;
  }
  
  .login-left {
    display: none;
  }
  
  .login-right {
    padding: 20px;
  }
}
</style>

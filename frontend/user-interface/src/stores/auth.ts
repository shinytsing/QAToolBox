import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import type { User, LoginCredentials, RegisterData } from '@/types/auth'

// 创建独立的 axios 实例，避免循环依赖
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 添加请求拦截器
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 初始化认证状态
  const initializeAuth = async () => {
    if (token.value) {
      try {
        const response = await api.get('/auth/profile/')
        user.value = response.data
      } catch (error) {
        // Token无效，清除本地存储
        logout()
      }
    }
  }

  // 登录
  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    try {
      const response = await api.post('/auth/login/', credentials)
      const { data } = response.data
      
      if (data && data.tokens && data.user) {
        const { access_token, refresh_token } = data.tokens
        const userData = data.user
        
        token.value = access_token
        user.value = userData
        
        localStorage.setItem('token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        
        return { success: true }
      } else {
        return { 
          success: false, 
          error: '响应数据格式错误' 
        }
      }
    } catch (error: any) {
      console.error('登录错误:', error)
      return { 
        success: false, 
        error: error.response?.data?.message || error.response?.data?.detail || '登录失败' 
      }
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (data: RegisterData) => {
    loading.value = true
    try {
      const response = await api.post('/auth/register/', data)
      return { success: true, data: response.data }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || '注册失败' 
      }
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      if (token.value) {
        await api.post('/auth/logout/')
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      user.value = null
      token.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
    }
  }

  // 刷新Token
  const refreshToken = async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) return false

    try {
      const response = await api.post('/auth/refresh/', {
        refresh: refreshToken
      })
      const { access } = response.data
      token.value = access
      localStorage.setItem('token', access)
      return true
    } catch (error) {
      logout()
      return false
    }
  }

  // 更新用户信息
  const updateProfile = async (data: Partial<User>) => {
    try {
      const response = await api.patch('/auth/profile/', data)
      user.value = response.data
      return { success: true }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || '更新失败' 
      }
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    initializeAuth,
    login,
    register,
    logout,
    refreshToken,
    updateProfile
  }
})

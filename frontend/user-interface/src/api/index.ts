import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const authStore = useAuthStore()
    
    if (error.response?.status === 401) {
      // Token过期，尝试刷新
      const refreshed = await authStore.refreshToken()
      if (refreshed) {
        // 重新发送原请求
        const originalRequest = error.config
        originalRequest.headers.Authorization = `Bearer ${authStore.token}`
        return api(originalRequest)
      } else {
        // 刷新失败，跳转到登录页
        authStore.logout()
        window.location.href = '/login'
      }
    }
    
    // 显示错误消息
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    
    return Promise.reject(error)
  }
)

export { api }

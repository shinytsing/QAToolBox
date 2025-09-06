import axios from 'axios'
import { ElMessage } from 'element-plus'

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
    // 从localStorage获取token，避免循环依赖
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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
    if (error.response?.status === 401) {
      // Token过期，尝试刷新
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh/', {
            refresh: refreshToken
          })
          const { access } = response.data
          localStorage.setItem('token', access)
          
          // 重新发送原请求
          const originalRequest = error.config
          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        } catch (refreshError) {
          // 刷新失败，清除token并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        // 没有refresh token，直接跳转到登录页
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

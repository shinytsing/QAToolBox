import { defineStore } from 'pinia'
import { authAPI, type LoginRequest } from '@/api/auth'

export interface User {
  id: number
  username: string
  email: string
  is_staff: boolean
  is_superuser: boolean
}

export interface Device {
  device_id: string
  device_type: string
  device_name: string
  platform: string
  version: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    device: null as Device | null,
    accessToken: localStorage.getItem('access_token') || '',
    refreshToken: localStorage.getItem('refresh_token') || '',
    isLoggedIn: false,
  }),

  getters: {
    isAdmin: (state) => state.user?.is_superuser || false,
    isStaff: (state) => state.user?.is_staff || false,
  },

  actions: {
    // 登录
    async login(credentials: LoginRequest) {
      try {
        const response = await authAPI.login(credentials)
        
        if (response.success) {
          this.user = response.data.user
          this.device = response.data.device
          this.accessToken = response.data.access_token
          this.refreshToken = response.data.refresh_token
          this.isLoggedIn = true

          // 保存到本地存储
          localStorage.setItem('access_token', this.accessToken)
          localStorage.setItem('refresh_token', this.refreshToken)
          localStorage.setItem('user', JSON.stringify(this.user))
          localStorage.setItem('device', JSON.stringify(this.device))

          return { success: true, message: response.message }
        } else {
          return { success: false, message: response.message }
        }
      } catch (error: any) {
        return { 
          success: false, 
          message: error.response?.data?.message || '登录失败' 
        }
      }
    },

    // 登出
    async logout() {
      try {
        await authAPI.logout()
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        this.clearAuth()
      }
    },

    // 清除认证信息
    clearAuth() {
      this.user = null
      this.device = null
      this.accessToken = ''
      this.refreshToken = ''
      this.isLoggedIn = false

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      localStorage.removeItem('device')
    },

    // 初始化认证状态
    initAuth() {
      const user = localStorage.getItem('user')
      const device = localStorage.getItem('device')
      const accessToken = localStorage.getItem('access_token')

      if (user && device && accessToken) {
        this.user = JSON.parse(user)
        this.device = JSON.parse(device)
        this.accessToken = accessToken
        this.refreshToken = localStorage.getItem('refresh_token') || ''
        this.isLoggedIn = true
      }
    },

    // 刷新令牌
    async refreshAccessToken() {
      try {
        const response = await authAPI.refreshToken(this.refreshToken)
        
        if (response.success) {
          this.accessToken = response.data.access_token
          this.refreshToken = response.data.refresh_token
          
          localStorage.setItem('access_token', this.accessToken)
          localStorage.setItem('refresh_token', this.refreshToken)
          
          return true
        }
      } catch (error) {
        console.error('刷新令牌失败:', error)
        this.clearAuth()
      }
      return false
    }
  },

  persist: {
    key: 'qatoolbox-admin-auth',
    storage: localStorage,
    paths: ['user', 'device', 'accessToken', 'refreshToken', 'isLoggedIn']
  }
})
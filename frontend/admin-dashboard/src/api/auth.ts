import api from './index'

export interface LoginRequest {
  username: string
  password: string
  device_type: 'web' | 'miniprogram' | 'mobile'
  device_info?: {
    device_id?: string
    device_name?: string
    platform?: string
    version?: string
  }
}

export interface LoginResponse {
  success: boolean
  message: string
  data: {
    access_token: string
    refresh_token: string
    user: {
      id: number
      username: string
      email: string
      is_staff: boolean
      is_superuser: boolean
    }
    device: {
      device_id: string
      device_type: string
      device_name: string
      platform: string
      version: string
    }
    expires_in: number
  }
}

export const authAPI = {
  // 统一登录
  login: (data: LoginRequest): Promise<LoginResponse> => {
    return api.post('/auth/unified/login/', data)
  },

  // 刷新令牌
  refreshToken: (refreshToken: string): Promise<LoginResponse> => {
    return api.post('/auth/unified/refresh/', { refresh_token: refreshToken })
  },

  // 登出
  logout: (): Promise<any> => {
    return api.post('/auth/unified/logout/')
  },

  // 获取用户信息
  getUserInfo: (): Promise<any> => {
    return api.get('/auth/user/')
  },

  // 同步用户数据
  syncUserData: (data: { data_type: string; data: any }): Promise<any> => {
    return api.post('/auth/unified/sync/', data)
  }
}

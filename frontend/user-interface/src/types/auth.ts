export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  avatar?: string
  is_staff: boolean
  is_superuser: boolean
  date_joined: string
  last_login?: string
  is_active: boolean
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  first_name?: string
  last_name?: string
}

export interface AuthResponse {
  access: string
  refresh: string
  user: User
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface ApiResponse<T = unknown> {
  code: string
  message: string
  data: T | null
  timestamp: number
}

export interface PageResult<T = unknown> {
  records: T[]
  total: number
  page: number
  limit: number
}

export interface LoginRequest {
  username: string
  password: string
  captcha: string
}

export interface LoginResponse {
  token: string
  refreshToken: string
  userInfo: {
    userId: string
    name: string
    roleIds: string[]
  }
}

import request from '@/utils/request'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  accessToken: string
  refreshToken: string
  user: {
    userId: string
    username: string
    name: string
    deptId: string
    email: string
    phone: string
  }
}

export function login(data: LoginRequest) {
  return request<LoginResponse>({
    url: '/auth/login',
    method: 'post',
    data
  })
}

export function logout() {
  return request({
    url: '/auth/logout',
    method: 'post'
  })
}

export function refreshToken(refreshToken: string) {
  return request<LoginResponse>({
    url: '/auth/refresh',
    method: 'post',
    headers: {
      'X-Refresh-Token': refreshToken
    }
  })
}
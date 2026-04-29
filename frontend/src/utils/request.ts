import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// Request cancellation map
const pendingRequests = new Map<string, AbortController>()

function getRequestKey(config: any): string {
  return `${config.method}:${config.url}`
}

export function cancelAllPending(): void {
  pendingRequests.forEach((controller) => {
    controller.abort()
  })
  pendingRequests.clear()
}

service.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Cancel previous duplicate requests
    const key = getRequestKey(config)
    if (pendingRequests.has(key)) {
      pendingRequests.get(key)!.abort()
    }
    const controller = new AbortController()
    config.signal = controller.signal
    pendingRequests.set(key, controller)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response: AxiosResponse) => {
    // Clean up pending request
    const key = getRequestKey(response.config)
    pendingRequests.delete(key)

    const { code, message, data } = response.data
    if (code === 'SUCCESS' || code === '0') {
      return data
    }
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message))
  },
  (error) => {
    // Clean up pending request on error
    if (error.config) {
      const key = getRequestKey(error.config)
      pendingRequests.delete(key)
    }

    if (error.response?.status === 401) {
      sessionStorage.removeItem('token')
      localStorage.removeItem('token')
      router.push('/login')
    } else {
      const serverMsg = error.response?.data?.message
      if (serverMsg) {
        ElMessage.error(serverMsg)
      } else {
        ElMessage.error(error.message || '网络异常')
      }
    }
    return Promise.reject(error)
  }
)

export default service as {
  <T = unknown>(config: Parameters<AxiosInstance['request']>[0]): Promise<T>
  request<T = unknown>(config: Parameters<AxiosInstance['request']>[0]): Promise<T>
  get<T = unknown>(url: string, config?: unknown): Promise<T>
  post<T = unknown>(url: string, data?: unknown, config?: unknown): Promise<T>
  put<T = unknown>(url: string, data?: unknown, config?: unknown): Promise<T>
  delete<T = unknown>(url: string, config?: unknown): Promise<T>
}

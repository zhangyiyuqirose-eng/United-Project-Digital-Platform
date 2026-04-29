import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getUserInfo, logout as logoutApi } from '@/api/modules/system'
import type { UserInfoVO } from '@/api/modules/system'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(sessionStorage.getItem('token') || localStorage.getItem('token') || '')
  const userInfo = ref<UserInfoVO | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => userInfo.value?.name || '')
  const userRoles = computed(() => userInfo.value?.roles || [])
  const userPermissions = computed(() => userInfo.value?.permissions || [])

  async function login(username: string, password: string, rememberMe?: boolean) {
    const res = await loginApi({ username, password })
    token.value = res.token
    sessionStorage.setItem('token', res.token)
    if (rememberMe) {
      localStorage.setItem('token', res.token)
    }
    await fetchUserInfo()
  }

  async function fetchUserInfo() {
    try {
      userInfo.value = await getUserInfo()
    } catch {
      // ignore error, user info will be null
    }
  }

  async function logout() {
    try {
      await logoutApi()
    } catch {
      // ignore error
    }
    token.value = ''
    userInfo.value = null
    sessionStorage.removeItem('token')
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    userName,
    userRoles,
    userPermissions,
    login,
    fetchUserInfo,
    logout,
  }
})

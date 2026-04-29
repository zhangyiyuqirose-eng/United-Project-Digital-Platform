import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const sidebarCollapsed = ref(false)
  const theme = ref<'light' | 'dark'>('light')

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme.value)
    localStorage.setItem('updg-theme', theme.value)
  }

  function initTheme() {
    const saved = localStorage.getItem('updg-theme') as 'light' | 'dark' | null
    if (saved) {
      theme.value = saved
      document.documentElement.setAttribute('data-theme', saved)
    }
  }

  const isDark = computed(() => theme.value === 'dark')

  return { sidebarCollapsed, theme, isDark, toggleSidebar, toggleTheme, initTheme }
})

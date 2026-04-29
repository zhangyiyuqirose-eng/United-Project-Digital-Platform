<template>
  <button
    class="theme-toggle"
    @click="uiStore.toggleTheme"
    :title="uiStore.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
  >
    <svg v-if="uiStore.isDark" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.64 16.36l-1.42 1.42c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0l1.42-1.42c.39-.39.39-1.02 0-1.41-.39-.39-1.02-.39-1.41 0zm12.72 0l-1.42 1.42c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0l1.42-1.42c.39-.39.39-1.02 0-1.41-.39-.39-1.02-.39-1.41 0zM5.64 7.64l-1.42-1.42c-.39-.39-.39-1.02 0-1.41.39-.39 1.02-.39 1.41 0l1.42 1.42c.39.39.39 1.02 0 1.41-.39.39-1.02.39-1.41 0zm12.72 0l1.42-1.42c.39-.39.39-1.02 0-1.41-.39-.39-1.02-.39-1.41 0l-1.42 1.42c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0z" />
    </svg>
    <svg v-else viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z" />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.theme-toggle {
  width: 36px;
  height: 36px;
  border-radius: $radius-md;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $text-secondary;
  transition: all $transition-normal;

  svg { width: 20px; height: 20px; }

  &:hover {
    background: $bg-secondary;
    color: $accent-color;
  }
}
</style>

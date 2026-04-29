<template>
  <span class="trend" :class="[direction, size]">
    <svg viewBox="0 0 20 20" fill="currentColor">
      <path v-if="direction === 'up'" d="M10 3l5 6h-3.5v5h-3V9H5l5-6z" />
      <path v-else-if="direction === 'down'" d="M10 17l5-6h-3.5V6h-3v5H5l5 6z" />
      <path v-else d="M3 10h14v.5H3V10z" />
    </svg>
    <span class="trend-value">{{ value }}</span>
    <span v-if="label" class="trend-label">{{ label }}</span>
  </span>
</template>

<script setup lang="ts">
defineProps<{
  value: string | number
  direction: 'up' | 'down' | 'flat'
  size?: 'sm' | 'md'
  label?: string
}>()
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: $font-weight-medium;

  svg { width: 16px; height: 16px; flex-shrink: 0; }
  &.up svg { color: $success-color; }
  &.down svg { color: $danger-color; }
  &.flat svg { color: $text-muted; }

  &-value { font-variant-numeric: tabular-nums; }

  &.sm {
    font-size: $font-size-xs;
    svg { width: 12px; height: 12px; }
  }

  &.md { font-size: $font-size-sm; }
}
</style>

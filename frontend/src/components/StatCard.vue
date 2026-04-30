<template>
  <div class="stat-card" :class="{ clickable, elevated }" @click="clickable && $emit('click')">
    <div class="stat-card-icon" :class="colorClass">
      <component :is="icon" v-if="icon" />
    </div>
    <div class="stat-card-content">
      <span class="stat-card-value">{{ formattedValue }}</span>
      <span class="stat-card-label">{{ label }}</span>
    </div>
    <div v-if="trend !== undefined" class="stat-card-trend" :class="trend > 0 ? 'up' : 'down'">
      <svg v-if="trend > 0" viewBox="0 0 20 20" fill="currentColor"><path d="M10 4l4 4h-3v4H9V8H6l4-4z"/></svg>
      <svg v-else viewBox="0 0 20 20" fill="currentColor"><path d="M10 16l-4-4h3V8h2v4h3l-4 4z"/></svg>
      <span>{{ Math.abs(trend) }}%</span>
    </div>
    <div v-if="sparkline" class="stat-card-sparkline">
      <svg :viewBox="`0 0 ${sparkline.length} 24`" preserveAspectRatio="none">
        <polyline :points="sparklinePoints" fill="none" stroke-width="2" :class="colorClass" />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

const props = defineProps<{
  icon?: Component
  value: number | string
  label: string
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  trend?: number
  clickable?: boolean
  elevated?: boolean
  sparkline?: number[]
}>()

defineEmits<{ click: [] }>()

const colorClass = computed(() => props.color ? `color-${props.color}` : 'color-primary')

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value >= 1000000
      ? `${(props.value / 1000000).toFixed(1)}M`
      : props.value >= 1000
        ? `${(props.value / 1000).toFixed(1)}K`
        : props.value.toLocaleString()
  }
  return props.value
})

const sparklinePoints = computed(() => {
  if (!props.sparkline?.length) return ''
  const max = Math.max(...props.sparkline)
  const min = Math.min(...props.sparkline)
  const range = max - min || 1
  return props.sparkline
    .map((v, i) => `${i},${24 - ((v - min) / range) * 20}`)
    .join(' ')
})
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.stat-card {
  @include card-base;
  display: flex;
  align-items: flex-start;
  gap: 24px; // 8px栅格: 24px
  padding: 24px; // 8px栅格: 24px
  border-radius: 12px; // 统一圆角 8-12px

  &.clickable { cursor: pointer; }
  &.elevated { box-shadow: $shadow-lg; }

  &-icon {
    @include icon-badge;
    width: 48px; // 8px栅格: 48px
    height: 48px;
    border-radius: 12px;
  }

  &-content {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  &-value {
    font-size: $font-size-2xl; // 22px
    font-weight: $font-weight-bold;
    color: $text-primary;
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
  }

  &-label {
    font-size: $font-size-sm; // 13px
    color: $text-muted;
    margin-top: 8px; // 8px栅格
  }

  &-trend {
    display: flex;
    align-items: center;
    gap: 2px;
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;

    svg { width: 16px; height: 16px; }
    &.up { color: $success-color; }
    &.down { color: $danger-color; }
  }

  &-sparkline {
    width: 100%;
    height: 24px; // 8px栅格: 24px
    margin-top: 16px; // 8px栅格

    svg { width: 100%; height: 100%; overflow: visible; }
    polyline { stroke-linejoin: round; stroke-linecap: round; }
  }
}

.color-primary .stat-card-icon { background: rgba($accent-color, 0.1); color: $accent-color; }
.color-primary polyline { stroke: $accent-color; }
.color-success .stat-card-icon { background: rgba($success-500, 0.1); color: $success-600; }
.color-success polyline { stroke: $success-500; }
.color-warning .stat-card-icon { background: rgba($warning-500, 0.1); color: $warning-600; }
.color-warning polyline { stroke: $warning-500; }
.color-danger .stat-card-icon { background: rgba($danger-500, 0.1); color: $danger-600; }
.color-danger polyline { stroke: $danger-500; }
.color-info .stat-card-icon { background: rgba($info-500, 0.1); color: $info-600; }
.color-info polyline { stroke: $info-500; }
</style>

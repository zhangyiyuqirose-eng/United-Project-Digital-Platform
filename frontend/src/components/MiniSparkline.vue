<template>
  <svg class="sparkline" :viewBox="`0 0 ${data.length} 40`" preserveAspectRatio="none">
    <defs>
      <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" :stop-color="c" stop-opacity="0.3" />
        <stop offset="100%" :stop-color="c" stop-opacity="0" />
      </linearGradient>
    </defs>
    <path :d="areaPath" fill="url(#sparkGrad)" />
    <path :d="linePath" fill="none" :stroke="c" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ data: number[]; color?: string }>()

const c = computed(() => props.color || '#6366f1')

const linePath = computed(() => {
  const d = props.data
  if (!d.length) return ''
  const max = Math.max(...d)
  const min = Math.min(...d)
  const range = max - min || 1
  const pts = d.map((v, i) => ({ x: i, y: 38 - ((v - min) / range) * 34 }))
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ')
})

const areaPath = computed(() => {
  const d = props.data
  if (!d.length) return ''
  const max = Math.max(...d)
  const min = Math.min(...d)
  const range = max - min || 1
  const pts = d.map((v, i) => ({ x: i, y: 38 - ((v - min) / range) * 34 }))
  const line = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ')
  return `${line} L${pts.length - 1},40 L0,40 Z`
})
</script>

<style scoped lang="scss">
.sparkline { width: 100%; height: 40px; }
</style>

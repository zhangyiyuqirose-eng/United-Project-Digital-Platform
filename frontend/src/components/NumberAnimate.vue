<template>
  <span class="animate-number">{{ displayValue }}</span>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = defineProps<{
  value: number
  duration?: number
  decimals?: number
}>()

const displayValue = ref(0)

function animate() {
  const start = 0
  const end = props.value
  const dur = props.duration || 1000
  const startTime = performance.now()

  function step(now: number) {
    const progress = Math.min((now - startTime) / dur, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    const current = start + (end - start) * eased
    displayValue.value = props.decimals !== undefined
      ? Number(current.toFixed(props.decimals))
      : Math.round(current)
    if (progress < 1) requestAnimationFrame(step)
    else displayValue.value = end
  }

  requestAnimationFrame(step)
}

onMounted(animate)
watch(() => props.value, animate)
</script>

<style scoped lang="scss">
.animate-number {
  font-variant-numeric: tabular-nums;
  display: inline-block;
}
</style>

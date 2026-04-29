<template>
  <div class="bento-grid" :class="layout">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  layout?: 'dashboard' | 'default'
}>()
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.bento-grid {
  display: grid;
  gap: $spacing-lg;

  &.dashboard {
    grid-template-columns: repeat(4, 1fr);
    grid-auto-rows: minmax(180px, auto);

    > *:nth-child(1) { grid-column: span 2; grid-row: span 2; }
    > *:nth-child(2) { grid-column: span 1; grid-row: span 1; }
    > *:nth-child(3) { grid-column: span 1; grid-row: span 2; }
    > *:nth-child(4) { grid-column: span 4; grid-row: span 1; }
  }

  &.default {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
}

@media (max-width: 1024px) {
  .bento-grid.dashboard {
    grid-template-columns: repeat(2, 1fr);
    > * { grid-column: span 1 !important; grid-row: span 1 !important; }
  }
}

@media (max-width: 640px) {
  .bento-grid { grid-template-columns: 1fr; }
}
</style>

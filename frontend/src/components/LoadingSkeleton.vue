<template>
  <div class="skeleton" :class="{ 'is-loading': loading }">
    <template v-if="type === 'card'">
      <div class="skeleton-card">
        <div class="skeleton-line" style="width: 60%"></div>
        <div class="skeleton-line" style="width: 100%"></div>
        <div class="skeleton-line short" style="width: 40%"></div>
      </div>
    </template>
    <template v-else-if="type === 'table'">
      <div class="skeleton-table">
        <div v-for="i in rows" :key="i" class="skeleton-row">
          <div v-for="j in cols" :key="j" class="skeleton-cell"></div>
        </div>
      </div>
    </template>
    <template v-else>
      <div class="skeleton-line" :style="{ width: width }"></div>
    </template>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  loading?: boolean
  type?: 'card' | 'table' | 'text'
  rows?: number
  cols?: number
  width?: string
}>()
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.skeleton {
  &-card, &-table { width: 100%; }

  &-line {
    height: 14px;
    margin-bottom: $spacing-md;
    border-radius: $radius-sm;
    @include skeleton-loading;

    &.short { height: 10px; }
  }

  &-row {
    display: flex;
    gap: $spacing-lg;
    margin-bottom: $spacing-md;
  }

  &-cell {
    flex: 1;
    height: 24px;
    border-radius: $radius-sm;
    @include skeleton-loading;
  }
}
</style>

<template>
  <div class="page-header">
    <div class="page-header-content">
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="description" class="page-description">{{ description }}</p>
    </div>
    <div class="page-header-actions">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px; // 8px栅格: 24px
  gap: 16px; // 8px栅格: 16px

  &-content { flex: 1; }

  .page-title {
    font-size: $font-size-2xl; // 22px
    font-weight: $font-weight-bold;
    color: $text-primary;
    line-height: 1.25;
    margin-bottom: 8px; // 8px栅格
  }

  .page-description {
    font-size: $font-size-md; // 14px
    color: $text-muted;
  }

  &-actions {
    display: flex;
    gap: 8px; // 8px栅格
    flex-shrink: 0;
  }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; }
}
</style>

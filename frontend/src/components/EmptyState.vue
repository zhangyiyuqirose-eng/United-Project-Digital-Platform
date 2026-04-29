<template>
  <div class="empty-state">
    <div class="empty-state-icon">
      <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="100" cy="100" r="80" fill="#f1f5f9" />
        <rect x="60" y="70" width="80" height="60" rx="8" fill="#e2e8f0" />
        <rect x="75" y="85" width="50" height="6" rx="3" fill="#cbd5e1" />
        <rect x="75" y="98" width="35" height="6" rx="3" fill="#cbd5e1" />
        <circle cx="100" cy="130" r="12" fill="#cbd5e1" />
      </svg>
    </div>
    <h3 class="empty-state-title">{{ title }}</h3>
    <p class="empty-state-description">{{ description }}</p>
    <slot name="action" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  description?: string
}>()
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-4xl $spacing-xl;
  text-align: center;

  &-icon {
    width: 120px;
    height: 120px;
    margin-bottom: $spacing-lg;
    opacity: 0.6;
  }

  &-title {
    font-size: $font-size-lg;
    font-weight: $font-weight-semibold;
    color: $text-secondary;
    margin-bottom: $spacing-sm;
  }

  &-description {
    font-size: $font-size-md;
    color: $text-muted;
    max-width: 320px;
  }
}
</style>

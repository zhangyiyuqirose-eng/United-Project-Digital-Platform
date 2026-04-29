<template>
  <div class="stats-row">
    <div class="stat-card">
      <div class="stat-icon sales">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
        </svg>
      </div>
      <div class="stat-info">
        <span class="stat-value">{{ stats.sales }}</span>
        <span class="stat-label">销售合同</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon purchase">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/>
        </svg>
      </div>
      <div class="stat-info">
        <span class="stat-value">{{ stats.purchase }}</span>
        <span class="stat-label">采购合同</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon framework">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
      </div>
      <div class="stat-info">
        <span class="stat-value">{{ stats.framework }}</span>
        <span class="stat-label">框架协议</span>
      </div>
    </div>
    <div class="stat-card amount">
      <div class="stat-icon money">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.12h1.96c.1.73.72 1.46 2.25 1.46 1.57 0 2.15-.64 2.15-1.23 0-.68-.44-1.26-2.31-1.76-2.24-.59-3.71-1.56-3.71-3.36 0-1.71 1.37-2.85 3.27-3.2V6h2.67v1.95c1.86.45 2.79 1.66 2.85 2.92h-1.96c-.07-.57-.47-1.19-1.93-1.19-1.34 0-2.1.62-2.1 1.18 0 .58.54 1 2.17 1.49 2.37.62 3.85 1.57 3.85 3.44-.01 1.84-1.44 2.95-3.27 3.2z"/>
        </svg>
      </div>
      <div class="stat-info">
        <span class="stat-value">{{ formatAmount(stats.totalAmount) }}</span>
        <span class="stat-label">合同总金额</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  stats: { sales: number; purchase: number; framework: number; totalAmount: number }
}>()

function formatAmount(amount: number): string {
  if (!amount) return '\xA50'
  if (amount >= 1000000) return `\xA5${(amount / 1000000).toFixed(1)}M`
  if (amount >= 1000) return `\xA5${(amount / 1000).toFixed(0)}K`
  return `\xA5${amount}`
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;

  .stat-card {
    @include card-base;
    padding: $spacing-lg;
    display: flex;
    align-items: center;
    gap: $spacing-md;

    .stat-icon {
      width: 48px;
      height: 48px;
      border-radius: $radius-lg;
      display: flex;
      align-items: center;
      justify-content: center;

      svg { width: 24px; height: 24px; }

      &.sales { background: rgba($success-color, 0.15); color: $success-color; }
      &.purchase { background: rgba($accent-color, 0.15); color: $accent-color; }
      &.framework { background: rgba($warning-color, 0.15); color: $warning-color; }
      &.money { background: rgba($text-primary, 0.1); color: $text-primary; }
    }

    .stat-info {
      .stat-value {
        font-size: $font-size-xl;
        font-weight: $font-weight-bold;
        color: $text-primary;
        display: block;
      }
      .stat-label {
        font-size: $font-size-sm;
        color: $text-muted;
      }
    }
  }
}

@media (max-width: 900px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>

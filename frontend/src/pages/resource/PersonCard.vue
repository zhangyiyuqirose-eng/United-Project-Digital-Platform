<template>
  <div class="resource-card" :class="getPoolStatusClass(person.poolStatus)">
    <div class="card-header">
      <div class="avatar">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
      </div>
      <div class="status-badge" :class="getPoolStatusClass(person.poolStatus)">
        <span class="status-dot"></span>
        {{ getPoolStatusText(person.poolStatus) }}
      </div>
    </div>

    <div class="card-body">
      <h3 class="resource-name">{{ person.name }}</h3>
      <div class="resource-meta">
        <span class="meta-item">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93z"/>
          </svg>
          {{ person.skillTags?.join(', ') || '无技能' }}
        </span>
        <span class="meta-item level" :class="getLevelClass(person.level)">
          {{ getLevelText(person.level) }}
        </span>
      </div>

      <div class="resource-detail">
        <div class="detail-row">
          <span class="detail-label">部门</span>
          <span class="detail-value">{{ person.department || '未分配' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">当前项目</span>
          <span class="detail-value project" :class="{ empty: !person.currentProject }">
            {{ person.currentProject || '暂无项目' }}
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-label">入池日期</span>
          <span class="detail-value">{{ person.entryDate || '--' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">日费率</span>
          <span class="detail-value">\xA5{{ person.dailyRate?.toLocaleString() }}</span>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <button class="action-btn assign" v-if="person.poolStatus === 0" @click="emit('assign', person)">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
        分配项目
      </button>
      <button class="action-btn release" v-if="person.poolStatus === 1" @click="emit('release', person)">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>
        释放资源
      </button>
      <button class="action-btn view" @click="emit('view', person)">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PersonVO } from '@/api/modules/resource'

defineProps<{
  person: PersonVO
}>()

const emit = defineEmits<{
  (e: 'assign', person: PersonVO): void
  (e: 'release', person: PersonVO): void
  (e: 'view', person: PersonVO): void
}>()

function getPoolStatusText(status: number): string {
  const map: Record<number, string> = { 0: '空闲', 1: '已分配', 2: '已退场' }
  return map[status] || '未知'
}
function getPoolStatusClass(status: number): string {
  const map: Record<number, string> = { 0: 'AVAILABLE', 1: 'ASSIGNED', 2: 'ON_LEAVE' }
  return map[status] || 'BENCHED'
}
function getLevelText(level: number): string {
  const map: Record<number, string> = { 1: '初级', 2: '中级', 3: '高级', 4: '专家' }
  return map[level] || ''
}
function getLevelClass(level: number): string {
  const map: Record<number, string> = { 1: 'JUNIOR', 2: 'MIDDLE', 3: 'SENIOR', 4: 'EXPERT' }
  return map[level] || 'JUNIOR'
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.resource-card {
  @include card-base;
  padding: 0;
  overflow: hidden;
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-hover;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-lg;
    background: linear-gradient(135deg, $bg-secondary, $bg-tertiary);

    .avatar {
      width: 48px;
      height: 48px;
      border-radius: $radius-xl;
      background: $accent-gradient;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      svg { width: 28px; height: 28px; }
    }

    .status-badge {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: $radius-lg;
      font-size: $font-size-sm;
      font-weight: $font-weight-medium;

      .status-dot { width: 6px; height: 6px; border-radius: 50%; }

      &.AVAILABLE { background: rgba($success-color, 0.15); color: $success-color; .status-dot { background: $success-color; } }
      &.ASSIGNED { background: rgba($accent-color, 0.15); color: $accent-color; .status-dot { background: $accent-color; } }
      &.ON_LEAVE { background: rgba($warning-color, 0.15); color: $warning-color; .status-dot { background: $warning-color; } }
      &.BENCHED { background: rgba($text-muted, 0.15); color: $text-muted; .status-dot { background: $text-muted; } }
    }
  }

  .card-body {
    padding: $spacing-lg;

    .resource-name {
      font-size: $font-size-lg;
      font-weight: $font-weight-semibold;
      color: $text-primary;
      margin-bottom: $spacing-sm;
    }

    .resource-meta {
      display: flex;
      gap: $spacing-sm;
      margin-bottom: $spacing-md;

      .meta-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: $font-size-sm;
        color: $text-secondary;
        svg { width: 14px; height: 14px; }

        &.level {
          padding: 2px 8px;
          border-radius: $radius-sm;
          background: rgba($accent-color, 0.1);
          color: $accent-color;
          &.SENIOR { background: rgba($success-color, 0.1); color: $success-color; }
          &.MIDDLE { background: rgba($accent-color, 0.1); color: $accent-color; }
          &.JUNIOR { background: rgba($text-muted, 0.1); color: $text-muted; }
        }
      }
    }

    .resource-detail {
      display: flex;
      flex-direction: column;
      gap: $spacing-sm;

      .detail-row {
        display: flex;
        justify-content: space-between;
        .detail-label { font-size: $font-size-sm; color: $text-muted; }
        .detail-value {
          font-size: $font-size-sm;
          color: $text-secondary;
          font-weight: $font-weight-medium;
          &.project { color: $accent-color; &.empty { color: $text-muted; } }
        }
      }
    }
  }

  .card-footer {
    display: flex;
    gap: $spacing-sm;
    padding: $spacing-md $spacing-lg;
    border-top: 1px solid $divider-color;

    .action-btn {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px;
      border-radius: $radius-md;
      font-size: $font-size-sm;
      font-weight: $font-weight-medium;
      cursor: pointer;
      transition: all 0.2s ease;
      svg { width: 16px; height: 16px; }

      &.assign { background: $accent-color; border: none; color: white; &:hover { background: $primary-light; } }
      &.release { background: $warning-color; border: none; color: white; &:hover { background: #c05621; } }
      &.view {
        background: $bg-secondary;
        border: 1px solid $border-color;
        color: $text-secondary;
        flex: 0;
        width: 40px;
        &:hover { background: $bg-tertiary; color: $accent-color; border-color: $accent-color; }
      }
    }
  }
}
</style>

<template>
  <div class="search-section">
    <div class="search-form">
      <div class="search-row">
        <div class="search-field">
          <label class="field-label">项目名称</label>
          <div class="field-input">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <input v-model="keyword" type="text" placeholder="搜索项目名称..." class="input-control" @keyup.enter="doSearch">
          </div>
        </div>
        <div class="search-field">
          <label class="field-label">项目状态</label>
          <div class="field-input select-wrapper">
            <select v-model="status" class="input-control">
              <option value="">全部状态</option>
              <option value="PRE_INIT">立项前</option>
              <option value="IN_PROGRESS">进行中</option>
              <option value="COMPLETED">已完成</option>
              <option value="ON_HOLD">已暂停</option>
              <option value="CANCELLED">已取消</option>
            </select>
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5z"/></svg>
          </div>
        </div>
        <div class="search-actions">
          <button class="search-btn" @click="doSearch">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
            搜索
          </button>
          <button class="reset-btn" @click="doReset">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
            重置
          </button>
        </div>
      </div>
    </div>
    <!-- 快速筛选标签 -->
    <div class="quick-filters">
      <button class="filter-tag" :class="{ active: activeQuickFilter === 'all' }" @click="setQuickFilter('all')">
        全部项目
        <span class="filter-count">{{ total }}</span>
      </button>
      <button class="filter-tag" :class="{ active: activeQuickFilter === 'IN_PROGRESS' }" @click="setQuickFilter('IN_PROGRESS')">
        进行中
        <span class="filter-count running">--</span>
      </button>
      <button class="filter-tag" :class="{ active: activeQuickFilter === 'COMPLETED' }" @click="setQuickFilter('COMPLETED')">
        已完成
        <span class="filter-count success">--</span>
      </button>
      <button class="filter-tag" :class="{ active: activeQuickFilter === 'ON_HOLD' }" @click="setQuickFilter('ON_HOLD')">
        已暂停
        <span class="filter-count warning">--</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ total: number }>()

const emit = defineEmits<{
  (e: 'filter-change', params: { keyword: string; status: string; quickFilter: string }): void
}>()

const keyword = ref('')
const status = ref('')
const activeQuickFilter = ref('all')

function doSearch() {
  activeQuickFilter.value = 'all'
  emit('filter-change', { keyword: keyword.value, status: status.value, quickFilter: activeQuickFilter.value })
}

function doReset() {
  keyword.value = ''
  status.value = ''
  activeQuickFilter.value = 'all'
  emit('filter-change', { keyword: '', status: '', quickFilter: 'all' })
}

function setQuickFilter(filter: string) {
  activeQuickFilter.value = filter
  if (filter === 'all') {
    status.value = ''
  } else {
    status.value = filter
  }
  emit('filter-change', { keyword: keyword.value, status: status.value, quickFilter: filter })
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.search-section {
  @include card-base;
  padding: $spacing-lg;
  margin-bottom: $spacing-lg;

  .search-form {
    .search-row {
      display: flex;
      align-items: flex-end;
      gap: $spacing-lg;

      .search-field {
        flex: 1;

        .field-label {
          font-size: $font-size-sm;
          font-weight: $font-weight-medium;
          color: $text-secondary;
          margin-bottom: $spacing-sm;
          display: block;
        }

        .field-input {
          display: flex;
          align-items: center;
          background: $bg-secondary;
          border: 2px solid transparent;
          border-radius: $radius-lg;
          padding: 0 16px;
          height: 44px;
          transition: all 0.25s ease;

          svg { width: 20px; height: 20px; color: $text-muted; }

          .input-control {
            flex: 1;
            border: none;
            background: transparent;
            font-size: $font-size-md;
            color: $text-primary;
            padding: 0 8px;
            &:focus { outline: none; }
            &::placeholder { color: $text-muted; }
          }

          &:hover { background: $bg-tertiary; }
          &:focus-within {
            background: white;
            border-color: $accent-color;
            box-shadow: 0 0 0 4px rgba(49, 130, 206, 0.1);
          }
        }

        .select-wrapper {
          position: relative;
          .input-control { appearance: none; cursor: pointer; }
          svg { position: absolute; right: 16px; width: 20px; height: 20px; color: $text-muted; pointer-events: none; }
        }
      }

      .search-actions {
        display: flex;
        gap: $spacing-sm;

        .search-btn, .reset-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 10px 16px;
          border-radius: $radius-lg;
          font-size: $font-size-md;
          font-weight: $font-weight-medium;
          cursor: pointer;
          transition: all 0.2s ease;
          svg { width: 18px; height: 18px; }
        }

        .search-btn { background: $accent-color; border: none; color: white; &:hover { background: $primary-light; transform: translateY(-1px); } }
        .reset-btn { background: $bg-secondary; border: 1px solid $border-color; color: $text-secondary; &:hover { background: $bg-tertiary; color: $text-primary; } }
      }
    }
  }

  .quick-filters {
    display: flex;
    gap: $spacing-sm;
    margin-top: $spacing-lg;
    padding-top: $spacing-lg;
    border-top: 1px solid $divider-color;

    .filter-tag {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: $bg-secondary;
      border: 1px solid $border-color;
      border-radius: $radius-lg;
      font-size: $font-size-sm;
      color: $text-secondary;
      cursor: pointer;
      transition: all 0.2s ease;

      .filter-count {
        padding: 2px 6px;
        background: $divider-color;
        border-radius: $radius-sm;
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;
        color: $text-muted;
        &.running { background: rgba($accent-color, 0.15); color: $accent-color; }
        &.success { background: rgba($success-color, 0.15); color: $success-color; }
        &.warning { background: rgba($warning-color, 0.15); color: $warning-color; }
      }

      &:hover { background: $bg-tertiary; }
      &.active { background: rgba($accent-color, 0.1); border-color: $accent-color; color: $accent-color; }
    }
  }
}

@media (max-width: 1024px) {
  .search-section .search-form .search-row { flex-wrap: wrap; }
  .search-field { min-width: 200px; }
}

@media (max-width: 768px) {
  .search-actions { width: 100%; justify-content: flex-end; }
  .quick-filters { flex-wrap: wrap; }
}
</style>

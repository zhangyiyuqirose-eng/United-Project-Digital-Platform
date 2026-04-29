<template>
  <div>
    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-form">
        <div class="search-row">
          <div class="search-field">
            <label class="field-label">技能搜索</label>
            <div class="field-input">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
              <input v-model="searchForm.skill" type="text" placeholder="搜索技能关键词..." class="input-control" @keyup.enter="handleSearch">
            </div>
          </div>
          <div class="search-field">
            <label class="field-label">人员状态</label>
            <div class="field-input select-wrapper">
              <select v-model="searchForm.status" class="input-control" @change="handleSearch">
                <option value="">全部状态</option>
                <option value="AVAILABLE">空闲</option>
                <option value="ASSIGNED">已分配</option>
                <option value="ON_LEAVE">请假中</option>
                <option value="BENCHED">待分配</option>
              </select>
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5z"/></svg>
            </div>
          </div>
          <div class="search-actions">
            <button class="search-btn" @click="handleSearch">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
              搜索
            </button>
            <button class="reset-btn" @click="handleReset">重置</button>
          </div>
        </div>
      </div>

      <!-- 快速筛选 -->
      <div class="quick-filters">
        <button class="filter-chip" :class="{ active: searchForm.status === '' }" @click="setFilter('')">全部</button>
        <button class="filter-chip" :class="{ active: searchForm.status === 'AVAILABLE' }" @click="setFilter('AVAILABLE')">
          <span class="chip-dot available"></span>空闲
        </button>
        <button class="filter-chip" :class="{ active: searchForm.status === 'ASSIGNED' }" @click="setFilter('ASSIGNED')">
          <span class="chip-dot assigned"></span>已分配
        </button>
        <button class="filter-chip" :class="{ active: searchForm.status === 'ON_LEAVE' }" @click="setFilter('ON_LEAVE')">
          <span class="chip-dot leave"></span>请假中
        </button>
        <button class="filter-chip" :class="{ active: searchForm.status === 'BENCHED' }" @click="setFilter('BENCHED')">
          <span class="chip-dot bench"></span>待分配
        </button>
      </div>
    </div>

    <!-- 资源列表 -->
    <div class="resource-grid">
      <PersonCard
        v-for="row in tableData"
        :key="row.personId"
        :person="row"
        @assign="(p) => emit('assign', p)"
        @release="(p) => emit('release', p)"
        @view="(p) => emit('view', p)"
      />

      <!-- 空状态 -->
      <div class="empty-state" v-if="!loading && tableData.length === 0">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 4v2h14v-2c0-2.83-4.67-4-7-4zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.95v2h6v-2c0-2.83-4.67-4-7-4z"/></svg>
        <p>暂无资源数据</p>
      </div>

      <!-- 加载状态 -->
      <div class="loading-overlay" v-if="loading">
        <div class="spinner"></div>
        <span>正在加载...</span>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-section">
      <div class="pagination-info">共 <span class="total-count">{{ total }}</span> 名人员</div>
      <div class="pagination-controls">
        <button class="page-btn" :class="{ disabled: page === 1 }" @click="changePage(page - 1)" :disabled="page === 1">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L11.83 12z"/></svg>
        </button>
        <div class="page-numbers">
          <button v-for="p in visiblePages" :key="p" class="page-num" :class="{ active: p === page }" @click="changePage(p)">{{ p }}</button>
        </div>
        <button class="page-btn" :class="{ disabled: page >= totalPages }" @click="changePage(page + 1)" :disabled="page >= totalPages">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
        </button>
        <select class="limit-select" v-model="limit" @change="handleLimitChange">
          <option value="12">12人/页</option>
          <option value="24">24人/页</option>
          <option value="48">48人/页</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getPersons, type PersonVO } from '@/api/modules/resource'
import PersonCard from './PersonCard.vue'

const emit = defineEmits<{
  (e: 'assign', person: PersonVO): void
  (e: 'release', person: PersonVO): void
  (e: 'view', person: PersonVO): void
  (e: 'stats-update', stats: { total: number; available: number; assigned: number }): void
}>()

const loading = ref(false)
const tableData = ref<PersonVO[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(12)
const searchForm = reactive({ skill: '', status: '' })

const totalPages = computed(() => Math.ceil(total.value / limit.value) || 1)

const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, page.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const stats = computed(() => ({
  total: total.value,
  available: tableData.value.filter(r => r.poolStatus === 0).length,
  assigned: tableData.value.filter(r => r.poolStatus === 1).length,
}))

watch(stats, (val) => emit('stats-update', val), { immediate: true })

async function fetchData() {
  loading.value = true
  try {
    const poolStatusMap: Record<string, number | undefined> = {
      '': undefined, 'AVAILABLE': 0, 'ASSIGNED': 1, 'ON_LEAVE': undefined, 'BENCHED': 0,
    }
    const res = await getPersons({
      page: page.value, size: limit.value,
      keyword: searchForm.skill || undefined,
      pool_status: poolStatusMap[searchForm.status],
    })
    tableData.value = res.records || []
    total.value = res.total || 0
  } catch {
    ElMessage.error('获取人员列表失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleSearch() { page.value = 1; fetchData() }
function handleReset() { searchForm.skill = ''; searchForm.status = ''; page.value = 1; fetchData() }
function setFilter(status: string) { searchForm.status = status; page.value = 1; fetchData() }
function changePage(p: number) { if (p >= 1 && p <= totalPages.value) { page.value = p; fetchData() } }
function handleLimitChange() { page.value = 1; fetchData() }

defineExpose({ fetchData })

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

/* 搜索区域 */
.search-section {
  @include card-base;
  padding: $spacing-lg;
  margin-bottom: $spacing-lg;

  .search-form .search-row {
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
        svg { position: absolute; right: 16px; width: 20px; height: 20px; color: $text-muted; pointer-events: none; }
        .input-control { appearance: none; cursor: pointer; }
      }
    }

    .search-actions {
      display: flex;
      gap: $spacing-sm;

      .search-btn, .reset-btn {
        padding: 10px 16px;
        border-radius: $radius-lg;
        font-size: $font-size-md;
        font-weight: $font-weight-medium;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .search-btn {
        background: $accent-color;
        border: none;
        color: white;
        display: flex;
        align-items: center;
        gap: 6px;
        svg { width: 18px; height: 18px; }
        &:hover { background: $primary-light; transform: translateY(-1px); }
      }

      .reset-btn {
        background: $bg-secondary;
        border: 1px solid $border-color;
        color: $text-secondary;
        &:hover { background: $bg-tertiary; color: $text-primary; }
      }
    }
  }

  .quick-filters {
    display: flex;
    gap: $spacing-sm;
    margin-top: $spacing-lg;
    padding-top: $spacing-lg;
    border-top: 1px solid $divider-color;

    .filter-chip {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      background: $bg-secondary;
      border: 1px solid $border-color;
      border-radius: $radius-lg;
      font-size: $font-size-sm;
      color: $text-secondary;
      cursor: pointer;
      transition: all 0.2s ease;

      .chip-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        &.available { background: $success-color; }
        &.assigned { background: $accent-color; }
        &.leave { background: $warning-color; }
        &.bench { background: $text-muted; }
      }

      &:hover { background: $bg-tertiary; }
      &.active { background: rgba($accent-color, 0.1); border-color: $accent-color; color: $accent-color; }
    }
  }
}

/* 资源网格 */
.resource-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $spacing-lg;
  margin-bottom: $spacing-lg;

  .empty-state {
    grid-column: span 4;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: $spacing-md;
    padding: $spacing-2xl;
    color: $text-muted;
    svg { width: 48px; height: 48px; opacity: 0.5; }
  }

  .loading-overlay {
    grid-column: span 4;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: $spacing-md;
    padding: $spacing-2xl;
    color: $text-muted;

    .spinner {
      width: 24px;
      height: 24px;
      border: 3px solid $divider-color;
      border-top-color: $accent-color;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
  }
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 分页 */
.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  background: white;
  border-radius: $radius-card;
  box-shadow: $shadow-card;

  .pagination-info {
    font-size: $font-size-sm;
    color: $text-muted;
    .total-count { font-weight: $font-weight-semibold; color: $text-secondary; }
  }

  .pagination-controls {
    display: flex;
    align-items: center;
    gap: $spacing-sm;

    .page-btn {
      width: 36px;
      height: 36px;
      border-radius: $radius-md;
      background: $bg-secondary;
      border: 1px solid $border-color;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      color: $text-secondary;
      transition: all 0.2s ease;
      svg { width: 20px; height: 20px; }
      &:hover:not(.disabled) { background: white; border-color: $accent-color; color: $accent-color; }
      &.disabled { opacity: 0.5; cursor: not-allowed; }
    }

    .page-numbers {
      display: flex;
      gap: 4px;
      .page-num {
        width: 36px;
        height: 36px;
        border-radius: $radius-md;
        background: $bg-secondary;
        border: 1px solid transparent;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: $font-size-md;
        color: $text-secondary;
        transition: all 0.2s ease;
        &:hover:not(.active) { background: white; border-color: $border-color; }
        &.active { background: $accent-color; color: white; }
      }
    }

    .limit-select {
      padding: 8px 12px;
      border-radius: $radius-md;
      border: 1px solid $border-color;
      background: $bg-secondary;
      font-size: $font-size-sm;
      color: $text-secondary;
      cursor: pointer;
      &:hover { background: white; border-color: $accent-color; }
    }
  }
}

@media (max-width: 1200px) { .resource-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 900px) { .resource-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) {
  .resource-grid { grid-template-columns: 1fr; }
  .search-section .search-form .search-row { flex-direction: column; }
  .pagination-section { flex-direction: column; gap: $spacing-md; .pagination-controls { width: 100%; justify-content: center; } }
}
</style>

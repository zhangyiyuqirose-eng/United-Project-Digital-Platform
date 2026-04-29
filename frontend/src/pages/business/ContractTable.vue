<template>
  <div>
    <!-- 搜索筛选 -->
    <div class="search-section">
      <div class="search-bar">
        <div class="search-input">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
          <input v-model="searchForm.keyword" type="text" placeholder="搜索合同名称或编号..." @keyup.enter="handleSearch">
        </div>
        <select v-model="searchForm.type" class="filter-select" @change="handleSearch">
          <option value="">全部类型</option>
          <option value="SALES">销售合同</option>
          <option value="PROCUREMENT">采购合同</option>
          <option value="FRAMEWORK">框架协议</option>
        </select>
        <select v-model="searchForm.status" class="filter-select" @change="handleSearch">
          <option value="">全部状态</option>
          <option value="DRAFT">草稿</option>
          <option value="PENDING">审批中</option>
          <option value="SIGNED">已签署</option>
          <option value="COMPLETED">已完成</option>
        </select>
        <button class="search-btn" @click="handleSearch">搜索</button>
        <button class="reset-btn" @click="handleReset">重置</button>
      </div>

      <!-- 状态筛选标签 -->
      <div class="filter-tags">
        <button class="filter-tag" :class="{ active: searchForm.status === '' }" @click="setStatusFilter('')">
          全部
          <span class="tag-count">{{ total }}</span>
        </button>
        <button class="filter-tag" :class="{ active: searchForm.status === 'DRAFT' }" @click="setStatusFilter('DRAFT')">
          <span class="tag-dot draft"></span>
          草稿
        </button>
        <button class="filter-tag" :class="{ active: searchForm.status === 'PENDING' }" @click="setStatusFilter('PENDING')">
          <span class="tag-dot pending"></span>
          审批中
        </button>
        <button class="filter-tag" :class="{ active: searchForm.status === 'SIGNED' }" @click="setStatusFilter('SIGNED')">
          <span class="tag-dot signed"></span>
          已签署
        </button>
        <button class="filter-tag" :class="{ active: searchForm.status === 'COMPLETED' }" @click="setStatusFilter('COMPLETED')">
          <span class="tag-dot completed"></span>
          已完成
        </button>
      </div>
    </div>

    <!-- 合同列表 -->
    <div class="contract-list">
      <div class="list-header">
        <div class="header-row">
          <span class="col code">合同编号</span>
          <span class="col name">合同名称</span>
          <span class="col type">类型</span>
          <span class="col party">相对方</span>
          <span class="col amount">合同金额</span>
          <span class="col date">签署日期</span>
          <span class="col status">状态</span>
          <span class="col actions">操作</span>
        </div>
      </div>

      <div class="list-body">
        <div class="contract-row" v-for="row in tableData" :key="row.contractId">
          <span class="col code">
            <span class="code-badge">{{ row.contractCode }}</span>
          </span>
          <span class="col name">
            <span class="contract-name">{{ row.contractName }}</span>
          </span>
          <span class="col type">
            <span class="type-badge" :class="row.contractType">{{ getTypeText(row.contractType) }}</span>
          </span>
          <span class="col party">
            <span class="party-name">{{ row.counterparty }}</span>
          </span>
          <span class="col amount">
            <span class="amount-value">{{ formatAmount(row.amount) }}</span>
          </span>
          <span class="col date">
            <span class="date-text">{{ row.signDate || '--' }}</span>
          </span>
          <span class="col status">
            <span class="status-badge" :class="row.status">
              <span class="status-dot"></span>
              {{ getStatusText(row.status) }}
            </span>
          </span>
          <span class="col actions">
            <button class="action-btn view" @click="emit('view', row)">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
            </button>
            <button class="action-btn edit" @click="emit('edit', row)">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
            </button>
            <button class="action-btn delete" @click="emit('delete', row.contractId)">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
            </button>
          </span>
        </div>

        <div class="empty-list" v-if="!loading && tableData.length === 0">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/></svg>
          <p>暂无合同数据</p>
        </div>

        <div class="loading-state" v-if="loading">
          <div class="spinner"></div>
          <span>正在加载...</span>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <div class="page-info">共 {{ total }} 条记录</div>
        <div class="page-controls">
          <button class="page-btn" :class="{ disabled: page === 1 }" @click="changePage(page - 1)" :disabled="page === 1">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L11.83 12z"/></svg>
          </button>
          <div class="page-numbers">
            <button v-for="p in visiblePages" :key="p" class="page-num" :class="{ active: p === page }" @click="changePage(p)">{{ p }}</button>
          </div>
          <button class="page-btn" :class="{ disabled: page >= totalPages }" @click="changePage(page + 1)" :disabled="page >= totalPages">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { getContractList } from '@/api/modules/business'

const emit = defineEmits<{
  (e: 'view', row: any): void
  (e: 'edit', row: any): void
  (e: 'delete', id: string): void
  (e: 'stats-update', stats: { sales: number; purchase: number; framework: number; totalAmount: number }): void
}>()

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const searchForm = reactive({ keyword: '', type: '', status: '' })

const totalPages = computed(() => Math.ceil(total.value / limit.value) || 1)

const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, page.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const stats = computed(() => ({
  sales: tableData.value.filter(r => r.contractType === 'SALES').length,
  purchase: tableData.value.filter(r => r.contractType === 'PROCUREMENT').length,
  framework: tableData.value.filter(r => r.contractType === 'FRAMEWORK').length,
  totalAmount: tableData.value.reduce((sum, r) => sum + (r.amount || 0), 0),
}))

watch(stats, (val) => emit('stats-update', val), { immediate: true })

async function fetchData() {
  loading.value = true
  try {
    const res = await getContractList({ page: page.value, limit: limit.value, ...searchForm })
    tableData.value = res.records || []
    total.value = res.total || 0
  } catch {
    tableData.value = [
      { contractId: '1', contractCode: 'HT-2026-001', contractName: '数字化平台运维服务合同', contractType: 'SALES', counterparty: '某某银行', amount: 1500000, signDate: '2026-03-15', status: 'SIGNED' },
      { contractId: '2', contractCode: 'HT-2026-002', contractName: '云服务器采购合同', contractType: 'PROCUREMENT', counterparty: '阿里云', amount: 800000, signDate: '2026-04-01', status: 'COMPLETED' },
      { contractId: '3', contractCode: 'HT-2026-003', contractName: 'IT服务框架协议', contractType: 'FRAMEWORK', counterparty: '某某公司', amount: 5000000, signDate: '2026-01-20', status: 'PENDING' },
    ]
    total.value = 3
  } finally {
    loading.value = false
  }
}

function handleSearch() { page.value = 1; fetchData() }
function handleReset() {
  searchForm.keyword = ''
  searchForm.type = ''
  searchForm.status = ''
  page.value = 1
  fetchData()
}
function setStatusFilter(status: string) { searchForm.status = status; page.value = 1; fetchData() }
function changePage(p: number) { if (p >= 1 && p <= totalPages.value) { page.value = p; fetchData() } }

function formatAmount(amount: number): string {
  if (!amount) return '\xA50'
  if (amount >= 1000000) return `\xA5${(amount / 1000000).toFixed(1)}M`
  if (amount >= 1000) return `\xA5${(amount / 1000).toFixed(0)}K`
  return `\xA5${amount}`
}
function getTypeText(type: string): string {
  const map: Record<string, string> = { 'SALES': '销售', 'PROCUREMENT': '采购', 'FRAMEWORK': '框架' }
  return map[type] || type
}
function getStatusText(status: string): string {
  const map: Record<string, string> = { 'DRAFT': '草稿', 'PENDING': '审批中', 'SIGNED': '已签署', 'COMPLETED': '已完成' }
  return map[status] || status
}

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

  .search-bar {
    display: flex;
    align-items: center;
    gap: $spacing-md;

    .search-input {
      flex: 1;
      display: flex;
      align-items: center;
      background: $bg-secondary;
      border: 2px solid transparent;
      border-radius: $radius-lg;
      padding: 0 $spacing-md;
      height: 44px;
      transition: all 0.25s ease;

      svg { width: 20px; height: 20px; color: $text-muted; }

      input {
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

    .filter-select {
      padding: 8px 16px;
      background: $bg-secondary;
      border: 1px solid $border-color;
      border-radius: $radius-md;
      font-size: $font-size-sm;
      color: $text-secondary;
      cursor: pointer;
      transition: all 0.2s ease;
      &:hover { background: $bg-tertiary; border-color: $divider-color; }
    }

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
      &:hover { background: $primary-light; transform: translateY(-1px); }
    }

    .reset-btn {
      background: $bg-secondary;
      border: 1px solid $border-color;
      color: $text-secondary;
      &:hover { background: $bg-tertiary; color: $text-primary; }
    }
  }

  .filter-tags {
    display: flex;
    gap: $spacing-sm;
    margin-top: $spacing-md;
    padding-top: $spacing-md;
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

      .tag-count {
        padding: 2px 6px;
        background: $divider-color;
        border-radius: $radius-sm;
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;
      }

      .tag-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        &.draft { background: $text-muted; }
        &.pending { background: $warning-color; }
        &.signed { background: $accent-color; }
        &.completed { background: $success-color; }
      }

      &:hover { background: $bg-tertiary; }
      &.active {
        background: rgba($accent-color, 0.1);
        border-color: $accent-color;
        color: $accent-color;
      }
    }
  }
}

/* 合同列表 */
.contract-list {
  @include card-base;
  padding: 0;
  overflow: hidden;

  .list-header {
    .header-row {
      display: flex;
      align-items: center;
      padding: $spacing-md $spacing-lg;
      background: $bg-secondary;
      gap: $spacing-md;

      .col {
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        color: $text-muted;
        &.code { width: 120px; }
        &.name { flex: 1; }
        &.type { width: 80px; }
        &.party { width: 140px; }
        &.amount { width: 100px; }
        &.date { width: 100px; }
        &.status { width: 100px; }
        &.actions { width: 100px; text-align: center; }
      }
    }
  }

  .list-body {
    .contract-row {
      display: flex;
      align-items: center;
      padding: $spacing-md $spacing-lg;
      gap: $spacing-md;
      border-bottom: 1px solid $divider-color;
      transition: background 0.15s ease;
      &:hover { background: rgba($accent-color, 0.03); }
      &:last-child { border-bottom: none; }

      .col {
        &.code {
          .code-badge {
            display: inline-block;
            padding: 4px 10px;
            background: $bg-secondary;
            border-radius: $radius-sm;
            font-size: $font-size-sm;
            font-weight: $font-weight-medium;
            color: $text-secondary;
          }
        }

        &.name {
          .contract-name { font-size: $font-size-md; font-weight: $font-weight-medium; color: $text-primary; }
        }

        &.type {
          .type-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: $radius-sm;
            font-size: $font-size-sm;
            font-weight: $font-weight-medium;
            &.SALES { background: rgba($success-color, 0.15); color: $success-color; }
            &.PROCUREMENT { background: rgba($accent-color, 0.15); color: $accent-color; }
            &.FRAMEWORK { background: rgba($warning-color, 0.15); color: $warning-color; }
          }
        }

        &.party .party-name { font-size: $font-size-sm; color: $text-secondary; }
        &.amount .amount-value { font-size: $font-size-md; font-weight: $font-weight-semibold; color: $text-primary; }
        &.date .date-text { font-size: $font-size-sm; color: $text-secondary; }

        &.status {
          .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: $radius-lg;
            font-size: $font-size-sm;
            font-weight: $font-weight-medium;

            .status-dot { width: 6px; height: 6px; border-radius: 50%; }

            &.DRAFT { background: rgba($text-muted, 0.15); color: $text-muted; .status-dot { background: $text-muted; } }
            &.PENDING { background: rgba($warning-color, 0.15); color: $warning-color; .status-dot { background: $warning-color; } }
            &.SIGNED { background: rgba($accent-color, 0.15); color: $accent-color; .status-dot { background: $accent-color; } }
            &.COMPLETED { background: rgba($success-color, 0.15); color: $success-color; .status-dot { background: $success-color; } }
          }
        }

        &.actions {
          display: flex;
          justify-content: center;
          gap: 4px;

          .action-btn {
            width: 32px;
            height: 32px;
            border-radius: $radius-md;
            background: transparent;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: $text-muted;
            transition: all 0.2s ease;
            svg { width: 18px; height: 18px; }
            &:hover { background: $bg-secondary; }
            &.view:hover { background: rgba($accent-color, 0.1); color: $accent-color; }
            &.edit:hover { background: rgba($warning-color, 0.1); color: $warning-color; }
            &.delete:hover { background: rgba($danger-color, 0.1); color: $danger-color; }
          }
        }
      }
    }

    .empty-list {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: $spacing-md;
      padding: $spacing-2xl;
      color: $text-muted;
      svg { width: 48px; height: 48px; opacity: 0.5; }
    }

    .loading-state {
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
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 分页 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  border-top: 1px solid $divider-color;

  .page-info { font-size: $font-size-sm; color: $text-muted; }

  .page-controls {
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
  }
}

@media (max-width: 900px) {
  .search-bar { flex-wrap: wrap; }
}
</style>

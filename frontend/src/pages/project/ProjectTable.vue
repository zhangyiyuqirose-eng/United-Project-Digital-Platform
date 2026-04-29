<template>
  <div class="table-section">
    <div class="table-container">
      <table class="modern-table">
        <thead>
          <tr>
            <th class="col-code">项目编号</th>
            <th class="col-name">项目名称</th>
            <th class="col-type">类型</th>
            <th class="col-manager">项目经理</th>
            <th class="col-date">时间周期</th>
            <th class="col-budget">预算金额</th>
            <th class="col-status">状态</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody v-if="loading">
          <tr>
            <td colspan="8" class="loading-cell">
              <div class="loading-spinner">
                <div class="spinner"></div>
                <span>正在加载...</span>
              </div>
            </td>
          </tr>
        </tbody>
        <tbody v-else-if="tableData.length === 0">
          <tr>
            <td colspan="8" class="empty-cell">
              <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/></svg>
                <p>暂无项目数据</p>
              </div>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr v-for="row in tableData" :key="row.projectId" class="data-row">
            <td class="col-code">
              <span class="code-badge">{{ row.projectCode || '--' }}</span>
            </td>
            <td class="col-name">
              <div class="name-cell" @click="emit('view', row)">
                <span class="project-name">{{ row.projectName }}</span>
                <span class="project-dept">{{ row.departmentName || '未分配部门' }}</span>
              </div>
            </td>
            <td class="col-type">
              <span class="type-tag">{{ row.projectType || '内部项目' }}</span>
            </td>
            <td class="col-manager">
              <div class="manager-cell">
                <div class="manager-avatar">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                </div>
                <span class="manager-name">{{ row.managerName || '未指派' }}</span>
              </div>
            </td>
            <td class="col-date">
              <div class="date-range">
                <span class="date-start">{{ row.startDate || '--' }}</span>
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 5l-1.42 1.42L17.17 9H3v2h14.17l-2.58 2.58L16 15l5-5-5-5z"/></svg>
                <span class="date-end">{{ row.endDate || '--' }}</span>
              </div>
            </td>
            <td class="col-budget">
              <span class="budget-value" v-if="row.budget">\xA5{{ formatBudget(row.budget) }}</span>
              <span class="budget-empty" v-else>--</span>
            </td>
            <td class="col-status">
              <div class="status-tag" :class="getStatusClass(row.status)">
                <span class="status-dot"></span>
                <span class="status-text">{{ getStatusText(row.status) }}</span>
              </div>
            </td>
            <td class="col-actions">
              <div class="action-group">
                <button class="action-btn view" @click="emit('view', row)" title="查看详情">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                </button>
                <button class="action-btn edit" @click="emit('edit', row)" title="编辑">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                </button>
                <button class="action-btn workflow" @click="emit('workflow', row)" title="发起流程">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
                </button>
                <button class="action-btn delete" @click="emit('delete', row)" title="删除">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pagination-section">
      <div class="pagination-info">共 <span class="total-count">{{ total }}</span> 条记录</div>
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
          <option value="10">10条/页</option>
          <option value="20">20条/页</option>
          <option value="50">50条/页</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getProjectList, type ProjectVO } from '@/api/modules/project'

const emit = defineEmits<{
  (e: 'view', row: ProjectVO): void
  (e: 'edit', row: ProjectVO): void
  (e: 'workflow', row: ProjectVO): void
  (e: 'delete', row: ProjectVO): void
  (e: 'total-update', count: number): void
}>()

const loading = ref(false)
const tableData = ref<ProjectVO[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)

// Filters passed from parent
const filters = ref({ keyword: '', status: '' })

const totalPages = computed(() => Math.ceil(total.value / limit.value) || 1)
const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, page.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getProjectList({ page: page.value, limit: limit.value, ...filters.value })
    tableData.value = res.records || []
    total.value = res.total || 0
  } catch {
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

watch(total, (val) => emit('total-update', val))

function setFilters(params: { keyword: string; status: string }) {
  filters.value = params
  page.value = 1
  fetchData()
}

function changePage(p: number) {
  if (p >= 1 && p <= totalPages.value) {
    page.value = p
    fetchData()
  }
}

function handleLimitChange() { page.value = 1; fetchData() }

function formatBudget(amount: number): string {
  if (amount >= 1000000) return (amount / 1000000).toFixed(1) + '万'
  return amount.toLocaleString()
}

function getStatusClass(status: string): string {
  const map: Record<string, string> = {
    'PRE_INIT': 'planning', 'IN_PROGRESS': 'running', 'COMPLETED': 'success', 'ON_HOLD': 'warning', 'CANCELLED': 'danger'
  }
  return map[status] || 'planning'
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    'PRE_INIT': '立项前', 'IN_PROGRESS': '进行中', 'COMPLETED': '已完成', 'ON_HOLD': '已暂停', 'CANCELLED': '已取消'
  }
  return map[status] || status
}

defineExpose({ setFilters, fetchData })

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.table-section {
  @include card-base;
  padding: 0;
  overflow: hidden;

  .table-container {
    overflow-x: auto;

    .modern-table {
      width: 100%;
      border-collapse: collapse;

      th, td {
        padding: $spacing-md $spacing-lg;
        text-align: left;
        border-bottom: 1px solid $divider-color;
      }

      th {
        background: $bg-secondary;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        color: $text-secondary;
        white-space: nowrap;
        &.col-actions { text-align: center; }
      }

      tbody tr {
        transition: background 0.15s ease;
        &:hover { background: rgba($accent-color, 0.03); }
        &:last-child td { border-bottom: none; }
      }

      .loading-cell, .empty-cell {
        padding: $spacing-2xl;
        text-align: center;
      }

      .loading-spinner {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: $spacing-md;
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

      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: $spacing-md;
        color: $text-muted;
        svg { width: 48px; height: 48px; opacity: 0.5; }
        p { font-size: $font-size-md; }
      }

      .col-code .code-badge {
        display: inline-block;
        padding: 4px 10px;
        background: $bg-secondary;
        border-radius: $radius-sm;
        font-size: $font-size-sm;
        font-weight: $font-weight-medium;
        color: $text-secondary;
      }

      .col-name .name-cell {
        cursor: pointer;
        .project-name { font-size: $font-size-md; font-weight: $font-weight-medium; color: $text-primary; display: block; &:hover { color: $accent-color; } }
        .project-dept { font-size: $font-size-sm; color: $text-muted; }
      }

      .col-type .type-tag {
        display: inline-block;
        padding: 4px 10px;
        background: rgba($accent-color, 0.1);
        border-radius: $radius-sm;
        font-size: $font-size-sm;
        color: $accent-color;
      }

      .col-manager .manager-cell {
        display: flex;
        align-items: center;
        gap: 8px;

        .manager-avatar {
          width: 28px;
          height: 28px;
          background: $bg-secondary;
          border-radius: $radius-md;
          display: flex;
          align-items: center;
          justify-content: center;
          svg { width: 16px; height: 16px; color: $text-muted; }
        }
        .manager-name { font-size: $font-size-md; color: $text-primary; }
      }

      .col-date .date-range {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: $font-size-sm;
        color: $text-secondary;
        svg { width: 16px; height: 16px; color: $text-muted; }
      }

      .col-budget {
        .budget-value { font-size: $font-size-md; font-weight: $font-weight-semibold; color: $text-primary; }
        .budget-empty { color: $text-muted; }
      }

      .col-status .status-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: $radius-lg;
        font-size: $font-size-sm;
        font-weight: $font-weight-medium;

        .status-dot { width: 6px; height: 6px; border-radius: 50%; }

        &.planning { background: rgba($info-color, 0.1); color: $info-color; .status-dot { background: $info-color; } }
        &.running { background: rgba($accent-color, 0.1); color: $accent-color; .status-dot { background: $accent-color; } }
        &.success { background: rgba($success-color, 0.1); color: $success-color; .status-dot { background: $success-color; } }
        &.warning { background: rgba($warning-color, 0.1); color: $warning-color; .status-dot { background: $warning-color; } }
        &.danger { background: rgba($danger-color, 0.1); color: $danger-color; .status-dot { background: $danger-color; } }
      }

      .col-actions .action-group {
        display: flex;
        align-items: center;
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
          &.workflow:hover { background: rgba($success-color, 0.1); color: $success-color; }
          &.delete:hover { background: rgba($danger-color, 0.1); color: $danger-color; }
        }
      }
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
  border-top: 1px solid $divider-color;

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
      transition: all 0.2s ease;
      &:hover { background: white; border-color: $accent-color; }
    }
  }
}

@media (max-width: 768px) {
  .pagination-section { flex-direction: column; gap: $spacing-md; .pagination-controls { width: 100%; justify-content: center; } }
}
</style>

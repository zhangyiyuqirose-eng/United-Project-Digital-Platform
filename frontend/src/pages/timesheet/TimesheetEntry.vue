<template>
  <div class="timesheet-entry-page">
    <PageHeader title="工时填报" description="填报每日工时记录并提交审批" />
    <!-- 快速填报 -->
    <div class="quick-submit">
      <div class="quick-form">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">选择项目</label>
            <div class="form-input select-wrapper">
              <input v-model="timesheetForm.projectId" type="text" placeholder="输入项目ID">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/>
              </svg>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">工作日期</label>
            <div class="form-input">
              <input v-model="timesheetForm.date" type="date" class="date-input">
            </div>
          </div>
          <div class="form-group hours-group">
            <label class="form-label">工时</label>
            <div class="hours-selector">
              <button class="hours-btn" @click="adjustHours(-0.5)">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 13H5v-2h14v2z"/>
                </svg>
              </button>
              <span class="hours-value">{{ timesheetForm.hours }}</span>
              <button class="hours-btn" @click="adjustHours(0.5)">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group full-width">
            <label class="form-label">工作内容</label>
            <textarea v-model="timesheetForm.workContent" class="form-textarea" placeholder="描述今天完成的工作内容..." rows="2"></textarea>
          </div>
        </div>
        <div class="form-actions">
          <button class="submit-btn draft" @click="saveDraft">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm2 16H5V5h11.17L19 7.83V19z"/>
            </svg>
            保存草稿
          </button>
          <button class="submit-btn primary" @click="submitTimesheetForm">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
            提交审批
          </button>
        </div>
      </div>
    </div>

    <!-- 工时列表 -->
    <div class="timesheet-list">
      <div class="list-header">
        <h3 class="list-title">我的工时记录</h3>
        <div class="list-filters">
          <select v-model="searchForm.status" class="filter-select" @change="handleSearch">
            <option value="">全部状态</option>
            <option value="DRAFT">草稿</option>
            <option value="SUBMITTED">已提交</option>
            <option value="APPROVED">已审批</option>
            <option value="REJECTED">已驳回</option>
          </select>
        </div>
      </div>

      <div class="timesheet-grid">
        <div class="timesheet-card" v-for="row in tableData" :key="row.timesheetId" :class="row.status">
          <div class="card-header">
            <div class="date-badge">
              <span class="date-day">{{ formatDateDay(row.date) }}</span>
              <span class="date-week">{{ formatDateWeek(row.date) }}</span>
            </div>
            <div class="status-tag" :class="row.status">
              <span class="status-dot"></span>
              {{ getStatusText(row.status) }}
            </div>
          </div>

          <div class="card-body">
            <div class="project-info">
              <span class="project-name">{{ row.projectName }}</span>
              <span class="hours-badge">{{ row.hours }}h</span>
            </div>
            <div class="work-content">
              <p>{{ row.workContent || '暂无工作描述' }}</p>
            </div>
            <div class="meta-info">
              <span class="create-time">创建于 {{ row.createTime }}</span>
            </div>
          </div>

          <div class="card-footer" v-if="row.status === 'DRAFT'">
            <button class="action-btn submit" @click="handleSubmit(row)">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
              提交
            </button>
            <button class="action-btn delete" @click="() => confirmDelete(row.timesheetId)">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="empty-state" v-if="!loading && tableData.length === 0">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
          </svg>
          <p>暂无工时记录</p>
          <span class="empty-tip">开始填报今天的工时吧</span>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button class="page-btn" :class="{ disabled: page === 1 }" @click="changePage(page - 1)" :disabled="page === 1">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L11.83 12z"/>
          </svg>
        </button>
        <span class="page-info">{{ page }} / {{ totalPages || 1 }}</span>
        <button class="page-btn" :class="{ disabled: page >= totalPages }" @click="changePage(page + 1)" :disabled="page >= totalPages">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getTimesheetList, createTimesheet, deleteTimesheet, submitTimesheet,
} from '@/api/modules/timesheet'

const emit = defineEmits<{
  (e: 'stats-update', stats: { totalHours: number; pending: number; draft: number }): void
}>()

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const searchForm = reactive({ projectId: '', status: '' })

const timesheetForm = reactive({ projectId: '', date: '', hours: 8, workContent: '', status: '' })

const totalPages = computed(() => Math.ceil(total.value / limit.value) || 1)

const myStats = computed(() => ({
  totalHours: tableData.value.reduce((sum, r) => sum + r.hours, 0),
  pending: tableData.value.filter(r => r.status === 'SUBMITTED').length,
  draft: tableData.value.filter(r => r.status === 'DRAFT').length,
}))

watch(myStats, (val) => emit('stats-update', val), { immediate: true })

function adjustHours(delta: number) {
  const newVal = timesheetForm.hours + delta
  if (newVal >= 0.5 && newVal <= 24) {
    timesheetForm.hours = newVal
  }
}

async function saveDraft() {
  timesheetForm.status = 'DRAFT'
  await handleAddTimesheet()
}

async function submitTimesheetForm() {
  timesheetForm.status = 'SUBMITTED'
  await handleAddTimesheet()
}

async function handleAddTimesheet() {
  if (!timesheetForm.projectId || !timesheetForm.date) {
    ElMessage.warning('请填写项目和日期')
    return
  }
  try {
    await createTimesheet(timesheetForm)
    ElMessage.success('保存成功')
    timesheetForm.workContent = ''
    fetchData()
  } catch { /* handled */ }
}

async function handleSubmit(row: any) {
  try {
    await submitTimesheet(row.timesheetId)
    ElMessage.success('提交成功')
    fetchData()
  } catch { /* handled */ }
}

async function confirmDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定删除此工时记录？', '删除确认', { type: 'warning' })
    await deleteTimesheet(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* cancelled */ }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getTimesheetList({ page: page.value, limit: limit.value, ...searchForm })
    tableData.value = res.records || []
    total.value = res.total || 0
  } catch {
    tableData.value = [
      { timesheetId: '1', projectName: '数字员工平台', date: '2026-04-25', hours: 8, workContent: '完成登录页面设计优化', status: 'APPROVED', createTime: '2026-04-25 09:30' },
      { timesheetId: '2', projectName: '企业门户升级', date: '2026-04-25', hours: 4, workContent: '编写API接口文档', status: 'SUBMITTED', createTime: '2026-04-25 14:00' },
      { timesheetId: '3', projectName: '数据治理平台', date: '2026-04-24', hours: 6, workContent: '数据库优化', status: 'DRAFT', createTime: '2026-04-24 18:00' },
    ]
    total.value = 3
  } finally {
    loading.value = false
  }
}

function handleSearch() { page.value = 1; fetchData() }
function changePage(p: number) { if (p >= 1 && p <= totalPages.value) { page.value = p; fetchData() } }

function formatDateDay(date: string): string { return date ? date.split('-')[2] : '--' }
function formatDateWeek(date: string): string {
  if (!date) return '--'
  const weeks = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return weeks[new Date(date).getDay()]
}
function getStatusText(status: string): string {
  const map: Record<string, string> = { 'DRAFT': '草稿', 'SUBMITTED': '待审批', 'APPROVED': '已通过', 'REJECTED': '已驳回' }
  return map[status] || status
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.timesheet-entry-page {
  max-width: 1400px;
}

/* 快速填报 */
.quick-submit {
  @include card-base;
  padding: $spacing-xl;
  margin-bottom: $spacing-xl;

  .quick-form {
    .form-row {
      display: flex;
      gap: $spacing-lg;
      margin-bottom: $spacing-lg;

      .form-group {
        flex: 1;

        &.full-width {
          flex: 3;
        }

        &.hours-group {
          flex: 0.8;
        }

        .form-label {
          font-size: $font-size-sm;
          font-weight: $font-weight-medium;
          color: $text-secondary;
          margin-bottom: $spacing-sm;
          display: block;
        }

        .form-input {
          display: flex;
          align-items: center;
          background: $bg-secondary;
          border: 2px solid transparent;
          border-radius: $radius-lg;
          padding: 0 16px;
          height: 48px;
          transition: all 0.25s ease;

          input, .date-input {
            flex: 1;
            border: none;
            background: transparent;
            font-size: $font-size-md;
            color: $text-primary;
            &:focus { outline: none; }
          }

          svg {
            width: 20px;
            height: 20px;
            color: $text-muted;
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
          svg {
            position: absolute;
            right: 16px;
          }
        }

        .hours-selector {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: $spacing-lg;
          padding: $spacing-md;
          background: $bg-secondary;
          border-radius: $radius-lg;

          .hours-btn {
            width: 36px;
            height: 36px;
            border-radius: $radius-md;
            background: white;
            border: 1px solid $border-color;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: $text-secondary;
            transition: all 0.2s ease;

            svg { width: 20px; height: 20px; }

            &:hover {
              background: $accent-color;
              color: white;
              border-color: $accent-color;
            }
          }

          .hours-value {
            font-size: $font-size-xl;
            font-weight: $font-weight-bold;
            color: $text-primary;
          }
        }

        .form-textarea {
          width: 100%;
          padding: $spacing-md $spacing-lg;
          background: $bg-secondary;
          border: 2px solid transparent;
          border-radius: $radius-lg;
          font-size: $font-size-md;
          color: $text-primary;
          resize: none;
          transition: all 0.25s ease;

          &:hover { background: $bg-tertiary; }
          &:focus {
            background: white;
            border-color: $accent-color;
            box-shadow: 0 0 0 4px rgba(49, 130, 206, 0.1);
          }
        }
      }
    }

    .form-actions {
      display: flex;
      gap: $spacing-md;
      justify-content: flex-end;

      .submit-btn {
        display: flex;
        align-items: center;
        gap: $spacing-sm;
        padding: $spacing-md $spacing-xl;
        border-radius: $radius-lg;
        font-size: $font-size-md;
        font-weight: $font-weight-semibold;
        cursor: pointer;
        transition: all 0.25s ease;

        svg { width: 18px; height: 18px; }

        &.draft {
          background: $bg-secondary;
          border: 2px solid $border-color;
          color: $text-secondary;

          &:hover {
            background: white;
            border-color: $text-muted;
            color: $text-primary;
          }
        }

        &.primary {
          @include button-primary;
        }
      }
    }
  }
}

/* 工时列表 */
.timesheet-list {
  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-xl;

    .list-title {
      font-size: $font-size-lg;
      font-weight: $font-weight-semibold;
      color: $text-primary;
    }

    .filter-select {
      padding: $spacing-sm $spacing-lg;
      background: white;
      border: 1px solid $border-color;
      border-radius: $radius-md;
      font-size: $font-size-sm;
      color: $text-secondary;
      cursor: pointer;
    }
  }

  .timesheet-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: $spacing-lg;

    .timesheet-card {
      @include card-base;
      padding: 0;
      overflow: hidden;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: $spacing-lg;
        background: linear-gradient(135deg, $bg-secondary, $bg-tertiary);

        .date-badge {
          display: flex;
          flex-direction: column;

          .date-day {
            font-size: $font-size-xl;
            font-weight: $font-weight-bold;
            color: $text-primary;
          }

          .date-week {
            font-size: $font-size-sm;
            color: $text-muted;
          }
        }

        .status-tag {
          display: flex;
          align-items: center;
          gap: $spacing-xs;
          padding: 6px 12px;
          border-radius: $radius-lg;
          font-size: $font-size-sm;
          font-weight: $font-weight-medium;

          .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
          }

          &.DRAFT {
            background: rgba($text-muted, 0.15);
            color: $text-muted;
            .status-dot { background: $text-muted; }
          }

          &.SUBMITTED {
            background: rgba($warning-color, 0.15);
            color: $warning-color;
            .status-dot { background: $warning-color; }
          }

          &.APPROVED {
            background: rgba($success-color, 0.15);
            color: $success-color;
            .status-dot { background: $success-color; }
          }

          &.REJECTED {
            background: rgba($danger-color, 0.15);
            color: $danger-color;
            .status-dot { background: $danger-color; }
          }
        }
      }

      .card-body {
        padding: $spacing-lg;

        .project-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: $spacing-sm;

          .project-name {
            font-size: $font-size-md;
            font-weight: $font-weight-medium;
            color: $text-primary;
          }

          .hours-badge {
            padding: 4px 12px;
            background: rgba($accent-color, 0.15);
            border-radius: $radius-md;
            font-size: $font-size-md;
            font-weight: $font-weight-bold;
            color: $accent-color;
          }
        }

        .work-content p {
          font-size: $font-size-sm;
          color: $text-secondary;
          margin-bottom: $spacing-sm;
        }

        .meta-info .create-time {
          font-size: $font-size-xs;
          color: $text-muted;
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
          gap: $spacing-xs;
          padding: 8px;
          border-radius: $radius-md;
          font-size: $font-size-sm;
          font-weight: $font-weight-medium;
          cursor: pointer;
          transition: all 0.2s ease;

          svg { width: 16px; height: 16px; }

          &.submit {
            background: $accent-color;
            border: none;
            color: white;
            &:hover { background: $primary-light; }
          }

          &.delete {
            background: transparent;
            border: 1px solid $border-color;
            color: $text-muted;
            &:hover { background: rgba($danger-color, 0.1); color: $danger-color; border-color: $danger-color; }
          }
        }
      }
    }

    .empty-state {
      grid-column: span 3;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: $spacing-md;
      padding: $spacing-2xl;
      color: $text-muted;

      svg { width: 48px; height: 48px; opacity: 0.5; }
      .empty-tip { font-size: $font-size-sm; }
    }
  }

  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: $spacing-md;
    margin-top: $spacing-xl;

    .page-btn {
      width: 36px;
      height: 36px;
      border-radius: $radius-md;
      background: white;
      border: 1px solid $border-color;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      color: $text-secondary;
      transition: all 0.2s ease;

      svg { width: 20px; height: 20px; }

      &:hover:not(.disabled) { border-color: $accent-color; color: $accent-color; }
      &.disabled { opacity: 0.5; cursor: not-allowed; }
    }

    .page-info {
      font-size: $font-size-md;
      color: $text-secondary;
    }
  }
}

@media (max-width: 900px) {
  .timesheet-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .quick-form .form-row {
    flex-direction: column;
  }
}

@media (max-width: 600px) {
  .timesheet-grid {
    grid-template-columns: 1fr;
  }
}
</style>

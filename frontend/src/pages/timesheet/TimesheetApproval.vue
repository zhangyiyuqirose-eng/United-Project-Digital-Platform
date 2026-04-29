<template>
  <div class="timesheet-approval-page">
    <PageHeader title="工时审批" description="审批团队成员提交的工时记录" />
    <div class="tab-content">
    <div class="approval-section">
      <div class="section-header">
        <h3 class="section-title">待审批工时</h3>
        <span class="pending-count">共 {{ approvalTotal }} 条待处理</span>
      </div>

      <div class="approval-table">
        <div class="table-row header-row">
          <span class="col submitter">提交人</span>
          <span class="col project">项目</span>
          <span class="col date">日期</span>
          <span class="col hours">工时</span>
          <span class="col content">工作内容</span>
          <span class="col time">提交时间</span>
          <span class="col actions">操作</span>
        </div>

        <div class="table-row data-row" v-for="row in approvalData" :key="row.approvalId">
          <span class="col submitter">
            <div class="user-avatar">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
            {{ row.userName }}
          </span>
          <span class="col project">{{ row.projectName }}</span>
          <span class="col date">{{ row.date }}</span>
          <span class="col hours">
            <span class="hours-num">{{ row.hours }}</span>
          </span>
          <span class="col content">
            <span class="content-preview">{{ truncate(row.workContent, 30) }}</span>
          </span>
          <span class="col time">{{ row.submitTime }}</span>
          <span class="col actions">
            <button class="approve-btn" @click="handleApprove(row)">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            </button>
            <button class="reject-btn" @click="handleReject(row)">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </button>
          </span>
        </div>

        <div class="empty-table" v-if="!approvalLoading && approvalData.length === 0">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          <span>所有工时已审批完毕</span>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getApprovalQueue, approveTimesheet, rejectTimesheet } from '@/api/modules/timesheet'

const emit = defineEmits<{
  (e: 'count-update', count: number): void
}>()

const approvalLoading = ref(false)
const approvalData = ref<any[]>([])
const approvalTotal = ref(0)
const approvalPage = ref(1)

watch(approvalTotal, (val) => emit('count-update', val), { immediate: true })

async function fetchApprovals() {
  approvalLoading.value = true
  try {
    const res = await getApprovalQueue({ page: approvalPage.value, limit: 10 })
    approvalData.value = res.records || []
    approvalTotal.value = res.total || 0
  } catch {
    approvalData.value = [
      { approvalId: '1', userName: '张三', projectName: '数字员工平台', date: '2026-04-25', hours: 8, workContent: '完成登录页面设计优化', submitTime: '2026-04-25 09:30' },
      { approvalId: '2', userName: '李四', projectName: '企业门户升级', date: '2026-04-25', hours: 4, workContent: '编写API接口文档', submitTime: '2026-04-25 14:00' },
    ]
    approvalTotal.value = 2
  } finally {
    approvalLoading.value = false
  }
}

async function handleApprove(row: any) {
  try {
    await approveTimesheet(row.approvalId, '')
    ElMessage.success('审批通过')
    fetchApprovals()
  } catch { /* handled */ }
}

async function handleReject(row: any) {
  try {
    await rejectTimesheet(row.approvalId, '不符合要求')
    ElMessage.success('已驳回')
    fetchApprovals()
  } catch { /* handled */ }
}

function truncate(text: string, len: number): string {
  return text?.length > len ? text.slice(0, len) + '...' : text || '--'
}

onMounted(fetchApprovals)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.timesheet-approval-page {
  max-width: 1400px;
}

/* 审批队列 */
.approval-section {
  @include card-base;
  padding: 0;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-lg;
    border-bottom: 1px solid $divider-color;

    .section-title {
      font-size: $font-size-lg;
      font-weight: $font-weight-semibold;
      color: $text-primary;
    }

    .pending-count {
      font-size: $font-size-sm;
      color: $text-muted;
    }
  }

  .approval-table {
    .table-row {
      display: flex;
      align-items: center;
      padding: $spacing-md $spacing-lg;
      gap: $spacing-md;

      &.header-row {
        background: $bg-secondary;
        font-size: $font-size-sm;
        font-weight: $font-weight-medium;
        color: $text-muted;
      }

      &.data-row {
        border-bottom: 1px solid $divider-color;
        transition: background 0.15s ease;
        &:hover { background: rgba($accent-color, 0.03); }
        &:last-child { border-bottom: none; }
      }

      .col {
        &.submitter {
          width: 100px;
          display: flex;
          align-items: center;
          gap: $spacing-sm;

          .user-avatar {
            width: 24px;
            height: 24px;
            background: $bg-secondary;
            border-radius: $radius-md;
            display: flex;
            align-items: center;
            justify-content: center;
            svg { width: 14px; height: 14px; color: $text-muted; }
          }
        }

        &.project { flex: 1; }
        &.date { width: 80px; }
        &.hours { width: 60px; .hours-num { font-weight: $font-weight-semibold; color: $accent-color; } }
        &.content { width: 200px; .content-preview { font-size: $font-size-sm; color: $text-secondary; } }
        &.time { width: 120px; font-size: $font-size-sm; color: $text-muted; }
        &.actions {
          width: 80px;
          display: flex;
          gap: $spacing-sm;

          .approve-btn, .reject-btn {
            width: 32px;
            height: 32px;
            border-radius: $radius-md;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;

            svg { width: 18px; height: 18px; }
          }

          .approve-btn {
            background: rgba($success-color, 0.1);
            border: none;
            color: $success-color;
            &:hover { background: $success-color; color: white; }
          }

          .reject-btn {
            background: rgba($danger-color, 0.1);
            border: none;
            color: $danger-color;
            &:hover { background: $danger-color; color: white; }
          }
        }
      }
    }

    .empty-table {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: $spacing-sm;
      padding: $spacing-xl;
      color: $text-muted;
      svg { width: 32px; height: 32px; color: $success-color; }
    }
  }
}

@media (max-width: 600px) {
  .approval-table .table-row {
    flex-wrap: wrap;
    .col { min-width: 80px; }
  }
}
</style>

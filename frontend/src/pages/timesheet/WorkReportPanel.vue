<template>
  <div class="work-report-page">
    <PageHeader title="工作周报" description="查看和提交每周工作汇报">
      <button class="create-report-btn" @click="showReportDialog = true">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        填写周报
      </button>
    </PageHeader>
    <div class="tab-content">
    <div class="report-section">
      <div class="section-header">
        <h3 class="section-title">周报列表</h3>
      </div>

      <div class="report-list">
        <div class="report-card" v-for="row in reportData" :key="row.reportId">
          <div class="report-header">
            <div class="week-range">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM9 10H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm-8 4H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/>
              </svg>
              <span>{{ row.weekStart }} ~ {{ row.weekEnd }}</span>
            </div>
            <div class="status-badge" :class="row.status">
              {{ getReportStatus(row.status) }}
            </div>
          </div>
          <div class="report-body">
            <p class="report-content">{{ row.content }}</p>
          </div>
          <div class="report-footer">
            <span class="submit-time">{{ row.createTime }}</span>
          </div>
        </div>

        <div class="empty-reports" v-if="reportData.length === 0">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
          </svg>
          <span>暂无周报记录</span>
        </div>
      </div>
    </div>
    </div>

    <!-- 周报对话框 -->
    <div class="dialog-overlay" v-if="showReportDialog" @click.self="showReportDialog = false">
      <div class="dialog-card">
        <div class="dialog-header">
          <h3>填写周报</h3>
          <button class="close-btn" @click="showReportDialog = false">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label class="form-label">本周工作总结</label>
            <textarea v-model="reportContent" class="form-textarea" rows="5" placeholder="描述本周完成的主要工作内容..."></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="cancel-btn" @click="showReportDialog = false">取消</button>
          <button class="confirm-btn" @click="submitReport">提交周报</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getWorkReports, createWorkReport } from '@/api/modules/timesheet'

const reportData = ref<any[]>([])
const showReportDialog = ref(false)
const reportContent = ref('')

async function fetchReports() {
  try {
    const res = await getWorkReports({ page: 1, limit: 10 })
    reportData.value = res.records || []
  } catch {
    reportData.value = [
      { reportId: '1', weekStart: '2026-04-20', weekEnd: '2026-04-26', content: '本周完成了登录页面、Dashboard、项目列表页的UI优化工作。', status: 'SUBMITTED', createTime: '2026-04-26' },
    ]
  }
}

async function submitReport() {
  if (!reportContent.value) {
    ElMessage.warning('请填写周报内容')
    return
  }
  try {
    await createWorkReport({ content: reportContent.value })
    ElMessage.success('周报提交成功')
    showReportDialog.value = false
    reportContent.value = ''
    fetchReports()
  } catch { /* handled */ }
}

function getReportStatus(status: string): string {
  const map: Record<string, string> = { 'DRAFT': '草稿', 'SUBMITTED': '已提交', 'APPROVED': '已确认' }
  return map[status] || status
}

onMounted(fetchReports)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.work-report-page {
  max-width: 1400px;

  .create-report-btn {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    @include button-primary;
    padding: $spacing-md $spacing-xl;
    font-size: $font-size-md;

    svg { width: 18px; height: 18px; }
  }
}

/* 周报管理 */
.report-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-xl;

    .section-title {
      font-size: $font-size-lg;
      font-weight: $font-weight-semibold;
      color: $text-primary;
    }
  }

  .report-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;

    .report-card {
      @include card-base;
      padding: $spacing-lg;

      .report-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: $spacing-md;

        .week-range {
          display: flex;
          align-items: center;
          gap: $spacing-sm;
          font-size: $font-size-md;
          font-weight: $font-weight-medium;
          color: $text-primary;

          svg { width: 18px; height: 18px; color: $text-muted; }
        }

        .status-badge {
          padding: $spacing-xs $spacing-md;
          border-radius: $radius-lg;
          font-size: $font-size-sm;
          font-weight: $font-weight-medium;

          &.DRAFT { background: rgba($text-muted, 0.15); color: $text-muted; }
          &.SUBMITTED { background: rgba($accent-color, 0.15); color: $accent-color; }
          &.APPROVED { background: rgba($success-color, 0.15); color: $success-color; }
        }
      }

      .report-body {
        .report-content {
          font-size: $font-size-md;
          color: $text-secondary;
          line-height: 1.6;
        }
      }

      .report-footer {
        margin-top: $spacing-sm;
        .submit-time {
          font-size: $font-size-xs;
          color: $text-muted;
        }
      }
    }

    .empty-reports {
      @include card-base;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: $spacing-sm;
      padding: $spacing-xl;
      color: $text-muted;

      svg { width: 32px; height: 32px; opacity: 0.5; }
    }
  }
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;

  .dialog-card {
    background: white;
    border-radius: $radius-xl;
    width: 500px;
    max-width: 90vw;
    animation: dialogEnter 0.3s ease;

    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-lg;
      border-bottom: 1px solid $divider-color;

      h3 {
        font-size: $font-size-lg;
        font-weight: $font-weight-semibold;
        color: $text-primary;
      }

      .close-btn {
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
        svg { width: 20px; height: 20px; }
        &:hover { background: $bg-secondary; color: $danger-color; }
      }
    }

    .dialog-body {
      padding: $spacing-lg;

      .form-label {
        font-size: $font-size-sm;
        font-weight: $font-weight-medium;
        color: $text-secondary;
        margin-bottom: $spacing-sm;
        display: block;
      }

      .form-textarea {
        width: 100%;
        padding: $spacing-md;
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

    .dialog-footer {
      display: flex;
      gap: $spacing-sm;
      padding: $spacing-lg;
      border-top: 1px solid $divider-color;

      .cancel-btn, .confirm-btn {
        flex: 1;
        padding: 12px;
        border-radius: $radius-lg;
        font-size: $font-size-md;
        font-weight: $font-weight-medium;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .cancel-btn {
        background: $bg-secondary;
        border: 1px solid $border-color;
        color: $text-secondary;
        &:hover { background: $bg-tertiary; }
      }

      .confirm-btn {
        background: $accent-gradient;
        border: none;
        color: white;
        &:hover { transform: translateY(-1px); box-shadow: $shadow-md; }
      }
    }
  }
}

@keyframes dialogEnter {
  from { opacity: 0; transform: translateY(-20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
</style>

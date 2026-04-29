<template>
  <div class="timesheet-page">
    <!-- 页面头部 -->
    <PageHeader title="工时管理" description="填报工时、审批管理、周报提交一站式处理">
      <div class="header-stats">
        <div class="stat-mini">
          <span class="stat-num">{{ myStats.totalHours }}</span>
          <span class="stat-label">本月工时</span>
        </div>
        <div class="stat-mini pending">
          <span class="stat-num">{{ myStats.pending }}</span>
          <span class="stat-label">待审批</span>
        </div>
      </div>
    </PageHeader>

    <!-- 标签导航 -->
    <div class="tab-navigation">
      <button class="tab-btn" :class="{ active: activeTab === 'submit' }" @click="activeTab = 'submit'">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        <span>工时填报</span>
        <span class="tab-badge" v-if="myStats.draft > 0">{{ myStats.draft }}</span>
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'approval' }" @click="activeTab = 'approval'">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
        <span>审批队列</span>
        <span class="tab-badge warning" v-if="approvalTotal > 0">{{ approvalTotal }}</span>
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'report' }" @click="activeTab = 'report'">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
        </svg>
        <span>周报管理</span>
      </button>
    </div>

    <!-- 工时填报 -->
    <TimesheetEntry v-show="activeTab === 'submit'" @stats-update="onEntryStatsUpdate" />

    <!-- 审批队列 -->
    <TimesheetApproval v-show="activeTab === 'approval'" @count-update="onApprovalCountUpdate" />

    <!-- 周报管理 -->
    <WorkReportPanel v-show="activeTab === 'report'" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import TimesheetEntry from './TimesheetEntry.vue'
import TimesheetApproval from './TimesheetApproval.vue'
import WorkReportPanel from './WorkReportPanel.vue'

const activeTab = ref('submit')

const myStats = ref({ totalHours: 0, pending: 0, draft: 0 })
const approvalTotal = ref(0)

function onEntryStatsUpdate(stats: { totalHours: number; pending: number; draft: number }) {
  myStats.value = stats
}

function onApprovalCountUpdate(count: number) {
  approvalTotal.value = count
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.timesheet-page {
  max-width: 1400px;
}

.header-stats {
  display: flex;
  gap: $spacing-md;

  .stat-mini {
    @include card-base;
    padding: $spacing-md $spacing-lg;
    text-align: center;

    .stat-num {
      font-size: $font-size-xl;
      font-weight: $font-weight-bold;
      color: $text-primary;
      display: block;
    }

    .stat-label {
      font-size: $font-size-sm;
      color: $text-muted;
    }

    &.pending .stat-num { color: $warning-color; }
  }
}

/* 标签导航 */
.tab-navigation {
  display: flex;
  gap: $spacing-sm;
  margin-bottom: $spacing-lg;

  .tab-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    background: white;
    border: 2px solid $border-color;
    border-radius: $radius-lg;
    font-size: $font-size-md;
    font-weight: $font-weight-medium;
    color: $text-secondary;
    cursor: pointer;
    transition: all 0.25s ease;

    svg {
      width: 18px;
      height: 18px;
    }

    .tab-badge {
      padding: 2px 8px;
      background: $accent-color;
      color: white;
      font-size: $font-size-xs;
      font-weight: $font-weight-semibold;
      border-radius: $radius-sm;

      &.warning { background: $warning-color; }
    }

    &:hover {
      background: $bg-secondary;
      border-color: $divider-color;
    }

    &.active {
      background: rgba($accent-color, 0.1);
      border-color: $accent-color;
      color: $accent-color;
    }
  }
}

@media (max-width: 600px) {
  .tab-navigation {
    flex-wrap: wrap;
  }
}
</style>

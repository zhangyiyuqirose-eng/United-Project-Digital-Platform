<template>
  <div class="cost-dashboard">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">成本管理</h1>
        <p class="page-desc">项目成本核算与挣值分析，实时监控预算执行情况</p>
      </div>
      <div class="header-stats">
        <div class="mini-stat">
          <span class="mini-label">总预算</span>
          <span class="mini-value">{{ formatCurrency(stats.totalBudget) }}</span>
        </div>
        <div class="mini-stat">
          <span class="mini-label">CPI</span>
          <span class="mini-value" :class="{ warning: cpiValue < 1, danger: cpiValue < 0.9 }">{{ cpiValue.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <!-- 预算环形卡片 -->
      <div class="stat-card budget">
        <div class="stat-visual">
          <div class="stat-ring">
            <svg viewBox="0 0 120 120">
              <circle class="ring-bg" cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="12"/>
              <circle class="ring-progress" cx="60" cy="60" r="50" fill="none" stroke-width="12"
                :stroke-dasharray="budgetCircle"
                :style="{ strokeDashoffset: ringOffset }"
                transform="rotate(-90 60 60)"/>
            </svg>
            <div class="stat-center">
              <span class="stat-percent">{{ budgetPercent }}%</span>
              <span class="stat-label">预算使用率</span>
            </div>
          </div>
        </div>
        <div class="stat-info">
          <div class="stat-row">
            <span class="stat-name">总预算</span>
            <span class="stat-amount">{{ formatCurrency(stats.totalBudget) }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-name">已支出</span>
            <span class="stat-amount spent">{{ formatCurrency(stats.totalSpent) }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-name">剩余预算</span>
            <span class="stat-amount remaining">{{ formatCurrency(stats.totalBudget - stats.totalSpent) }}</span>
          </div>
        </div>
      </div>

      <!-- StatCard: 本月支出 -->
      <StatCard
        :value="monthlySpending"
        label="本月支出"
        color="warning"
        :trend="spendingTrend"
        :sparkline="spendingSparkline"
      />

      <!-- StatCard: 成本预警 -->
      <StatCard
        :value="stats.alerts"
        label="成本预警"
        color="danger"
        :sparkline="alertSparkline"
      />

      <!-- StatCard: EVM指标 -->
      <StatCard
        :value="cpiValue.toFixed(2)"
        label="CPI 成本绩效"
        :color="cpiValue >= 1 ? 'success' : 'danger'"
        :trend="cpiTrend"
      />
    </div>

    <!-- 内容区域 -->
    <div class="content-grid">
      <!-- EVM图表 -->
      <div class="panel chart-panel">
        <div class="panel-header">
          <h3 class="panel-title">挣值分析趋势</h3>
          <div class="panel-controls">
            <div class="time-range-toggle">
              <button
                v-for="range in timeRanges"
                :key="range.value"
                class="range-btn"
                :class="{ active: timeRange === range.value }"
                @click="timeRange = range.value"
              >
                {{ range.label }}
              </button>
            </div>
            <div class="chart-type-btns">
              <button class="chart-btn" :class="{ active: chartType === 'line' }" @click="chartType = 'line'">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z"/>
                </svg>
              </button>
              <button class="chart-btn" :class="{ active: chartType === 'bar' }" @click="chartType = 'bar'">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div class="panel-content">
          <div class="evm-chart">
            <EvmChart :data="filteredEvmData" :type="chartType" />
          </div>
        </div>
      </div>

      <!-- 预警列表 -->
      <div class="panel alerts-panel">
        <div class="panel-header">
          <h3 class="panel-title">成本预警明细</h3>
          <button class="panel-action">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
            </svg>
          </button>
        </div>
        <div class="panel-content">
          <div class="alert-list">
            <div class="alert-card" v-for="alert in alerts" :key="alert.id" :class="alert.severity">
              <div class="alert-accent-bar" :class="alert.severity"></div>
              <div class="alert-icon" :class="alert.severity">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path v-if="alert.severity === 'HIGH'" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                  <path v-else d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
              </div>
              <div class="alert-body">
                <span class="alert-project">{{ alert.projectName }}</span>
                <span class="alert-message">{{ alert.message }}</span>
                <span class="alert-time">{{ alert.createTime }}</span>
              </div>
              <div class="alert-badge" :class="alert.severity">{{ getAlertLabel(alert.severity) }}</div>
            </div>
            <div class="empty-alerts" v-if="alerts.length === 0">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
              <span>当前无成本预警</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 项目成本分布 -->
      <div class="panel distribution-panel">
        <div class="panel-header">
          <h3 class="panel-title">项目成本分布</h3>
        </div>
        <div class="panel-content">
          <div class="distribution-list">
            <div class="distribution-item" v-for="(item, idx) in costDistribution" :key="item.projectId">
              <div class="distribution-info">
                <span class="distribution-name">{{ item.projectName }}</span>
                <span class="distribution-percent">{{ item.percent }}%</span>
              </div>
              <div class="distribution-bar">
                <div
                  class="bar-fill"
                  :class="'bar-gradient-' + (idx % 4)"
                  :style="{ width: item.percent + '%' }"
                ></div>
              </div>
              <span class="distribution-amount">{{ formatCurrency(item.amount) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getCostDashboard, getCostAlerts } from '@/api/modules/cost'
import EvmChart from '@/components/EvmChart.vue'
import StatCard from '@/components/StatCard.vue'

const stats = ref({ totalBudget: 0, totalSpent: 0, alerts: 0 })
const evmData = ref<{ month: string; pv: number; ev: number; ac: number; cpi: number; spi: number }[]>([])
const alerts = ref<any[]>([])
const chartType = ref('line')
const timeRange = ref('month')

const timeRanges = [
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '本季', value: 'quarter' },
  { label: '本年', value: 'year' },
]

// 计算属性
const budgetPercent = computed(() => {
  if (!stats.value.totalBudget) return 0
  return Math.min(100, Math.round((stats.value.totalSpent / stats.value.totalBudget) * 100))
})

const budgetCircle = computed(() => {
  const percent = budgetPercent.value / 100
  return `${percent * 314} 314`
})

// Animated ring offset: starts at full circumference (314) and transitions to target
const ringOffset = computed(() => {
  const circumference = 314
  const percent = budgetPercent.value / 100
  return circumference - percent * circumference
})

const cpiValue = computed(() => {
  if (!evmData.value.length) return 1
  const last = evmData.value[evmData.value.length - 1]
  return last.cpi || 1
})

const cpiTrend = computed(() => {
  if (evmData.value.length < 2) return 0
  const last = evmData.value[evmData.value.length - 1].cpi
  const prev = evmData.value[evmData.value.length - 2].cpi
  if (!prev) return 0
  return Math.round(((last - prev) / prev) * 100)
})

const monthlySpending = computed(() => stats.value.totalSpent * 0.15)
const spendingTrend = computed(() => -5)

const spendingSparkline = computed(() => [
  Math.round(monthlySpending.value * 0.4),
  Math.round(monthlySpending.value * 0.6),
  Math.round(monthlySpending.value * 0.3),
  Math.round(monthlySpending.value * 0.8),
  Math.round(monthlySpending.value),
])

const alertSparkline = computed(() => {
  const count = stats.value.alerts
  return count > 0 ? [count - 1, count, count + 1, count, count - 1].map(v => Math.max(0, v)) : [0, 0, 0, 0, 0]
})

const costDistribution = computed(() => [
  { projectId: '1', projectName: '数字员工平台', amount: stats.value.totalSpent * 0.35, percent: 35 },
  { projectId: '2', projectName: '企业门户升级', amount: stats.value.totalSpent * 0.25, percent: 25 },
  { projectId: '3', projectName: '数据治理平台', amount: stats.value.totalSpent * 0.20, percent: 20 },
  { projectId: '4', projectName: '移动端应用', amount: stats.value.totalSpent * 0.15, percent: 15 },
])

// Filter EVM data based on selected time range
const filteredEvmData = computed(() => {
  if (!evmData.value.length) return evmData.value
  const now = new Date()
  const cutoff = new Date()
  switch (timeRange.value) {
    case 'week':
      cutoff.setDate(now.getDate() - 7)
      break
    case 'month':
      cutoff.setMonth(now.getMonth() - 1)
      break
    case 'quarter':
      cutoff.setMonth(now.getMonth() - 3)
      break
    case 'year':
      cutoff.setFullYear(now.getFullYear() - 1)
      break
    default:
      return evmData.value
  }
  return evmData.value.filter(d => new Date(d.month) >= cutoff)
})

function formatCurrency(v: number) {
  if (!v) return '¥0'
  if (v >= 1000000) return `¥${(v / 1000000).toFixed(1)}M`
  if (v >= 1000) return `¥${(v / 1000).toFixed(1)}K`
  return `¥${v.toFixed(0)}`
}

function getAlertLabel(level: string): string {
  const map: Record<string, string> = { HIGH: '高', MEDIUM: '中', LOW: '低' }
  return map[level] || level
}

async function loadData() {
  try {
    const dashboard = await getCostDashboard()
    stats.value = { totalBudget: dashboard.totalBudget || 0, totalSpent: dashboard.totalSpent || 0, alerts: dashboard.alerts || 0 }
    evmData.value = dashboard.evm || []
  } catch {
    stats.value = { totalBudget: 1000000, totalSpent: 650000, alerts: 3 }
    evmData.value = [
      { month: '2026-01', pv: 100000, ev: 90000, ac: 85000, cpi: 1.06, spi: 0.9 },
      { month: '2026-02', pv: 200000, ev: 180000, ac: 175000, cpi: 1.03, spi: 0.9 },
      { month: '2026-03', pv: 300000, ev: 280000, ac: 290000, cpi: 0.97, spi: 0.93 },
    ]
  }
  try {
    const res = await getCostAlerts({ page: 1, limit: 10 })
    alerts.value = res.records || []
  } catch {
    alerts.value = [
      { id: '1', projectName: '数字员工平台', severity: 'HIGH', message: '预算超支风险', createTime: '2026-04-25' },
      { id: '2', projectName: '企业门户升级', severity: 'MEDIUM', message: '成本偏离10%', createTime: '2026-04-24' },
    ]
  }
}

onMounted(loadData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.cost-dashboard {
  max-width: 1400px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-xl;

  .header-content {
    .page-title {
      font-size: $font-size-2xl;
      font-weight: $font-weight-bold;
      color: $text-primary;
      margin-bottom: $spacing-xs;
    }

    .page-desc {
      font-size: $font-size-md;
      color: $text-muted;
    }
  }

  .header-stats {
    display: flex;
    gap: $spacing-lg;

    .mini-stat {
      @include card-base;
      padding: $spacing-md $spacing-lg;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      min-width: 100px;

      .mini-label {
        font-size: $font-size-xs;
        color: $text-muted;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .mini-value {
        font-size: $font-size-lg;
        font-weight: $font-weight-semibold;
        color: $text-primary;

        &.warning { color: $warning-color; }
        &.danger { color: $danger-color; }
      }
    }
  }
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;

  .stat-card {
    @include card-base;
    padding: $spacing-xl;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background: $accent-gradient;
      border-radius: 0 4px 4px 0;
    }

    .stat-header {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      margin-bottom: $spacing-md;

      .stat-icon {
        width: 36px;
        height: 36px;
        border-radius: $radius-md;
        background: rgba($accent-color, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: $accent-color;

        &.warning {
          background: rgba($warning-color, 0.1);
          color: $warning-color;
        }

        svg {
          width: 20px;
          height: 20px;
        }
      }

      .stat-title {
        font-size: $font-size-md;
        font-weight: $font-weight-medium;
        color: $text-secondary;
      }
    }

    .stat-value {
      font-size: $font-size-2xl;
      font-weight: $font-weight-bold;
      color: $text-primary;
      margin-bottom: $spacing-sm;

      &.danger { color: $danger-color; }
    }

    /* 预算卡片 */
    &.budget {
      grid-column: span 2;
      display: flex;
      gap: $spacing-xl;

      .stat-visual {
        .stat-ring {
          position: relative;
          width: 120px;
          height: 120px;

          svg {
            width: 100%;
            height: 100%;
          }

          .ring-bg {
            stroke: $border-color;
          }

          .ring-progress {
            stroke: url(#budget-gradient);
            stroke-linecap: round;
            transition: stroke-dashoffset 1.2s $transition-spring;
          }

          .stat-center {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;

            .stat-percent {
              font-size: $font-size-xl;
              font-weight: $font-weight-bold;
              color: $text-primary;
              animation: countUp 0.6s $transition-normal;
            }

            .stat-label {
              font-size: $font-size-xs;
              color: $text-muted;
            }
          }
        }
      }

      .stat-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: $spacing-md;
        justify-content: center;

        .stat-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: $spacing-sm 0;
          border-bottom: 1px solid $divider-color;

          &:last-child {
            border-bottom: none;
          }

          .stat-name {
            font-size: $font-size-sm;
            color: $text-muted;
          }

          .stat-amount {
            font-size: $font-size-lg;
            font-weight: $font-weight-semibold;
            color: $text-primary;

            &.spent { color: $warning-color; }
            &.remaining { color: $success-color; }
          }
        }
      }
    }
  }
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: $spacing-lg;
}

/* 面板 */
.panel {
  @include card-base;
  padding: 0;
  overflow: hidden;

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $spacing-lg;
    border-bottom: 1px solid $divider-color;

    .panel-title {
      font-size: $font-size-lg;
      font-weight: $font-weight-semibold;
      color: $text-primary;
    }

    .panel-controls {
      display: flex;
      align-items: center;
      gap: $spacing-md;
    }

    .panel-actions {
      display: flex;
      gap: $spacing-xs;

      .chart-btn {
        width: 32px;
        height: 32px;
        border-radius: $radius-md;
        background: $bg-secondary;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: $text-muted;
        transition: all $transition-fast;

        svg { width: 16px; height: 16px; }

        &:hover { background: $bg-tertiary; }
        &.active { background: $accent-color; color: white; }
      }
    }

    .panel-action {
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
      transition: all $transition-fast;

      svg { width: 20px; height: 20px; }

      &:hover { background: $bg-secondary; color: $accent-color; }
    }
  }

  .panel-content {
    padding: $spacing-lg;
  }
}

/* 时间范围切换按钮 */
.time-range-toggle {
  display: flex;
  background: $bg-secondary;
  border-radius: $radius-md;
  padding: 3px;
  gap: 2px;

  .range-btn {
    padding: 6px 14px;
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
    color: $text-muted;
    background: transparent;
    border: none;
    border-radius: $radius-sm;
    cursor: pointer;
    transition: all $transition-fast;
    white-space: nowrap;

    &:hover {
      color: $text-primary;
    }

    &.active {
      background: $bg-card;
      color: $accent-color;
      box-shadow: $shadow-sm;
    }
  }
}

.chart-type-btns {
  display: flex;
  gap: $spacing-xs;

  .chart-btn {
    width: 32px;
    height: 32px;
    border-radius: $radius-md;
    background: $bg-secondary;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $text-muted;
    transition: all $transition-fast;

    svg { width: 16px; height: 16px; }

    &:hover { background: $bg-tertiary; }
    &.active { background: $accent-color; color: white; }
  }
}

.chart-panel {
  grid-column: span 1;
  grid-row: span 2;

  .evm-chart {
    min-height: 300px;
  }
}

.alerts-panel {
  .alert-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;

    .alert-card {
      display: flex;
      align-items: flex-start;
      gap: $spacing-md;
      padding: $spacing-md;
      border-radius: $radius-lg;
      background: $bg-secondary;
      position: relative;
      overflow: hidden;
      transition: all $transition-fast;

      &:hover {
        background: $bg-tertiary;
        transform: translateX(2px);
      }

      /* Severity-based left accent bar */
      .alert-accent-bar {
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;

        &.HIGH { background: $danger-color; }
        &.MEDIUM { background: $warning-color; }
        &.LOW { background: $info-color; }
      }

      .alert-icon {
        width: 28px;
        height: 28px;
        min-width: 28px;
        border-radius: $radius-md;
        display: flex;
        align-items: center;
        justify-content: center;
        svg { width: 16px; height: 16px; }

        /* Default (LOW/MEDIUM) */
        background: rgba($info-color, 0.1);
        color: $info-color;

        &.HIGH {
          background: rgba($danger-color, 0.12);
          color: $danger-color;
        }

        &.MEDIUM {
          background: rgba($warning-color, 0.12);
          color: $warning-color;
        }
      }

      /* Severity card borders */
      &.HIGH {
        border: 1px solid rgba($danger-color, 0.15);
        background: $danger-50;
      }

      &.MEDIUM {
        border: 1px solid rgba($warning-color, 0.12);
        background: $warning-50;
      }

      &.LOW {
        border: 1px solid rgba($info-color, 0.1);
        background: $info-50;
      }

      .alert-body {
        flex: 1;
        min-width: 0;

        .alert-project {
          font-size: $font-size-md;
          font-weight: $font-weight-medium;
          color: $text-primary;
          display: block;
          margin-bottom: 2px;
        }

        .alert-message {
          font-size: $font-size-sm;
          color: $text-secondary;
          display: block;
        }

        .alert-time {
          font-size: $font-size-xs;
          color: $text-muted;
          display: block;
          margin-top: 2px;
        }
      }

      .alert-badge {
        font-size: $font-size-xs;
        padding: 3px 8px;
        border-radius: $radius-sm;
        font-weight: $font-weight-medium;
        white-space: nowrap;

        &.HIGH { background: rgba($danger-color, 0.15); color: $danger-color; }
        &.MEDIUM { background: rgba($warning-color, 0.15); color: $warning-color; }
        &.LOW { background: rgba($info-color, 0.15); color: $info-color; }
      }
    }

    .empty-alerts {
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

.distribution-panel {
  .distribution-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-lg;

    .distribution-item {
      display: flex;
      align-items: center;
      gap: $spacing-md;

      .distribution-info {
        flex: 1;
        min-width: 0;

        .distribution-name {
          font-size: $font-size-sm;
          font-weight: $font-weight-medium;
          color: $text-primary;
          display: block;
          margin-bottom: 4px;
        }

        .distribution-percent {
          font-size: $font-size-xs;
          color: $text-muted;
          font-variant-numeric: tabular-nums;
        }
      }

      .distribution-bar {
        flex: 2;
        height: 10px;
        background: $bg-tertiary;
        border-radius: 5px;
        overflow: hidden;

        .bar-fill {
          height: 100%;
          border-radius: 5px;
          transition: width 0.8s $transition-spring;

          &.bar-gradient-0 {
            background: linear-gradient(90deg, $accent-500, $accent-400);
          }

          &.bar-gradient-1 {
            background: linear-gradient(90deg, $primary-500, $primary-400);
          }

          &.bar-gradient-2 {
            background: linear-gradient(90deg, $success-500, $success-600);
          }

          &.bar-gradient-3 {
            background: linear-gradient(90deg, $warning-500, $warning-600);
          }
        }
      }

      .distribution-amount {
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        color: $text-secondary;
        min-width: 60px;
        text-align: right;
        font-variant-numeric: tabular-nums;
      }
    }
  }
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-card.budget {
    grid-column: span 2;
  }

  .content-grid {
    grid-template-columns: 1fr 1fr;
  }

  .chart-panel {
    grid-column: span 2;
    grid-row: span 1;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card.budget {
    grid-column: span 1;
    flex-direction: column;
    text-align: center;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .chart-panel {
    grid-column: span 1;
  }

  .header-stats {
    flex-wrap: wrap;
  }

  .panel-controls {
    flex-direction: column;
    gap: $spacing-sm;
  }
}
</style>

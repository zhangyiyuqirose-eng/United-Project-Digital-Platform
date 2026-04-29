<template>
  <div class="dashboard">
    <!-- Welcome Banner -->
    <div class="welcome-banner">
      <div class="welcome-banner-bg">
        <div class="pattern-dots"></div>
        <div class="pattern-ring ring-1"></div>
        <div class="pattern-ring ring-2"></div>
        <div class="pattern-ring ring-3"></div>
        <div class="pattern-glow"></div>
      </div>
      <div class="welcome-banner-content">
        <div class="welcome-text">
          <h1 class="welcome-title">
            <span class="greeting">{{ greetingText }}</span>
            <span class="user-name">{{ userName }}</span>
          </h1>
          <p class="welcome-subtitle">今日待办事项 <strong>{{ pendingTasks }}</strong> 项，请及时处理</p>
        </div>
        <div class="welcome-actions">
          <button class="quick-btn primary" @click="navigateTo('/project/create')">
            <ElIcon><Plus /></ElIcon>
            <span>新建项目</span>
          </button>
          <button class="quick-btn" @click="navigateTo('/timesheet')">
            <ElIcon><Clock /></ElIcon>
            <span>填报工时</span>
          </button>
          <button class="quick-btn" @click="navigateTo('/workflow/tasks')">
            <ElIcon><Document /></ElIcon>
            <span>申请审批</span>
          </button>
        </div>
        <div class="welcome-date">
          <div class="date-card">
            <div class="date-day">{{ currentDay }}</div>
            <div class="date-month">{{ currentMonth }}</div>
            <div class="date-week">{{ currentWeek }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stat Cards Row -->
    <div class="stats-row">
      <StatCard
        :icon="Odometer"
        :value="stats.projects"
        label="进行中项目"
        color="primary"
        :trend="12"
        clickable
        @click="navigateTo('/project')"
      />
      <StatCard
        :icon="Document"
        :value="stats.approvals"
        label="待办审批"
        color="warning"
        :trend="-5"
        clickable
        @click="navigateTo('/workflow/tasks')"
      />
      <StatCard
        :icon="User"
        :value="stats.resources"
        label="外包人员"
        color="success"
        :trend="8"
        clickable
        @click="navigateTo('/resource')"
      />
      <StatCard
        :icon="Bell"
        :value="stats.alerts"
        label="预警事项"
        color="danger"
        :trend="3"
        clickable
        @click="navigateTo('/quality')"
      />
    </div>

    <!-- Bento Content Row -->
    <div class="bento-row">
      <!-- Project Overview (spans 2 cols) -->
      <div class="bento-card card-projects">
        <div class="card-header">
          <h3 class="card-title">项目概览</h3>
          <button class="card-action" @click="navigateTo('/project')">
            <ElIcon><ArrowRight /></ElIcon>
          </button>
        </div>
        <div class="card-body">
          <div class="project-list">
            <div
              class="project-item"
              v-for="project in recentProjects"
              :key="project.id"
              @click="navigateTo(`/project/${project.id}`)"
            >
              <div class="project-status" :class="project.statusClass">
                <span class="pulse-dot"></span>
              </div>
              <div class="project-info">
                <span class="project-name">{{ project.name }}</span>
                <span class="project-meta">{{ project.department }} · {{ project.manager }}</span>
              </div>
              <div class="project-progress">
                <div class="mini-progress">
                  <div class="mini-bar" :style="{ width: project.progress + '%', '--bar-color': statusColor(project.statusClass) }"></div>
                </div>
                <span class="progress-text">{{ project.progress }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Task List (spans 1 col) -->
      <div class="bento-card card-tasks">
        <div class="card-header">
          <h3 class="card-title">待办事项</h3>
          <div class="card-tabs">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'all' }"
              @click="activeTab = 'all'"
            >全部</button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'urgent' }"
              @click="activeTab = 'urgent'"
            >紧急</button>
          </div>
        </div>
        <div class="card-body">
          <div class="task-list">
            <div
              class="task-item"
              v-for="task in filteredTasks"
              :key="task.id"
              :class="{ urgent: task.urgent, completed: task.completed }"
            >
              <label class="task-checkbox">
                <input type="checkbox" v-model="task.completed">
                <span class="checkmark"></span>
              </label>
              <div class="task-content">
                <span class="task-title">{{ task.title }}</span>
                <span class="task-due">截止: {{ task.dueDate }}</span>
              </div>
              <span class="task-priority" :class="task.priorityClass">{{ task.priority }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Shortcuts (spans 1 col) -->
      <div class="bento-card card-shortcuts">
        <div class="card-header">
          <h3 class="card-title">快捷入口</h3>
        </div>
        <div class="card-body">
          <div class="shortcut-grid">
            <div class="shortcut-item" @click="navigateTo('/project')">
              <div class="shortcut-icon shortcut-projects">
                <ElIcon><Folder /></ElIcon>
              </div>
              <span class="shortcut-label">项目管理</span>
            </div>
            <div class="shortcut-item" @click="navigateTo('/timesheet')">
              <div class="shortcut-icon shortcut-timesheet">
                <ElIcon><Clock /></ElIcon>
              </div>
              <span class="shortcut-label">工时填报</span>
            </div>
            <div class="shortcut-item" @click="navigateTo('/cost')">
              <div class="shortcut-icon shortcut-cost">
                <ElIcon><Money /></ElIcon>
              </div>
              <span class="shortcut-label">成本管理</span>
            </div>
            <div class="shortcut-item" @click="navigateTo('/knowledge')">
              <div class="shortcut-icon shortcut-knowledge">
                <ElIcon><Reading /></ElIcon>
              </div>
              <span class="shortcut-label">知识库</span>
            </div>
            <div class="shortcut-item" @click="navigateTo('/workflow/tasks')">
              <div class="shortcut-icon shortcut-workflow">
                <ElIcon><CircleCheck /></ElIcon>
              </div>
              <span class="shortcut-label">审批流程</span>
            </div>
            <div class="shortcut-item" @click="navigateTo('/quality')">
              <div class="shortcut-icon shortcut-quality">
                <ElIcon><Briefcase /></ElIcon>
              </div>
              <span class="shortcut-label">质量管理</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Announcements Row (full width) -->
    <div class="bento-card card-announcements">
      <div class="card-header">
        <h3 class="card-title">通知公告</h3>
        <button class="card-action" @click="navigateTo('/system/announcements')">
          <ElIcon><ArrowRight /></ElIcon>
        </button>
      </div>
      <div class="card-body">
        <div class="notice-list">
          <div
            class="notice-item"
            v-for="notice in notices"
            :key="notice.id"
            :class="{ unread: notice.unread }"
            @click="navigateTo(`/system/announcements/${notice.id}`)"
          >
            <span class="notice-tag" :class="notice.type">{{ notice.typeLabel }}</span>
            <span class="notice-title">{{ notice.title }}</span>
            <span class="notice-date">{{ notice.date }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import StatCard from '@/components/StatCard.vue'
import {
  Odometer,
  Folder,
  Clock,
  User,
  Bell,
  Document,
  Money,
  Reading,
  CircleCheck,
  Briefcase,
  Plus,
  ArrowRight,
} from '@element-plus/icons-vue'

const router = useRouter()

// --- Welcome Banner ---
const userName = '管理员'
const pendingTasks = ref(8)

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早安'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 17) return '下午好'
  if (hour < 19) return '傍晚好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

const currentDay = computed(() => new Date().getDate().toString().padStart(2, '0'))
const currentMonth = computed(() => {
  const months = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
  return months[new Date().getMonth()]
})
const currentWeek = computed(() => {
  const weeks = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return weeks[new Date().getDay()]
})

// --- Stats ---
const stats = ref({
  projects: 12,
  approvals: 6,
  resources: 48,
  alerts: 3,
})

// --- Projects ---
const recentProjects = ref([
  { id: 1, name: '数字员工平台建设', department: '研发部', manager: '张三', progress: 75, statusClass: 'active' },
  { id: 2, name: '企业门户升级改造', department: '产品部', manager: '李四', progress: 45, statusClass: 'active' },
  { id: 3, name: '数据治理平台', department: '数据部', manager: '王五', progress: 30, statusClass: 'planning' },
  { id: 4, name: '移动端应用开发', department: '移动组', manager: '赵六', progress: 60, statusClass: 'delayed' },
])

function statusColor(statusClass: string): string {
  const colors: Record<string, string> = {
    active: '#16a34a',
    planning: '#d97706',
    delayed: '#dc2626',
  }
  return colors[statusClass] || '#3b82f6'
}

// --- Tasks ---
const activeTab = ref('all')
const tasks = ref([
  { id: 1, title: '审批项目立项申请', dueDate: '今天', priority: '高', priorityClass: 'high', urgent: true, completed: false },
  { id: 2, title: '审核本月工时填报', dueDate: '明天', priority: '中', priorityClass: 'medium', urgent: false, completed: false },
  { id: 3, title: '处理供应商合同', dueDate: '本周', priority: '低', priorityClass: 'low', urgent: false, completed: false },
  { id: 4, title: '完成项目预算审核', dueDate: '今天', priority: '高', priorityClass: 'high', urgent: true, completed: false },
])

const filteredTasks = computed(() => {
  if (activeTab.value === 'urgent') {
    return tasks.value.filter(t => t.urgent)
  }
  return tasks.value
})

// --- Notices ---
const notices = ref([
  { id: 1, title: '关于调整项目管理流程的通知', date: '2026-04-25', type: 'important', typeLabel: '重要', unread: true },
  { id: 2, title: '系统升级维护公告', date: '2026-04-24', type: 'system', typeLabel: '系统', unread: true },
  { id: 3, title: '本周项目例会安排', date: '2026-04-23', type: 'normal', typeLabel: '通知', unread: false },
  { id: 4, title: 'Q2 外包资源池扩容计划', date: '2026-04-22', type: 'important', typeLabel: '重要', unread: false },
])

// --- Navigation ---
function navigateTo(path: string) {
  router.push(path)
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.dashboard {
  max-width: 1400px;
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
  animation: fadeInUp 0.5s ease-out;
}

/* ── Welcome Banner ─────────────────────────────────── */

.welcome-banner {
  @include card-base;
  background: $accent-gradient;
  color: white;
  padding: $spacing-2xl $spacing-3xl;
  position: relative;
  overflow: hidden;
  border: none;

  &:hover {
    box-shadow: $shadow-hover;
    transform: none;
  }

  .welcome-banner-bg {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;

    .pattern-dots {
      position: absolute;
      inset: 0;
      background-image: radial-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px);
      background-size: 24px 24px;
      animation: drift 20s linear infinite;
    }

    .pattern-ring {
      position: absolute;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 50%;
      animation: pulse-ring 6s ease-out infinite;
    }

    .ring-1 {
      width: 300px;
      height: 300px;
      right: 10%;
      top: -20%;
      animation-delay: 0s;
    }

    .ring-2 {
      width: 200px;
      height: 200px;
      right: 25%;
      top: 10%;
      animation-delay: 2s;
    }

    .ring-3 {
      width: 150px;
      height: 150px;
      left: 5%;
      bottom: -10%;
      animation-delay: 4s;
    }

    .pattern-glow {
      position: absolute;
      width: 400px;
      height: 400px;
      right: -10%;
      bottom: -30%;
      background: radial-gradient(circle, rgba(255, 255, 255, 0.15), transparent 70%);
      animation: glow-pulse 8s ease-in-out infinite;
    }
  }

  .welcome-banner-content {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $spacing-xl;
  }

  .welcome-text {
    flex: 1;

    .welcome-title {
      font-size: $font-size-3xl;
      font-weight: $font-weight-bold;
      margin-bottom: $spacing-sm;
      line-height: 1.3;

      .greeting {
        opacity: 0.9;
        margin-right: $spacing-sm;
      }

      .user-name {
        color: white;
      }
    }

    .welcome-subtitle {
      font-size: $font-size-md;
      opacity: 0.85;

      strong {
        color: white;
        opacity: 1;
      }
    }
  }

  .welcome-actions {
    display: flex;
    gap: $spacing-md;

    .quick-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 20px;
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.25);
      border-radius: $radius-lg;
      color: white;
      font-size: $font-size-sm;
      font-weight: $font-weight-medium;
      cursor: pointer;
      transition: all $transition-normal;
      backdrop-filter: blur(8px);

      .el-icon {
        font-size: 18px;
      }

      &:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.4);
      }

      &.primary {
        background: white;
        color: $accent-600;
        border-color: transparent;
        font-weight: $font-weight-semibold;

        &:hover {
          background: rgba(255, 255, 255, 0.95);
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }
      }
    }
  }

  .welcome-date {
    flex-shrink: 0;

    .date-card {
      background: rgba(255, 255, 255, 0.15);
      border-radius: $radius-xl;
      padding: $spacing-lg $spacing-xl;
      text-align: center;
      min-width: 100px;
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.2);

      .date-day {
        font-size: 36px;
        font-weight: $font-weight-bold;
        line-height: 1;
      }

      .date-month {
        font-size: $font-size-md;
        opacity: 0.9;
        margin-top: 4px;
      }

      .date-week {
        font-size: $font-size-sm;
        opacity: 0.75;
        margin-top: 8px;
      }
    }
  }
}

@keyframes drift {
  from { background-position: 0 0; }
  to { background-position: 24px 24px; }
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

/* ── Stats Row ──────────────────────────────────────── */

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $spacing-lg;
}

/* ── Bento Row (Projects + Tasks + Shortcuts) ───────── */

.bento-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: $spacing-lg;
}

/* ── Bento Card (shared panel style) ────────────────── */

.bento-card {
  @include card-base;
  padding: $spacing-lg;
  display: flex;
  flex-direction: column;

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $spacing-md;
    padding-bottom: $spacing-md;
    border-bottom: 1px solid $divider-color;

    .card-title {
      font-size: $font-size-lg;
      font-weight: $font-weight-semibold;
      color: $text-primary;
      margin: 0;
    }

    .card-action {
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
      transition: all $transition-normal;

      &:hover {
        background: $bg-secondary;
        color: $accent-color;
      }
    }

    .card-tabs {
      display: flex;
      gap: $spacing-sm;

      .tab-btn {
        padding: 6px 14px;
        border-radius: $radius-sm;
        background: transparent;
        border: none;
        font-size: $font-size-sm;
        color: $text-muted;
        cursor: pointer;
        transition: all $transition-normal;
        font-weight: $font-weight-medium;

        &.active {
          background: $accent-color;
          color: white;
        }

        &:hover:not(.active) {
          background: $bg-secondary;
          color: $text-secondary;
        }
      }
    }
  }

  .card-body {
    flex: 1;
  }
}

/* ── Project Card ───────────────────────────────────── */

.card-projects {
  .project-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;

    .project-item {
      display: flex;
      align-items: center;
      gap: $spacing-md;
      padding: $spacing-md;
      border-radius: $radius-lg;
      background: $bg-secondary;
      transition: all $transition-normal;
      cursor: pointer;

      &:hover {
        background: $bg-tertiary;
        transform: translateX(4px);
      }

      .project-status {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        position: relative;
        flex-shrink: 0;

        .pulse-dot {
          position: absolute;
          inset: 0;
          border-radius: 50%;
          animation: pulse-ring 2s ease-out infinite;
        }

        &.active {
          background: $success-color;

          .pulse-dot {
            background: rgba($success-color, 0.3);
          }
        }

        &.planning {
          background: $warning-color;

          .pulse-dot {
            background: rgba($warning-color, 0.3);
          }
        }

        &.delayed {
          background: $danger-color;

          .pulse-dot {
            background: rgba($danger-color, 0.3);
          }
        }
      }

      .project-info {
        flex: 1;
        min-width: 0;

        .project-name {
          font-size: $font-size-md;
          font-weight: $font-weight-medium;
          color: $text-primary;
          display: block;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .project-meta {
          font-size: $font-size-sm;
          color: $text-muted;
          margin-top: 2px;
        }
      }

      .project-progress {
        display: flex;
        align-items: center;
        gap: $spacing-sm;
        flex-shrink: 0;

        .mini-progress {
          width: 80px;
          height: 6px;
          background: $divider-color;
          border-radius: 3px;
          overflow: hidden;

          .mini-bar {
            height: 100%;
            background: var(--bar-color, $accent-color);
            border-radius: 3px;
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
          }
        }

        .progress-text {
          font-size: $font-size-sm;
          font-weight: $font-weight-medium;
          color: $text-secondary;
          min-width: 36px;
          text-align: right;
        }
      }
    }
  }
}

/* ── Task Card ──────────────────────────────────────── */

.card-tasks {
  .task-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;

    .task-item {
      display: flex;
      align-items: center;
      gap: $spacing-md;
      padding: $spacing-md;
      border-radius: $radius-lg;
      background: $bg-secondary;
      transition: all $transition-normal;

      &:hover {
        background: $bg-tertiary;
      }

      &.urgent {
        border-left: 3px solid $danger-color;
      }

      &.completed {
        .task-title {
          text-decoration: line-through;
          color: $text-muted;
          opacity: 0.6;
        }

        .task-due {
          text-decoration: line-through;
          opacity: 0.4;
        }

        .task-priority {
          opacity: 0.4;
        }
      }

      .task-checkbox {
        position: relative;
        display: flex;
        align-items: center;
        flex-shrink: 0;

        input {
          position: absolute;
          opacity: 0;
          width: 0;
          height: 0;
        }

        .checkmark {
          width: 20px;
          height: 20px;
          border: 2px solid $slate-300;
          border-radius: $radius-sm;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all $transition-normal;
          cursor: pointer;

          &::after {
            content: '';
            width: 5px;
            height: 10px;
            border: solid white;
            border-width: 0 2px 2px 0;
            transform: rotate(45deg) scale(0);
            transition: transform $transition-bounce;
          }
        }

        input:checked + .checkmark {
          background: $accent-color;
          border-color: $accent-color;

          &::after {
            transform: rotate(45deg) scale(1);
          }
        }
      }

      .task-content {
        flex: 1;
        min-width: 0;

        .task-title {
          font-size: $font-size-md;
          color: $text-primary;
          display: block;
          transition: all $transition-normal;
        }

        .task-due {
          font-size: $font-size-sm;
          color: $text-muted;
          margin-top: 2px;
        }
      }

      .task-priority {
        font-size: $font-size-xs;
        padding: 4px 8px;
        border-radius: $radius-sm;
        font-weight: $font-weight-medium;
        flex-shrink: 0;

        &.high {
          background: rgba($danger-color, 0.12);
          color: $danger-color;
        }

        &.medium {
          background: rgba($warning-color, 0.12);
          color: $warning-color;
        }

        &.low {
          background: rgba($success-color, 0.12);
          color: $success-color;
        }
      }
    }
  }
}

/* ── Shortcuts Card ─────────────────────────────────── */

.card-shortcuts {
  .shortcut-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: $spacing-md;

    .shortcut-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: $spacing-sm;
      padding: $spacing-md;
      border-radius: $radius-lg;
      background: $bg-secondary;
      cursor: pointer;
      transition: all $transition-normal;

      &:hover {
        background: white;
        transform: translateY(-4px);
        box-shadow: $shadow-md;
      }

      .shortcut-icon {
        width: 44px;
        height: 44px;
        border-radius: $radius-lg;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all $transition-normal;

        .el-icon {
          font-size: 20px;
        }

        &.shortcut-projects {
          background: rgba($accent-color, 0.1);
          color: $accent-color;
        }

        &.shortcut-timesheet {
          background: rgba($success-color, 0.1);
          color: $success-color;
        }

        &.shortcut-cost {
          background: rgba($warning-color, 0.1);
          color: $warning-color;
        }

        &.shortcut-knowledge {
          background: rgba(#805ad5, 0.1);
          color: #805ad5;
        }

        &.shortcut-workflow {
          background: rgba($danger-color, 0.1);
          color: $danger-color;
        }

        &.shortcut-quality {
          background: rgba(#319795, 0.1);
          color: #319795;
        }
      }

      .shortcut-label {
        font-size: $font-size-sm;
        color: $text-secondary;
        font-weight: $font-weight-medium;
        text-align: center;
      }
    }
  }
}

/* ── Announcements Card ─────────────────────────────── */

.card-announcements {
  .notice-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;

    .notice-item {
      display: flex;
      align-items: center;
      gap: $spacing-md;
      padding: $spacing-md $spacing-lg;
      border-radius: $radius-lg;
      background: $bg-secondary;
      transition: all $transition-normal;
      cursor: pointer;

      &:hover {
        background: $bg-tertiary;
        transform: translateX(4px);
      }

      &.unread {
        background: white;
        border: 1px solid $border-color;
        position: relative;

        &::before {
          content: '';
          position: absolute;
          left: 8px;
          top: 50%;
          transform: translateY(-50%);
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: $accent-color;
        }
      }

      .notice-tag {
        font-size: $font-size-xs;
        padding: 4px 10px;
        border-radius: $radius-sm;
        font-weight: $font-weight-semibold;
        flex-shrink: 0;

        &.important {
          background: rgba($danger-color, 0.12);
          color: $danger-color;
        }

        &.system {
          background: rgba($accent-color, 0.12);
          color: $accent-color;
        }

        &.normal {
          background: $bg-tertiary;
          color: $text-muted;
        }
      }

      .notice-title {
        flex: 1;
        font-size: $font-size-md;
        color: $text-primary;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .notice-date {
        font-size: $font-size-sm;
        color: $text-muted;
        flex-shrink: 0;
      }
    }
  }
}

/* ── Responsive ─────────────────────────────────────── */

@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .bento-row {
    grid-template-columns: 1fr 1fr;

    .card-projects {
      grid-column: span 2;
    }

    .card-tasks {
      grid-column: span 1;
    }

    .card-shortcuts {
      grid-column: span 1;
    }
  }
}

@media (max-width: 1024px) {
  .bento-row {
    grid-template-columns: 1fr;

    .card-projects,
    .card-tasks,
    .card-shortcuts {
      grid-column: span 1;
    }
  }

  .welcome-banner {
    .welcome-actions {
      display: none;
    }
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }

  .welcome-banner {
    padding: $spacing-xl;

    .welcome-date {
      display: none;
    }

    .welcome-title {
      font-size: $font-size-2xl;
    }
  }

  .card-shortcuts .shortcut-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .card-announcements .notice-item {
    flex-wrap: wrap;

    .notice-date {
      width: 100%;
      margin-left: $spacing-lg;
    }
  }
}
</style>

<template>
  <div class="gantt-chart">
    <div class="gantt-header">
      <div class="gantt-task-name">任务名称</div>
      <div class="gantt-timeline">
        <div v-for="m in months" :key="m" class="gantt-month">{{ m }}</div>
      </div>
    </div>
    <div v-for="task in tasks" :key="task.taskId" class="gantt-row" :class="{ 'is-parent': !task.parentId }">
      <div class="gantt-task-name" :style="{ paddingLeft: (task.parentId ? '24px' : '8px') }">
        {{ task.taskName }}
      </div>
      <div class="gantt-timeline">
        <div class="gantt-bar-container">
          <div
            class="gantt-bar"
            :style="getBarStyle(task)"
            :title="`${task.taskName}: ${task.progress}%`"
          >
            <span class="gantt-bar-text" v-if="getBarWidth(task) > 40">{{ task.progress }}%</span>
          </div>
        </div>
      </div>
    </div>
    <div v-if="!tasks.length" class="gantt-empty">暂无数据</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GanttTaskVO } from '@/api/modules/project'

const props = defineProps<{
  tasks: GanttTaskVO[]
}>()

const months = computed(() => {
  if (!props.tasks.length) return []
  const dates = props.tasks.flatMap((t) => [new Date(t.startDate), new Date(t.endDate)])
  const minDate = new Date(Math.min(...dates.map((d) => d.getTime())))
  const maxDate = new Date(Math.max(...dates.map((d) => d.getTime())))
  const result: string[] = []
  const current = new Date(minDate.getFullYear(), minDate.getMonth(), 1)
  while (current <= maxDate) {
    result.push(`${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2, '0')}`)
    current.setMonth(current.getMonth() + 1)
  }
  return result
})

const timelineStart = computed(() => {
  if (!months.value.length) return new Date()
  const [y, m] = months.value[0].split('-').map(Number)
  return new Date(y, m - 1, 1)
})

const totalDays = computed(() => {
  if (!months.value.length) return 30
  const start = timelineStart.value
  const lastMonth = months.value[months.value.length - 1].split('-').map(Number)
  const end = new Date(lastMonth[0], lastMonth[1], 0)
  return Math.max(1, Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)))
})

function getBarStyle(task: GanttTaskVO) {
  const start = new Date(task.startDate).getTime()
  const end = new Date(task.endDate).getTime()
  const tStart = timelineStart.value.getTime()
  const dayMs = 1000 * 60 * 60 * 24
  const offsetDays = Math.max(0, (start - tStart) / dayMs)
  const durationDays = Math.max(1, (end - start) / dayMs)
  const left = (offsetDays / totalDays.value) * 100
  const width = (durationDays / totalDays.value) * 100
  return { left: `${left}%`, width: `${width}%` }
}

function getBarWidth(task: GanttTaskVO) {
  const start = new Date(task.startDate).getTime()
  const end = new Date(task.endDate).getTime()
  return Math.max(1, (end - start) / (1000 * 60 * 60 * 24))
}
</script>

<style scoped lang="scss">
.gantt-chart {
  background: #fff;
  border-radius: 4px;
  overflow-x: auto;
  min-width: 600px;
}
.gantt-header {
  display: flex;
  border-bottom: 2px solid #ebeef5;
  background: #f5f7fa;
  font-weight: 600;
  position: sticky;
  top: 0;
}
.gantt-task-name {
  width: 200px;
  min-width: 200px;
  padding: 8px;
  border-right: 1px solid #ebeef5;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gantt-timeline {
  flex: 1;
  display: flex;
  position: relative;
}
.gantt-month {
  flex: 1;
  min-width: 80px;
  text-align: center;
  padding: 8px 4px;
  font-size: 12px;
  color: #909399;
}
.gantt-row {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  &:hover { background: #fafafa; }
}
.gantt-row.is-parent {
  font-weight: 600;
  background: #fafafa;
}
.gantt-bar-container {
  flex: 1;
  position: relative;
  height: 32px;
}
.gantt-bar {
  position: absolute;
  height: 20px;
  top: 6px;
  background: #409eff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 11px;
  min-width: 2px;
}
.gantt-bar-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gantt-empty {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>

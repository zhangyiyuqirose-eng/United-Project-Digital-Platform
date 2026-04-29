<template>
  <el-tag :type="tagType" :effect="effect" size="small" round>
    {{ label }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  status: string
  effect?: 'dark' | 'light' | 'plain'
}>(), {
  effect: 'light',
})

const statusMap: Record<string, { label: string; type: string }> = {
  DRAFT: { label: '草稿', type: 'info' },
  PENDING: { label: '待审批', type: 'warning' },
  APPROVED: { label: '已通过', type: 'success' },
  REJECTED: { label: '已驳回', type: 'danger' },
  IN_PROGRESS: { label: '进行中', type: '' },
  COMPLETED: { label: '已完成', type: 'success' },
  CANCELLED: { label: '已取消', type: 'info' },
  ON_HOLD: { label: '已暂停', type: 'warning' },
  AVAILABLE: { label: '空闲', type: 'success' },
  ON_LEAVE: { label: '请假中', type: 'warning' },
  BENCHED: { label: '待分配', type: 'info' },
  ASSIGNED: { label: '已分配', type: '' },
  HIGH: { label: '高', type: 'danger' },
  MEDIUM: { label: '中', type: 'warning' },
  LOW: { label: '低', type: 'success' },
  OPEN: { label: '未解决', type: 'danger' },
  FIXED: { label: '已修复', type: 'success' },
  CLOSED: { label: '已关闭', type: 'info' },
  CRITICAL: { label: '严重', type: 'danger' },
  WARNING: { label: '警告', type: 'warning' },
  INFO: { label: '信息', type: 'info' },
  SALES: { label: '销售合同', type: '' },
  PROCUREMENT: { label: '采购合同', type: 'warning' },
  FRAMEWORK: { label: '框架协议', type: 'info' },
  UNPAID: { label: '未支付', type: 'warning' },
  PARTIAL: { label: '部分支付', type: '' },
  PAID: { label: '已支付', type: 'success' },
  OVERDUE: { label: '已逾期', type: 'danger' },
  PRE_INIT: { label: '立项前', type: 'info' },
  INITIATED: { label: '已立项', type: '' },
}

const tagType = computed(() => statusMap[props.status]?.type || 'info')
const label = computed(() => statusMap[props.status]?.label || props.status)
</script>

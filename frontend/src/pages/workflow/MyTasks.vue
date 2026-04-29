<template>
  <div class="my-tasks-page">
    <PageHeader title="我的待办" description="处理待审批的 workflow 任务" />

    <el-card>
      <template #header><span>我的待办</span></template>
      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="processName" label="流程名称" min-width="160" />
        <el-table-column prop="taskName" label="任务名称" width="140" />
        <el-table-column prop="assignee" label="当前处理人" width="120" />
        <el-table-column prop="businessKey" label="业务编号" width="140" />
        <el-table-column prop="createTime" label="到达时间" width="160" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><StatusTag :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" @click="handleApprove(row)">通过</el-button>
            <el-button link type="danger" @click="handleReject(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      <Pagination :total="total" :page="page" :limit="limit" @change="handlePageChange" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyTasks, approveTask, rejectTask } from '@/api/modules/workflow'
import PageHeader from '@/components/PageHeader.vue'
import Pagination from '@/components/Pagination.vue'
import StatusTag from '@/components/StatusTag.vue'

const loading = ref(false)
const tableData = ref<unknown[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)

async function fetchData() {
  loading.value = true
  try {
    const res = await getMyTasks({ page: page.value, limit: limit.value })
    tableData.value = res.records; total.value = res.total
  } finally { loading.value = false }
}

function handlePageChange(v: { page: number; limit: number }) { page.value = v.page; limit.value = v.limit; fetchData() }

async function handleApprove(row: Record<string, unknown>) {
  try { await approveTask(row.taskId as string, '同意'); ElMessage.success('已通过'); fetchData() } catch { /* handled */ }
}

async function handleReject(row: Record<string, unknown>) {
  try { await rejectTask(row.taskId as string, '驳回'); ElMessage.success('已驳回'); fetchData() } catch { /* handled */ }
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.my-tasks-page {
  max-width: 1400px;
}
</style>

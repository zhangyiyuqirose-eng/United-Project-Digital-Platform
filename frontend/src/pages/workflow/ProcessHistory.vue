<template>
  <div class="process-history-page">
    <PageHeader title="流程历史" description="查询工作流流程实例的历史记录" />

    <el-card>
      <template #header>
        <div class="card-header">
          <span>流程查询</span>
          <el-input v-model="instanceId" placeholder="输入流程实例ID" style="width: 300px" @keyup.enter="handleQuery" />
          <el-button type="primary" @click="handleQuery">查询</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="processName" label="流程名称" min-width="160" />
        <el-table-column prop="activityName" label="活动名称" width="140" />
        <el-table-column prop="assignee" label="处理人" width="120" />
        <el-table-column prop="action" label="操作" width="100">
          <template #default="{ row }"><StatusTag :status="row.action" /></template>
        </el-table-column>
        <el-table-column prop="comment" label="意见" min-width="200" show-overflow-tooltip />
        <el-table-column prop="createTime" label="时间" width="160" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getProcessHistory } from '@/api/modules/workflow'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'

const route = useRoute()
const instanceId = ref(route.query.id as string || '')
const loading = ref(false)
const tableData = ref<unknown[]>([])

async function handleQuery() {
  if (!instanceId.value) return
  loading.value = true
  try { tableData.value = await getProcessHistory(instanceId.value) } catch { tableData.value = [] } finally { loading.value = false }
}

onMounted(handleQuery)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.process-history-page {
  max-width: 1400px;
}

.card-header { display: flex; gap: 12px; align-items: center; }
</style>

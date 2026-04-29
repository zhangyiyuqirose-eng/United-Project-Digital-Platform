<template>
  <div class="quality-management-page">
    <PageHeader title="质量管理" description="缺陷跟踪与质量指标监控">
      <el-button v-if="activeTab === 'defects'" class="create-btn" @click="showDialog = true"><el-icon><Plus /></el-icon> 提交缺陷</el-button>
    </PageHeader>

    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="缺陷管理" name="defects">
        <SearchForm :model="searchForm" @search="handleSearch" @reset="handleReset">
          <el-form-item label="项目"><el-input v-model="searchForm.projectId" placeholder="项目ID" clearable /></el-form-item>
          <el-form-item label="严重程度">
            <el-select v-model="searchForm.severity" placeholder="全部" clearable>
              <el-option label="严重" value="CRITICAL" /><el-option label="高" value="HIGH" /><el-option label="中" value="MEDIUM" /><el-option label="低" value="LOW" />
            </el-select>
          </el-form-item>
        </SearchForm>
        <el-card>
          <template #header><div class="card-header"><span>缺陷列表</span></div></template>
          <el-table v-loading="loading" :data="tableData" stripe>
            <el-table-column prop="title" label="标题" min-width="180" />
            <el-table-column prop="projectName" label="项目" width="140" />
            <el-table-column prop="severity" label="严重程度" width="90"><template #default="{ row }"><StatusTag :status="row.severity" /></template></el-table-column>
            <el-table-column prop="priority" label="优先级" width="90"><template #default="{ row }"><StatusTag :status="row.priority" /></template></el-table-column>
            <el-table-column prop="status" label="状态" width="90"><template #default="{ row }"><StatusTag :status="row.status" /></template></el-table-column>
            <el-table-column prop="assignee" label="指派给" width="100" />
            <el-table-column prop="reporter" label="报告人" width="100" />
            <el-table-column prop="createTime" label="创建时间" width="160" />
            <el-table-column label="操作" width="100"><template #default="{ row }"><el-button link type="success" v-if="row.status === 'OPEN'" @click="handleResolve(row)">解决</el-button></template></el-table-column>
          </el-table>
          <Pagination :total="total" :page="page" :limit="limit" @change="handlePageChange" />
        </el-card>
        <el-dialog v-model="showDialog" title="提交缺陷" width="500px">
          <el-form :model="defectForm" label-width="80px">
            <el-form-item label="项目"><el-input v-model="defectForm.projectId" /></el-form-item>
            <el-form-item label="标题"><el-input v-model="defectForm.title" /></el-form-item>
            <el-form-item label="严重程度"><el-select v-model="defectForm.severity"><el-option label="严重" value="CRITICAL" /><el-option label="高" value="HIGH" /><el-option label="中" value="MEDIUM" /><el-option label="低" value="LOW" /></el-select></el-form-item>
            <el-form-item label="优先级"><el-select v-model="defectForm.priority"><el-option label="高" value="HIGH" /><el-option label="中" value="MEDIUM" /><el-option label="低" value="LOW" /></el-select></el-form-item>
            <el-form-item label="指派给"><el-input v-model="defectForm.assignee" /></el-form-item>
            <el-form-item label="描述"><el-input v-model="defectForm.description" type="textarea" :rows="4" /></el-form-item>
          </el-form>
          <template #footer><el-button @click="showDialog = false">取消</el-button><el-button type="primary" @click="handleSubmitDefect">提交</el-button></template>
        </el-dialog>
      </el-tab-pane>
      <el-tab-pane label="质量指标" name="metrics">
        <el-card><template #header><span>质量指标</span></template>
          <el-table :data="metricsData" stripe>
            <el-table-column prop="projectName" label="项目" min-width="140" />
            <el-table-column prop="metricName" label="指标" width="140" />
            <el-table-column prop="target" label="目标" width="100" />
            <el-table-column prop="actual" label="实际" width="100" />
            <el-table-column prop="status" label="状态" width="100"><template #default="{ row }"><StatusTag :status="row.status" /></template></el-table-column>
            <el-table-column prop="period" label="周期" width="120" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getDefectList, createDefect, resolveDefect, getQualityMetrics } from '@/api/modules/quality'
import PageHeader from '@/components/PageHeader.vue'
import SearchForm from '@/components/SearchForm.vue'
import Pagination from '@/components/Pagination.vue'
import StatusTag from '@/components/StatusTag.vue'

const activeTab = ref('defects')
const loading = ref(false)
const tableData = ref<unknown[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const showDialog = ref(false)
const searchForm = reactive({ projectId: '', severity: '' })
const defectForm = reactive({ projectId: '', title: '', severity: 'MEDIUM', priority: 'MEDIUM', assignee: '', description: '' })
const metricsData = ref<unknown[]>([])

async function fetchData() {
  loading.value = true
  try {
    const res = await getDefectList({ page: page.value, limit: limit.value, ...searchForm })
    tableData.value = res.records; total.value = res.total
  } finally { loading.value = false }
}

async function loadMetrics() {
  try { metricsData.value = await getQualityMetrics({}) } catch { metricsData.value = [] }
}

function handleSearch() { page.value = 1; fetchData() }
function handleReset() { searchForm.projectId = ''; searchForm.severity = ''; page.value = 1; fetchData() }
function handlePageChange(v: { page: number; limit: number }) { page.value = v.page; limit.value = v.limit; fetchData() }

async function handleSubmitDefect() {
  try { await createDefect(defectForm); ElMessage.success('提交成功'); showDialog.value = false; fetchData() } catch { /* handled */ }
}

async function handleResolve(row: Record<string, unknown>) {
  try { await resolveDefect(row.defectId as string); ElMessage.success('已解决'); fetchData() } catch { /* handled */ }
}

onMounted(() => { fetchData(); loadMetrics() })
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.quality-management-page {
  max-width: 1400px;
}

.card-header { display: flex; justify-content: space-between; align-items: center; }

.create-btn {
  @include button-primary;
}
</style>

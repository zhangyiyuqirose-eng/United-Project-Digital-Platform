<template>
  <div class="performance-eval-page">
    <PageHeader title="绩效评估" description="管理团队成员的绩效考核与评估记录" />

    <SearchForm :model="searchForm" @search="handleSearch" @reset="handleReset">
      <el-form-item label="项目">
        <el-input v-model="searchForm.projectId" placeholder="项目ID" clearable />
      </el-form-item>
    </SearchForm>

    <el-card class="eval-card">
      <template #header>
        <div class="card-header">
          <span>绩效评估</span>
          <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon> 新增评估</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="resourceName" label="姓名" width="100" />
        <el-table-column prop="projectName" label="项目" min-width="140" />
        <el-table-column prop="quality" label="质量" width="80" />
        <el-table-column prop="efficiency" label="效率" width="80" />
        <el-table-column prop="communication" label="沟通" width="80" />
        <el-table-column prop="overall" label="综合得分" width="100">
          <template #default="{ row }">
            <el-tag :type="row.overall >= 90 ? 'success' : row.overall >= 70 ? '' : 'warning'">{{ row.overall }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="evaluator" label="评估人" width="100" />
        <el-table-column prop="evalDate" label="评估日期" width="110" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <Pagination :total="total" :page="page" :limit="limit" @change="handlePageChange" />
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑评估' : '新增评估'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="资源"><el-input v-model="form.resourceId" /></el-form-item>
        <el-form-item label="项目"><el-input v-model="form.projectId" /></el-form-item>
        <el-form-item label="质量"><el-input-number v-model="form.quality" :min="0" :max="100" style="width: 100%" /></el-form-item>
        <el-form-item label="效率"><el-input-number v-model="form.efficiency" :min="0" :max="100" style="width: 100%" /></el-form-item>
        <el-form-item label="沟通"><el-input-number v-model="form.communication" :min="0" :max="100" style="width: 100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showDialog = false">取消</el-button><el-button type="primary" @click="handleSubmit">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getPerformanceEvalList, createPerformanceEval, updatePerformanceEval } from '@/api/modules/resource'
import SearchForm from '@/components/SearchForm.vue'
import Pagination from '@/components/Pagination.vue'

const loading = ref(false)
const tableData = ref<unknown[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const showDialog = ref(false)
const editingId = ref('')
const searchForm = reactive({ projectId: '' })

const form = reactive({ resourceId: '', projectId: '', quality: 0, efficiency: 0, communication: 0, overall: 0 })

async function fetchData() {
  loading.value = true
  try {
    const res = await getPerformanceEvalList({ page: page.value, limit: limit.value, ...searchForm })
    tableData.value = res.records; total.value = res.total
  } finally { loading.value = false }
}

function handleSearch() { page.value = 1; fetchData() }
function handleReset() { searchForm.projectId = ''; page.value = 1; fetchData() }
function handlePageChange(v: { page: number; limit: number }) { page.value = v.page; limit.value = v.limit; fetchData() }

function handleEdit(row: Record<string, unknown>) {
  editingId.value = row.evalId as string
  Object.assign(form, { resourceId: row.resourceId, projectId: row.projectId, quality: row.quality, efficiency: row.efficiency, communication: row.communication })
  showDialog.value = true
}

async function handleSubmit() {
  form.overall = Math.round((form.quality + form.efficiency + form.communication) / 3)
  try {
    if (editingId.value) { await updatePerformanceEval(editingId.value, form) } else { await createPerformanceEval(form) }
    ElMessage.success('保存成功'); showDialog.value = false; fetchData()
  } catch { /* handled */ }
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.performance-eval-page {
  max-width: 1400px;
}

.performance-eval-page > :deep(.search-form) {
  margin-bottom: $spacing-xl;
}

.eval-card {
  @include card-base;

  :deep(.el-card__header) {
    border-bottom: 1px solid $divider-color;
    padding: $spacing-lg $spacing-xl;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    span {
      font-size: $font-size-lg;
      font-weight: $font-weight-semibold;
      color: $text-primary;
    }

    .el-button {
      @include button-primary;
    }
  }
}
</style>

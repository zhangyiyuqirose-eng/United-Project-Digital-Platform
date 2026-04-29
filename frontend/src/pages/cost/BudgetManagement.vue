<template>
  <div class="page-container">
    <PageHeader title="预算管理" description="管理项目预算、跟踪实际支出与承诺金额">
      <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon> 新增预算</el-button>
    </PageHeader>
    <SearchForm :model="searchForm" @search="handleSearch" @reset="handleReset">
      <el-form-item label="项目">
        <el-input v-model="searchForm.projectId" placeholder="项目ID" clearable />
      </el-form-item>
      <el-form-item label="年度">
        <el-input-number v-model="searchForm.year" :min="2020" :max="2030" placeholder="年度" />
      </el-form-item>
    </SearchForm>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">预算列表</span>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="projectName" label="项目名称" min-width="160" />
        <el-table-column prop="category" label="预算类别" width="120" />
        <el-table-column prop="plannedAmount" label="计划金额" width="120">
          <template #default="{ row }">¥{{ row.plannedAmount?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="actualAmount" label="实际支出" width="120">
          <template #default="{ row }">¥{{ row.actualAmount?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="committedAmount" label="已承诺" width="120">
          <template #default="{ row }">¥{{ row.committedAmount?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="year" label="年度" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><StatusTag :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.budgetId)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <Pagination :total="total" :page="page" :limit="limit" @change="handlePageChange" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑预算' : '新增预算'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="项目"><el-input v-model="form.projectId" /></el-form-item>
        <el-form-item label="类别">
          <el-select v-model="form.category"><el-option label="人工" value="LABOR" /><el-option label="设备" value="EQUIPMENT" /><el-option label="差旅" value="TRAVEL" /><el-option label="其他" value="OTHER" /></el-select>
        </el-form-item>
        <el-form-item label="计划金额"><el-input-number v-model="form.plannedAmount" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="年度"><el-input-number v-model="form.year" :min="2020" :max="2030" style="width: 100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="handleSubmit">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getBudgetList, createBudget, updateBudget, deleteBudget } from '@/api/modules/cost'
import PageHeader from '@/components/PageHeader.vue'
import SearchForm from '@/components/SearchForm.vue'
import Pagination from '@/components/Pagination.vue'
import StatusTag from '@/components/StatusTag.vue'

const loading = ref(false)
const tableData = ref<unknown[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const dialogVisible = ref(false)
const editingId = ref('')

const searchForm = reactive({ projectId: '', year: undefined as number | undefined })
const form = reactive({ projectId: '', category: '', plannedAmount: 0, year: 2026 })

async function fetchData() {
  loading.value = true
  try {
    const res = await getBudgetList({ page: page.value, limit: limit.value, projectId: searchForm.projectId, year: searchForm.year })
    tableData.value = res.records
    total.value = res.total
  } finally { loading.value = false }
}

function handleSearch() { page.value = 1; fetchData() }
function handleReset() { searchForm.projectId = ''; searchForm.year = undefined; page.value = 1; fetchData() }
function handlePageChange(v: { page: number; limit: number }) { page.value = v.page; limit.value = v.limit; fetchData() }

function handleAdd() { editingId.value = ''; Object.assign(form, { projectId: '', category: '', plannedAmount: 0, year: 2026 }); dialogVisible.value = true }
function handleEdit(row: Record<string, unknown>) { editingId.value = row.budgetId as string; Object.assign(form, { projectId: row.projectId, category: row.category, plannedAmount: row.plannedAmount, year: row.year }); dialogVisible.value = true }

async function handleDelete(id: string) {
  try { await deleteBudget(id); ElMessage.success('删除成功'); fetchData() } catch { /* handled */ }
}

async function handleSubmit() {
  try {
    if (editingId.value) { await updateBudget(editingId.value, form) } else { await createBudget(form) }
    ElMessage.success('保存成功'); dialogVisible.value = false; fetchData()
  } catch { /* handled */ }
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.page-container {
  padding: $spacing-2xl;
  max-width: 1400px;
}

.table-card {
  @include card-base;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  color: $text-primary;
}

:deep(.el-form-item) {
  margin-bottom: $spacing-md;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  border-radius: $radius-lg;
}

:deep(.el-button--primary) {
  @include button-primary;
}
</style>

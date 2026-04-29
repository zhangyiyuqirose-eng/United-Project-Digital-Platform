<template>
  <div class="supplier-list-page">
    <PageHeader title="供应商管理" description="管理供应商信息，维护合作关系与评级">
      <el-button class="create-btn" @click="showDialog = true"><el-icon><Plus /></el-icon> 新增供应商</el-button>
    </PageHeader>

    <SearchForm :model="searchForm" @search="handleSearch" @reset="handleReset">
      <el-form-item label="关键词">
        <el-input v-model="searchForm.keyword" placeholder="供应商名称" clearable />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="searchForm.category" placeholder="全部" clearable>
          <el-option label="外包服务" value="OUTSOURCING" />
          <el-option label="设备供应商" value="EQUIPMENT" />
          <el-option label="咨询服务" value="CONSULTING" />
        </el-select>
      </el-form-item>
    </SearchForm>

    <el-card>
      <template #header>
        <div class="card-header"><span>供应商列表</span></div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="supplierCode" label="编码" width="100" />
        <el-table-column prop="supplierName" label="名称" min-width="160" />
        <el-table-column prop="contactPerson" label="联系人" width="100" />
        <el-table-column prop="contactPhone" label="电话" width="130" />
        <el-table-column prop="contactEmail" label="邮箱" width="160" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="rating" label="评级" width="80">
          <template #default="{ row }">
            <el-rate v-model="row._rating" disabled :max="5" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><StatusTag :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.supplierId)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <Pagination :total="total" :page="page" :limit="limit" @change="handlePageChange" />
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑供应商' : '新增供应商'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.supplierName" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contactPerson" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.contactPhone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.contactEmail" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category"><el-option label="外包服务" value="OUTSOURCING" /><el-option label="设备供应商" value="EQUIPMENT" /><el-option label="咨询服务" value="CONSULTING" /></el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="showDialog = false">取消</el-button><el-button type="primary" @click="handleSubmit">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getSupplierList, createSupplier, updateSupplier, deleteSupplier } from '@/api/modules/business'
import PageHeader from '@/components/PageHeader.vue'
import SearchForm from '@/components/SearchForm.vue'
import Pagination from '@/components/Pagination.vue'
import StatusTag from '@/components/StatusTag.vue'

const loading = ref(false)
const tableData = ref<unknown[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const showDialog = ref(false)
const editingId = ref('')
const searchForm = reactive({ keyword: '', category: '' })

const form = reactive({ supplierName: '', contactPerson: '', contactPhone: '', contactEmail: '', address: '', category: '' })

async function fetchData() {
  loading.value = true
  try {
    const res = await getSupplierList({ page: page.value, limit: limit.value, ...searchForm })
    tableData.value = res.records.map((r) => ({ ...r, _rating: typeof r.rating === 'string' ? parseInt(r.rating) || 3 : r.rating || 3 }))
    total.value = res.total
  } finally { loading.value = false }
}

function handleSearch() { page.value = 1; fetchData() }
function handleReset() { searchForm.keyword = ''; searchForm.category = ''; page.value = 1; fetchData() }
function handlePageChange(v: { page: number; limit: number }) { page.value = v.page; limit.value = v.limit; fetchData() }

function handleEdit(row: Record<string, unknown>) {
  editingId.value = row.supplierId as string
  Object.assign(form, { supplierName: row.supplierName, contactPerson: row.contactPerson, contactPhone: row.contactPhone, contactEmail: row.contactEmail, address: row.address, category: row.category })
  showDialog.value = true
}

async function handleDelete(id: string) {
  try { await deleteSupplier(id); ElMessage.success('删除成功'); fetchData() } catch { /* handled */ }
}

async function handleSubmit() {
  try {
    if (editingId.value) { await updateSupplier(editingId.value, form) } else { await createSupplier(form) }
    ElMessage.success('保存成功'); showDialog.value = false; fetchData()
  } catch { /* handled */ }
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.supplier-list-page {
  max-width: 1400px;
}

.card-header { display: flex; justify-content: space-between; align-items: center; }

.create-btn {
  @include button-primary;
}
</style>

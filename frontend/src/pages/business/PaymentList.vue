<template>
  <div class="payment-list-page">
    <PageHeader title="付款计划" description="管理付款计划，跟踪合同款项支付进度" />

    <SearchForm :model="searchForm" @search="handleSearch" @reset="handleReset">
      <el-form-item label="合同">
        <el-input v-model="searchForm.contractId" placeholder="合同ID" clearable />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="全部" clearable>
          <el-option label="未支付" value="UNPAID" />
          <el-option label="已支付" value="PAID" />
          <el-option label="部分支付" value="PARTIAL" />
          <el-option label="已逾期" value="OVERDUE" />
        </el-select>
      </el-form-item>
    </SearchForm>

    <el-card>
      <template #header>
        <div class="card-header"><span>付款计划</span></div>
      </template>
      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="contractName" label="合同" min-width="160" />
        <el-table-column prop="phase" label="阶段" width="120" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">¥{{ row.amount?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="plannedDate" label="计划日期" width="110" />
        <el-table-column prop="actualDate" label="实际日期" width="110" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><StatusTag :status="row.status" /></template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button link type="success" v-if="row.status === 'UNPAID'" @click="handleConfirm(row)">确认付款</el-button>
          </template>
        </el-table-column>
      </el-table>
      <Pagination :total="total" :page="page" :limit="limit" @change="handlePageChange" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPaymentList, confirmPayment } from '@/api/modules/business'
import PageHeader from '@/components/PageHeader.vue'
import SearchForm from '@/components/SearchForm.vue'
import Pagination from '@/components/Pagination.vue'
import StatusTag from '@/components/StatusTag.vue'

const loading = ref(false)
const tableData = ref<unknown[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const searchForm = reactive({ contractId: '', status: '' })

async function fetchData() {
  loading.value = true
  try {
    const res = await getPaymentList({ page: page.value, limit: limit.value, ...searchForm })
    tableData.value = res.records; total.value = res.total
  } finally { loading.value = false }
}

function handleSearch() { page.value = 1; fetchData() }
function handleReset() { searchForm.contractId = ''; searchForm.status = ''; page.value = 1; fetchData() }
function handlePageChange(v: { page: number; limit: number }) { page.value = v.page; limit.value = v.limit; fetchData() }

async function handleConfirm(row: Record<string, unknown>) {
  try { await confirmPayment(row.paymentId as string); ElMessage.success('确认成功'); fetchData() } catch { /* handled */ }
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.payment-list-page {
  max-width: 1400px;
}
</style>

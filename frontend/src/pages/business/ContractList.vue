<template>
  <div class="contract-page">
    <!-- 页面头部 -->
    <PageHeader title="合同管理" description="管理销售合同、采购合同及框架协议">
      <button class="create-btn" @click="openCreate">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        <span>新增合同</span>
      </button>
    </PageHeader>

    <!-- 统计概览 -->
    <ContractStats :stats="stats" />

    <!-- 合同列表 + 搜索 -->
    <ContractTable
      ref="tableRef"
      @stats-update="onStatsUpdate"
      @view="onView"
      @edit="onEdit"
      @delete="onDelete"
    />

    <!-- 新增/编辑对话框 -->
    <ContractDialog
      :visible="showDialog"
      :editing-id="editingId"
      :editing-data="editingData"
      @close="showDialog = false"
      @saved="onSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteContract } from '@/api/modules/business'
import PageHeader from '@/components/PageHeader.vue'
import ContractStats from './ContractStats.vue'
import ContractTable from './ContractTable.vue'
import ContractDialog from './ContractDialog.vue'

const tableRef = ref<InstanceType<typeof ContractTable> | null>(null)
const showDialog = ref(false)
const editingId = ref('')
const editingData = ref<Record<string, any>>({})

const stats = ref({ sales: 0, purchase: 0, framework: 0, totalAmount: 0 })

function onStatsUpdate(s: { sales: number; purchase: number; framework: number; totalAmount: number }) {
  stats.value = s
}

function openCreate() {
  editingId.value = ''
  editingData.value = {}
  showDialog.value = true
}

function onView(row: any) {
  ElMessage.info(`查看合同: ${row.contractName}`)
}

function onEdit(row: any) {
  editingId.value = row.contractId
  editingData.value = { ...row }
  showDialog.value = true
}

async function onDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定删除此合同？此操作不可撤销', '删除确认', { type: 'warning' })
    await deleteContract(id)
    ElMessage.success('删除成功')
    tableRef.value?.fetchData()
  } catch { /* cancelled */ }
}

function onSaved() {
  tableRef.value?.fetchData()
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.contract-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px; // 左右外边距 32px
}

.create-btn {
  @include button-primary;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  font-size: $font-size-md;

  svg { width: 20px; height: 20px; }
}
</style>

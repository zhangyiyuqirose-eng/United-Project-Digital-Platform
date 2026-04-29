<template>
  <div class="data-table">
    <el-table
      :data="data"
      v-loading="loading"
      stripe
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column v-if="selectable" type="selection" width="55" />
      <slot />
    </el-table>
    <div v-if="pagination" class="data-table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="$emit('page-change', { page: $event, limit: pageSize })"
        @update:page-size="$emit('page-change', { page: currentPage, limit: $event })"
      />
    </div>
    <EmptyState
      v-if="!loading && (!data || data.length === 0)"
      :title="emptyText"
      :description="emptyDescription"
    >
      <template #action><slot name="empty-action" /></template>
    </EmptyState>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import EmptyState from './EmptyState.vue'

defineProps<{
  data: any[]
  loading?: boolean
  selectable?: boolean
  pagination?: boolean
  total?: number
  emptyText?: string
  emptyDescription?: string
}>()

const emit = defineEmits<{
  'page-change': [payload: { page: number; limit: number }]
  'selection-change': [selection: any[]]
}>()

const currentPage = ref(1)
const pageSize = ref(20)

function handleSelectionChange(selection: any[]) {
  emit('selection-change', selection)
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.data-table {
  &-pagination {
    display: flex;
    justify-content: flex-end;
    padding: $spacing-lg 0;
  }
}
</style>

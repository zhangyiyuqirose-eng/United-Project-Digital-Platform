<template>
  <div class="pagination-wrapper">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      background
      @size-change="$emit('change', { page: currentPage, limit: pageSize })"
      @current-change="$emit('change', { page: currentPage, limit: pageSize })"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  total: number
  page: number
  limit: number
}>(), {
  total: 0,
  page: 1,
  limit: 10,
})

defineEmits<{
  change: [{ page: number; limit: number }]
}>()

const currentPage = ref(props.page)
const pageSize = ref(props.limit)

watch(() => props.page, (v) => { currentPage.value = v })
watch(() => props.limit, (v) => { pageSize.value = v })
</script>

<style scoped lang="scss">
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}
</style>

<template>
  <el-form :model="model" inline class="search-form">
    <slot />
    <el-form-item>
      <el-button type="primary" @click="$emit('search')">
        <el-icon><Search /></el-icon>
        查询
      </el-button>
      <el-button @click="$emit('reset')">
        <el-icon><RefreshLeft /></el-icon>
        重置
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { Search, RefreshLeft } from '@element-plus/icons-vue'

defineProps<{
  model: Record<string, unknown>
}>()

defineEmits<{
  search: []
  reset: []
}>()
</script>

<style scoped lang="scss">
.search-form {
  background: #fff;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
}
</style>

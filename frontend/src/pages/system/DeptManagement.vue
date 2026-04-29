<template>
  <div class="page-container">
    <PageHeader title="部门管理" description="配置组织架构与部门层级">
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon> 新增部门</el-button>
    </PageHeader>

    <div class="content-card">

      <el-table v-loading="loading" :data="tableData" row-key="deptId" default-expand-all stripe>
        <el-table-column prop="deptName" label="部门名称" min-width="200" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.deptId)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑部门' : '新增部门'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="部门名称"><el-input v-model="form.deptName" /></el-form-item>
        <el-form-item label="上级部门"><el-input v-model="form.parentId" placeholder="根部门留空" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showDialog = false">取消</el-button><el-button type="primary" @click="handleSubmit">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getDeptTree, createDept, updateDept, deleteDept, type DeptForm } from '@/api/modules/system'
import PageHeader from '@/components/PageHeader.vue'

const loading = ref(false)
const tableData = ref<unknown[]>([])
const showDialog = ref(false)
const editingId = ref('')

const form = reactive<DeptForm>({ deptName: '', parentId: '', sort: 0, status: 1 })

async function fetchData() {
  loading.value = true
  try { tableData.value = await getDeptTree() } catch { tableData.value = [] } finally { loading.value = false }
}

function handleEdit(row: Record<string, unknown>) {
  editingId.value = row.deptId as string
  Object.assign(form, { deptName: row.deptName, parentId: row.parentId, sort: row.sort, status: row.status })
  showDialog.value = true
}

async function handleDelete(id: string) {
  try { await deleteDept(id); ElMessage.success('删除成功'); fetchData() } catch { /* handled */ }
}

async function handleSubmit() {
  try {
    if (editingId.value) { await updateDept(editingId.value, form) } else { await createDept(form) }
    ElMessage.success('保存成功'); showDialog.value = false; fetchData()
  } catch { /* handled */ }
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.page-container {
  padding: $content-padding;
  max-width: 1400px;
}

.content-card {
  @include card-base;
  padding: $card-padding;
  margin-top: $spacing-lg;
}

:deep(.el-button--primary) {
  @include button-primary;
}

@media (max-width: 768px) {
  .page-container {
    padding: $spacing-lg;
  }

  .content-card {
    padding: $spacing-md;
  }
}
</style>

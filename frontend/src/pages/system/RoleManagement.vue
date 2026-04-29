<template>
  <div class="page-container">
    <PageHeader title="角色管理" description="定义系统角色及其权限边界">
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon> 新增角色</el-button>
    </PageHeader>

    <div class="content-card">

      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="roleCode" label="编码" width="120" />
        <el-table-column prop="roleName" label="名称" width="140" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="warning" @click="handlePermissions(row)">权限</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.roleId)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <Pagination :total="total" :page="page" :limit="limit" @change="handlePageChange" />
    </div>

    <!-- Role Dialog -->
    <el-dialog v-model="showDialog" :title="editingId ? '编辑角色' : '新增角色'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.roleName" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="form.roleCode" :disabled="!!editingId" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showDialog = false">取消</el-button><el-button type="primary" @click="handleSubmit">保存</el-button></template>
    </el-dialog>

    <!-- Permission Dialog -->
    <el-dialog v-model="permDialogVisible" title="分配权限" width="500px">
      <el-tree
        ref="permTreeRef"
        :data="permissionTree"
        :props="{ label: 'permissionName', children: 'children' }"
        show-checkbox
        node-key="permissionId"
        default-expand-all
      />
      <template #footer><el-button @click="permDialogVisible = false">取消</el-button><el-button type="primary" @click="handleSavePermissions">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { TreeInstance } from 'element-plus'
import { getRoleList, createRole, updateRole, deleteRole, assignPermissions, getPermissionTree, getPermissionsByRole, type RoleForm } from '@/api/modules/system'
import Pagination from '@/components/Pagination.vue'
import PageHeader from '@/components/PageHeader.vue'

const loading = ref(false)
const tableData = ref<unknown[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const showDialog = ref(false)
const permDialogVisible = ref(false)
const editingId = ref('')
const selectedRoleId = ref('')
const permTreeRef = ref<TreeInstance>()

const form = reactive<RoleForm>({ roleName: '', roleCode: '', description: '', permissionIds: [], status: 1 })
const permissionTree = ref<unknown[]>([])

async function fetchData() {
  loading.value = true
  try {
    const res = await getRoleList({ page: page.value, limit: limit.value })
    tableData.value = res.records; total.value = res.total
  } finally { loading.value = false }
}

async function loadPermissions() {
  try { permissionTree.value = await getPermissionTree() } catch { permissionTree.value = [] }
}

function handlePageChange(v: { page: number; limit: number }) { page.value = v.page; limit.value = v.limit; fetchData() }

function handleEdit(row: Record<string, unknown>) {
  editingId.value = row.roleId as string
  Object.assign(form, { roleName: row.roleName, roleCode: row.roleCode, description: row.description, status: row.status })
  showDialog.value = true
}

async function handlePermissions(row: Record<string, unknown>) {
  selectedRoleId.value = row.roleId as string
  await loadPermissions()
  try {
    const perms = await getPermissionsByRole(row.roleId as string)
    const checked = perms.map((p) => p.permissionId)
    setTimeout(() => permTreeRef.value?.setCheckedKeys(checked), 100)
  } catch { /* handled */ }
  permDialogVisible.value = true
}

async function handleSavePermissions() {
  const checked = permTreeRef.value?.getCheckedKeys() as string[] || []
  const halfChecked = permTreeRef.value?.getHalfCheckedKeys() as string[] || []
  const allKeys = [...checked, ...halfChecked]
  try { await assignPermissions(selectedRoleId.value, allKeys); ElMessage.success('保存成功'); permDialogVisible.value = false } catch { /* handled */ }
}

async function handleDelete(id: string) {
  try { await deleteRole(id); ElMessage.success('删除成功'); fetchData() } catch { /* handled */ }
}

async function handleSubmit() {
  try {
    if (editingId.value) { await updateRole(editingId.value, form) } else { await createRole(form) }
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

  :deep(.el-table) {
    font-size: $font-size-sm;
  }
}
</style>

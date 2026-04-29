<template>
  <div class="page-container">
    <PageHeader title="用户管理" description="管理系统用户、角色分配与状态控制">
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon> 新增用户</el-button>
    </PageHeader>

    <SearchForm :model="searchForm" @search="handleSearch" @reset="handleReset">
      <el-form-item label="关键词">
        <el-input v-model="searchForm.keyword" placeholder="用户名/姓名" clearable />
      </el-form-item>
    </SearchForm>

    <div class="content-card">

      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="deptName" label="部门" width="120" />
        <el-table-column prop="phone" label="手机" width="130" />
        <el-table-column prop="email" label="邮箱" width="160" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="warning" @click="handleRole(row)">角色</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.userId)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <Pagination :total="total" :page="page" :limit="limit" @change="handlePageChange" />
    </div>

    <!-- User Dialog -->
    <el-dialog v-model="showDialog" :title="editingId ? '编辑用户' : '新增用户'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="form.username" :disabled="!!editingId" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="部门"><el-input v-model="form.deptId" /></el-form-item>
        <el-form-item label="密码" v-if="!editingId"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="手机"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.roleIds" multiple>
            <el-option v-for="r in allRoles" :key="r.roleId" :label="r.roleName" :value="r.roleId" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="showDialog = false">取消</el-button><el-button type="primary" @click="handleSubmit">保存</el-button></template>
    </el-dialog>

    <!-- Role Assignment Dialog -->
    <el-dialog v-model="roleDialogVisible" title="分配角色" width="400px">
      <el-select v-model="selectedRoles" multiple style="width: 100%">
        <el-option v-for="r in allRoles" :key="r.roleId" :label="r.roleName" :value="r.roleId" />
      </el-select>
      <template #footer><el-button @click="roleDialogVisible = false">取消</el-button><el-button type="primary" @click="handleAssignRoles">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getUserList, createUser, updateUser, deleteUser, assignRoles, getAllRoles, type UserForm, type RoleVO } from '@/api/modules/system'
import SearchForm from '@/components/SearchForm.vue'
import Pagination from '@/components/Pagination.vue'
import PageHeader from '@/components/PageHeader.vue'

const loading = ref(false)
const tableData = ref<unknown[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const showDialog = ref(false)
const roleDialogVisible = ref(false)
const editingId = ref('')
const searchForm = reactive({ keyword: '' })
const allRoles = ref<RoleVO[]>([])
const selectedUserId = ref('')
const selectedRoles = ref<string[]>([])

const form = reactive<UserForm>({ username: '', name: '', deptId: '', password: '', phone: '', email: '', roleIds: [], status: 1 })

async function fetchData() {
  loading.value = true
  try {
    const res = await getUserList({ page: page.value, limit: limit.value, ...searchForm })
    tableData.value = res.records; total.value = res.total
  } finally { loading.value = false }
}

async function loadRoles() {
  try { allRoles.value = await getAllRoles() } catch { allRoles.value = [] }
}

function handleSearch() { page.value = 1; fetchData() }
function handleReset() { searchForm.keyword = ''; page.value = 1; fetchData() }
function handlePageChange(v: { page: number; limit: number }) { page.value = v.page; limit.value = v.limit; fetchData() }

function handleEdit(row: Record<string, unknown>) {
  editingId.value = row.userId as string
  Object.assign(form, { username: row.username, name: row.name, deptId: row.deptId, phone: row.phone, email: row.email, roleIds: [], status: row.status })
  showDialog.value = true
}

function handleRole(row: Record<string, unknown>) {
  selectedUserId.value = row.userId as string
  selectedRoles.value = []
  roleDialogVisible.value = true
}

async function handleAssignRoles() {
  try { await assignRoles(selectedUserId.value, selectedRoles.value); ElMessage.success('分配成功'); roleDialogVisible.value = false } catch { /* handled */ }
}

async function handleDelete(id: string) {
  try { await deleteUser(id); ElMessage.success('删除成功'); fetchData() } catch { /* handled */ }
}

async function handleSubmit() {
  try {
    if (editingId.value) { await updateUser(editingId.value, form) } else { await createUser(form) }
    ElMessage.success('保存成功'); showDialog.value = false; fetchData()
  } catch { /* handled */ }
}

onMounted(() => { fetchData(); loadRoles() })
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

  :deep(.el-form-item__label) {
    font-size: $font-size-sm;
  }
}
</style>

<template>
  <div class="page-container">
    <PageHeader title="权限管理" description="查看权限树与角色权限分配概览" />

    <div class="content-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="sub-card">
            <div class="sub-card-header"><span>权限树</span></div>
            <el-tree
              :data="permissionTree"
              :props="{ label: 'permissionName', children: 'children' }"
              default-expand-all
              node-key="permissionId"
            >
              <template #default="{ data }">
                <span class="perm-node">
                  <el-tag size="small" :type="data.type === 'MENU' ? '' : 'info'">{{ data.type === 'MENU' ? '菜单' : '按钮' }}</el-tag>
                  <span class="ml-8">{{ data.permissionName }}</span>
                  <span class="perm-code">[{{ data.permissionCode }}]</span>
                </span>
              </template>
            </el-tree>
          </div>
        </el-col>
        <el-col :span="16">
          <div class="sub-card">
            <div class="sub-card-header">
              <span>按角色查询权限</span>
              <el-select v-model="selectedRoleId" placeholder="选择角色" class="role-select" @change="handleRoleChange">
                <el-option v-for="r in roles" :key="r.roleId" :label="r.roleName" :value="r.roleId" />
              </el-select>
            </div>
            <el-table :data="rolePermissions" stripe>
              <el-table-column prop="permissionName" label="权限名称" min-width="180" />
              <el-table-column prop="permissionCode" label="权限编码" width="160" />
              <el-table-column prop="type" label="类型" width="80">
                <template #default="{ row }"><el-tag size="small">{{ row.type === 'MENU' ? '菜单' : '按钮' }}</el-tag></template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getPermissionTree, getPermissionsByRole, getRoleList, type PermissionVO, type RoleVO } from '@/api/modules/system'
import PageHeader from '@/components/PageHeader.vue'

const permissionTree = ref<PermissionVO[]>([])
const roles = ref<RoleVO[]>([])
const selectedRoleId = ref('')
const rolePermissions = ref<PermissionVO[]>([])

async function loadPermissions() {
  try { permissionTree.value = await getPermissionTree() } catch { permissionTree.value = [] }
}

async function loadRoles() {
  try { roles.value = await getRoleList({ page: 1, limit: 100 }) as unknown as RoleVO[] } catch { roles.value = [] }
}

async function handleRoleChange(roleId: string) {
  try { rolePermissions.value = await getPermissionsByRole(roleId) } catch { rolePermissions.value = [] }
}

onMounted(() => { loadPermissions(); loadRoles() })
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

.sub-card {
  @include card-base;
  padding: $card-padding;

  + .sub-card {
    margin-top: $spacing-lg;
  }
}

.sub-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
  font-weight: $font-weight-semibold;
  color: $text-primary;
  font-size: $font-size-lg;
}

.role-select {
  width: 200px;
  margin-left: $spacing-lg;
}

.perm-node { display: flex; align-items: center; }
.ml-8 { margin-left: $spacing-sm; }
.perm-code { margin-left: $spacing-sm; color: $text-muted; font-size: $font-size-xs; }

@media (max-width: 768px) {
  .page-container {
    padding: $spacing-lg;
  }

  .sub-card {
    padding: $spacing-md;
  }

  .role-select {
    width: 100%;
    margin-left: 0;
    margin-top: $spacing-sm;
  }

  .sub-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-sm;
  }
}
</style>

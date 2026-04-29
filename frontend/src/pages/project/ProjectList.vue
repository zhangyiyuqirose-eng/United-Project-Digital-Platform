<template>
  <div class="project-list-page">
    <!-- 页面头部 -->
    <PageHeader title="项目管理" description="管理所有项目信息，跟踪项目进度和状态">
      <button class="create-btn" @click="handleCreate">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        <span>新建项目</span>
      </button>
    </PageHeader>

    <!-- 搜索区域 -->
    <ProjectSearch :total="total" @filter-change="onFilterChange" />

    <!-- 数据表格 -->
    <ProjectTable
      ref="tableRef"
      @view="handleView"
      @edit="handleEdit"
      @workflow="handleStartWorkflow"
      @delete="confirmDelete"
      @total-update="total = $event"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteProject, type ProjectVO } from '@/api/modules/project'
import PageHeader from '@/components/PageHeader.vue'
import ProjectSearch from './ProjectSearch.vue'
import ProjectTable from './ProjectTable.vue'

const router = useRouter()
const tableRef = ref<InstanceType<typeof ProjectTable> | null>(null)
const total = ref(0)

function onFilterChange(params: { keyword: string; status: string }) {
  tableRef.value?.setFilters({ keyword: params.keyword, status: params.status })
}

function handleCreate() {
  router.push('/project/create')
}

function handleView(row: ProjectVO) {
  router.push(`/project/${row.projectId}`)
}

function handleEdit(row: ProjectVO) {
  router.push(`/project/create?id=${row.projectId}`)
}

function handleStartWorkflow(row: ProjectVO) {
  router.push(`/workflow/start?project=${row.projectId}`)
}

async function confirmDelete(row: ProjectVO) {
  try {
    await ElMessageBox.confirm('确定删除该项目？此操作不可撤销', '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteProject(row.projectId)
    ElMessage.success('删除成功')
    tableRef.value?.fetchData()
  } catch {
    // cancelled or error
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.project-list-page {
  max-width: 1400px;
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

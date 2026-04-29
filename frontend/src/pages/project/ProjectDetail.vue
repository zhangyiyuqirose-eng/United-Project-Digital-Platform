<template>
  <div class="page-container">
    <PageHeader :title="project?.projectName || '项目详情'" description="查看项目概览、WBS分解、任务、风险与文档">
      <el-button @click="goBack">返回列表</el-button>
    </PageHeader>

    <el-tabs v-model="activeTab" class="detail-tabs">
      <el-tab-pane label="项目概览" name="overview">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目编号">{{ project?.projectCode }}</el-descriptions-item>
          <el-descriptions-item label="项目名称">{{ project?.projectName }}</el-descriptions-item>
          <el-descriptions-item label="项目类型">{{ project?.projectType }}</el-descriptions-item>
          <el-descriptions-item label="项目经理">{{ project?.managerName }}</el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ project?.startDate }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ project?.endDate }}</el-descriptions-item>
          <el-descriptions-item label="预算金额">{{ project?.budget ? `¥${project.budget.toLocaleString()}` : '-' }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ project?.customer || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态"><StatusTag :status="project?.status || ''" /></el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ project?.createTime }}</el-descriptions-item>
          <el-descriptions-item label="项目描述" :span="2">{{ project?.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>

      <el-tab-pane label="WBS分解" name="wbs">
        <el-tree :data="wbsTree" :props="{ label: 'name', children: 'children' }" default-expand-all />
      </el-tab-pane>

      <el-tab-pane label="任务列表" name="tasks">
        <el-table :data="tasks" stripe>
          <el-table-column prop="taskName" label="任务名称" min-width="160" />
          <el-table-column prop="assigneeName" label="负责人" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }"><StatusTag :status="row.status" /></template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="80">
            <template #default="{ row }"><StatusTag :status="row.priority" /></template>
          </el-table-column>
          <el-table-column prop="startDate" label="开始日期" width="110" />
          <el-table-column prop="endDate" label="截止日期" width="110" />
          <el-table-column prop="progress" label="进度" width="120">
            <template #default="{ row }">
              <el-progress :percentage="row.progress" :stroke-width="12" />
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="风险管理" name="risks">
        <el-button type="primary" class="action-btn" @click="riskDialogVisible = true">添加风险</el-button>
        <el-table :data="risks" stripe>
          <el-table-column prop="riskName" label="风险名称" min-width="160" />
          <el-table-column prop="riskType" label="类型" width="100" />
          <el-table-column prop="probability" label="概率" width="80" />
          <el-table-column prop="impact" label="影响" width="80" />
          <el-table-column prop="level" label="等级" width="80">
            <template #default="{ row }"><StatusTag :status="row.level" /></template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }"><StatusTag :status="row.status" /></template>
          </el-table-column>
          <el-table-column prop="ownerName" label="责任人" width="100" />
          <el-table-column prop="mitigation" label="应对措施" min-width="180" />
        </el-table>
        <el-dialog v-model="riskDialogVisible" title="添加风险" width="500px">
          <el-form :model="riskForm" label-width="80px">
            <el-form-item label="风险名称"><el-input v-model="riskForm.riskName" /></el-form-item>
            <el-form-item label="类型">
              <el-select v-model="riskForm.riskType"><el-option label="技术" value="TECH" /><el-option label="管理" value="MANAGEMENT" /><el-option label="商务" value="BUSINESS" /></el-select>
            </el-form-item>
            <el-form-item label="应对措施"><el-input v-model="riskForm.mitigation" type="textarea" :rows="3" /></el-form-item>
          </el-form>
          <template #footer><el-button @click="riskDialogVisible = false">取消</el-button><el-button type="primary" @click="handleAddRisk">确定</el-button></template>
        </el-dialog>
      </el-tab-pane>

      <el-tab-pane label="甘特图" name="gantt">
        <GanttChart :tasks="ganttTasks" />
      </el-tab-pane>

      <el-tab-pane label="文档管理" name="documents">
        <el-button type="primary" class="action-btn">上传文档</el-button>
        <el-table :data="[]" stripe>
          <el-table-column prop="title" label="文档名称" min-width="200" />
          <el-table-column prop="category" label="分类" width="120" />
          <el-table-column prop="uploader" label="上传人" width="100" />
          <el-table-column prop="uploadTime" label="上传时间" width="160" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import { getProjectDetail, getWbsTree, getProjectTasks, getProjectRisks, getGanttData, createRisk, type RiskVO, type GanttTaskVO } from '@/api/modules/project'
import { ElMessage } from 'element-plus'
import StatusTag from '@/components/StatusTag.vue'
import GanttChart from '@/components/GanttChart.vue'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string
const activeTab = ref('overview')

const project = ref()
const wbsTree = ref<unknown[]>([])
const tasks = ref<unknown[]>([])
const risks = ref<RiskVO[]>([])
const ganttTasks = ref<GanttTaskVO[]>([])
const riskDialogVisible = ref(false)
const riskForm = reactive({ riskName: '', riskType: '', mitigation: '' })

async function loadProject() {
  project.value = await getProjectDetail(projectId)
}

async function loadWbs() {
  try { wbsTree.value = await getWbsTree(projectId) } catch { wbsTree.value = [] }
}

async function loadTasks() {
  try { tasks.value = await getProjectTasks(projectId) } catch { tasks.value = [] }
}

async function loadRisks() {
  try { risks.value = await getProjectRisks(projectId) } catch { risks.value = [] }
}

async function loadGantt() {
  try { ganttTasks.value = await getGanttData(projectId) } catch { ganttTasks.value = [] }
}

async function handleAddRisk() {
  try {
    await createRisk(projectId, { ...riskForm })
    ElMessage.success('添加成功')
    riskDialogVisible.value = false
    loadRisks()
  } catch { /* handled */ }
}

function goBack() { router.push('/project') }

onMounted(() => {
  loadProject()
  loadWbs()
  loadTasks()
  loadRisks()
  loadGantt()
})
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.page-container {
  padding: $spacing-2xl;
  max-width: 1400px;
}

.detail-tabs {
  @include card-base;
  padding: $spacing-lg;

  :deep(.el-tabs__header) {
    margin-bottom: $spacing-xl;
  }

  :deep(.el-tabs--border-card) {
    border: none;
    box-shadow: none;
  }
}

.action-btn {
  margin-bottom: $spacing-lg;
  @include button-primary;
}

:deep(.el-descriptions__label) {
  font-weight: $font-weight-semibold;
  color: $text-secondary;
}

:deep(.el-descriptions__content) {
  color: $text-primary;
}
</style>

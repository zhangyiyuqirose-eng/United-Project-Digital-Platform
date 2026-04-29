<template>
  <div class="resource-pool-page">
    <!-- 页面头部 -->
    <PageHeader title="入池人员资源管理" description="管理入池人力资源，支持人员分配与释放">
      <div class="header-stats">
        <div class="stat-mini">
          <span class="stat-num">{{ stats.total }}</span>
          <span class="stat-label">总人数</span>
        </div>
        <div class="stat-mini available">
          <span class="stat-num">{{ stats.available }}</span>
          <span class="stat-label">可分配</span>
        </div>
        <div class="stat-mini assigned">
          <span class="stat-num">{{ stats.assigned }}</span>
          <span class="stat-label">已分配</span>
        </div>
      </div>
    </PageHeader>

    <!-- 搜索 + 卡片网格 -->
    <PersonCardGrid
      ref="gridRef"
      @assign="onAssign"
      @release="onRelease"
      @view="onView"
      @stats-update="onStatsUpdate"
    />

    <!-- 分配对话框 -->
    <PoolOperationDialog
      :visible="dialogVisible"
      :resource="selectedResource"
      @close="dialogVisible = false"
      @confirmed="onAssignConfirmed"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { PersonVO } from '@/api/modules/resource'
import PageHeader from '@/components/PageHeader.vue'
import PersonCardGrid from './PersonCardGrid.vue'
import PoolOperationDialog from './PoolOperationDialog.vue'

const gridRef = ref<InstanceType<typeof PersonCardGrid> | null>(null)
const dialogVisible = ref(false)
const selectedResource = ref<PersonVO | null>(null)

const stats = ref({ total: 0, available: 0, assigned: 0 })

function onStatsUpdate(s: { total: number; available: number; assigned: number }) {
  stats.value = s
}

function onAssign(person: PersonVO) {
  selectedResource.value = person
  dialogVisible.value = true
}

function onRelease(_person: PersonVO) {
  ElMessage.success('资源已释放')
  gridRef.value?.fetchData()
}

function onView(person: PersonVO) {
  ElMessage.info(`查看 ${person.name} 的详细信息`)
}

function onAssignConfirmed() {
  gridRef.value?.fetchData()
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.resource-pool-page {
  max-width: 1400px;
}

.header-stats {
  display: flex;
  gap: $spacing-md;

  .stat-mini {
    @include card-base;
    padding: $spacing-md $spacing-lg;
    text-align: center;

    .stat-num {
      font-size: $font-size-xl;
      font-weight: $font-weight-bold;
      color: $text-primary;
      display: block;
    }

    .stat-label {
      font-size: $font-size-sm;
      color: $text-muted;
    }

    &.available .stat-num { color: $success-color; }
    &.assigned .stat-num { color: $accent-color; }
  }
}

@media (max-width: 900px) {
  .header-stats {
    flex-wrap: wrap;
  }
}
</style>

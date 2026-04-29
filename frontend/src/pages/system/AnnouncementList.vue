<template>
  <div class="page-container">
    <PageHeader title="公告管理" description="发布和管理系统通知与公告">
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon> 发布公告</el-button>
    </PageHeader>

    <div class="content-card">

      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type === 'NOTICE' ? '通知' : row.type === 'ANNOUNCEMENT' ? '公告' : '其他' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publisher" label="发布人" width="100" />
        <el-table-column prop="publishTime" label="发布时间" width="160" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '已发布' : '草稿' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="success" v-if="row.status === 0" @click="handlePublish(row)">发布</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.announcementId)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <Pagination :total="total" :page="page" :limit="limit" @change="handlePageChange" />
    </div>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑公告' : '发布公告'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type"><el-option label="通知" value="NOTICE" /><el-option label="公告" value="ANNOUNCEMENT" /><el-option label="其他" value="OTHER" /></el-select>
        </el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="6" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showDialog = false">取消</el-button><el-button type="primary" @click="handleSubmit">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getAnnouncementList, createAnnouncement, updateAnnouncement, deleteAnnouncement, publishAnnouncement, type AnnouncementForm } from '@/api/modules/system'
import Pagination from '@/components/Pagination.vue'
import PageHeader from '@/components/PageHeader.vue'

const loading = ref(false)
const tableData = ref<unknown[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const showDialog = ref(false)
const editingId = ref('')

const form = reactive<AnnouncementForm>({ title: '', content: '', type: 'NOTICE' })

async function fetchData() {
  loading.value = true
  try {
    const res = await getAnnouncementList({ page: page.value, limit: limit.value })
    tableData.value = res.records; total.value = res.total
  } finally { loading.value = false }
}

function handlePageChange(v: { page: number; limit: number }) { page.value = v.page; limit.value = v.limit; fetchData() }

function handleEdit(row: Record<string, unknown>) {
  editingId.value = row.announcementId as string
  Object.assign(form, { title: row.title, content: row.content, type: row.type })
  showDialog.value = true
}

async function handlePublish(row: Record<string, unknown>) {
  try { await publishAnnouncement(row.announcementId as string); ElMessage.success('发布成功'); fetchData() } catch { /* handled */ }
}

async function handleDelete(id: string) {
  try { await deleteAnnouncement(id); ElMessage.success('删除成功'); fetchData() } catch { /* handled */ }
}

async function handleSubmit() {
  try {
    if (editingId.value) { await updateAnnouncement(editingId.value, form) } else { await createAnnouncement(form) }
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

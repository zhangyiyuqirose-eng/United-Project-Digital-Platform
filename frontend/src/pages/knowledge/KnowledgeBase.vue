<template>
  <div class="knowledge-base-page">
    <PageHeader title="知识库" description="文档管理与模板中心" />

    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="文档管理" name="documents">
        <SearchForm :model="docSearchForm" @search="handleDocSearch" @reset="handleDocReset">
          <el-form-item label="项目"><el-input v-model="docSearchForm.projectId" placeholder="项目ID" clearable /></el-form-item>
          <el-form-item label="分类">
            <el-select v-model="docSearchForm.category" placeholder="全部" clearable>
              <el-option label="需求" value="REQUIREMENT" /><el-option label="设计" value="DESIGN" /><el-option label="测试" value="TEST" /><el-option label="验收" value="ACCEPTANCE" />
            </el-select>
          </el-form-item>
        </SearchForm>
        <el-card>
          <template #header><div class="card-header"><span>文档列表</span><el-upload action="/api/knowledge/document/upload" :headers="uploadHeaders" :on-success="handleUploadSuccess"><template #trigger><el-button type="primary">上传文档</el-button></template></el-upload></div></template>
          <el-table v-loading="docLoading" :data="docData" stripe>
            <el-table-column prop="title" label="名称" min-width="180" />
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column prop="projectName" label="项目" width="140" />
            <el-table-column prop="uploader" label="上传人" width="100" />
            <el-table-column prop="fileSize" label="大小" width="100"><template #default="{ row }">{{ formatSize(row.fileSize) }}</template></el-table-column>
            <el-table-column prop="uploadTime" label="上传时间" width="160" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleDownload(row)">下载</el-button>
                <el-popconfirm title="确定删除？" @confirm="handleDeleteDoc(row.documentId)"><template #reference><el-button link type="danger">删除</el-button></template></el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          <Pagination :total="docTotal" :page="docPage" :limit="docLimit" @change="handleDocPageChange" />
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="模板中心" name="templates">
        <el-card><template #header><span>文档模板</span></template>
          <el-table :data="templateData" stripe>
            <el-table-column prop="templateName" label="模板名称" min-width="180" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="description" label="描述" min-width="200" />
            <el-table-column label="操作" width="100"><template #default="{ row }"><el-button link type="primary" @click="handleDownloadTemplate(row)">下载</el-button></template></el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getDocumentList, deleteDocument, downloadDocument, getTemplateList, downloadTemplate } from '@/api/modules/knowledge'
import PageHeader from '@/components/PageHeader.vue'
import Pagination from '@/components/Pagination.vue'

const activeTab = ref('documents')
const docLoading = ref(false)
const docData = ref<unknown[]>([])
const docTotal = ref(0)
const docPage = ref(1)
const docLimit = ref(10)
const docSearchForm = reactive({ projectId: '', category: '' })

const templateData = ref<unknown[]>([])

const uploadHeaders = computed(() => ({ Authorization: `Bearer ${localStorage.getItem('token')}` }))

async function fetchDocs() {
  docLoading.value = true
  try {
    const res = await getDocumentList({ page: docPage.value, limit: docLimit.value, ...docSearchForm })
    docData.value = res.records; docTotal.value = res.total
  } finally { docLoading.value = false }
}

async function loadTemplates() {
  try { templateData.value = await getTemplateList({}) } catch { templateData.value = [] }
}

function formatSize(bytes: number) {
  if (!bytes) return '-'
  if (bytes > 1048576) return `${(bytes / 1048576).toFixed(1)}MB`
  return `${(bytes / 1024).toFixed(1)}KB`
}

function handleDocSearch() { docPage.value = 1; fetchDocs() }
function handleDocReset() { docSearchForm.projectId = ''; docSearchForm.category = ''; docPage.value = 1; fetchDocs() }
function handleDocPageChange(v: { page: number; limit: number }) { docPage.value = v.page; docLimit.value = v.limit; fetchDocs() }
function handleUploadSuccess() { ElMessage.success('上传成功'); fetchDocs() }

async function handleDownload(row: Record<string, unknown>) {
  try {
    const blob = await downloadDocument(row.documentId as string) as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = row.fileName as string || 'document'
    a.click(); URL.revokeObjectURL(url)
  } catch { /* handled */ }
}

async function handleDeleteDoc(id: string) {
  try { await deleteDocument(id); ElMessage.success('删除成功'); fetchDocs() } catch { /* handled */ }
}

async function handleDownloadTemplate(row: Record<string, unknown>) {
  try {
    const blob = await downloadTemplate(row.templateId as string) as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = row.templateName as string || 'template'
    a.click(); URL.revokeObjectURL(url)
  } catch { /* handled */ }
}

onMounted(() => { fetchDocs(); loadTemplates() })
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.knowledge-base-page {
  max-width: 1400px;
}

.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>

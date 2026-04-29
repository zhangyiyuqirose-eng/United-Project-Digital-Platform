<template>
  <div class="page-container">
    <PageHeader :title="isEdit ? '编辑项目' : '新建项目'" description="创建或编辑项目基本信息" />
    <el-card class="form-card">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" class="form-content">
        <el-form-item label="项目名称" prop="projectName">
          <el-input v-model="form.projectName" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目编号" prop="projectCode">
          <el-input v-model="form.projectCode" placeholder="请输入项目编号" />
        </el-form-item>
        <el-form-item label="项目类型" prop="projectType">
          <el-select v-model="form.projectType" placeholder="请选择">
            <el-option label="研发项目" value="R&D" />
            <el-option label="交付项目" value="DELIVERY" />
            <el-option label="内部项目" value="INTERNAL" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目经理" prop="managerId">
          <el-input v-model="form.managerId" placeholder="请输入项目经理ID" />
        </el-form-item>
        <el-form-item label="开始日期" prop="startDate">
          <el-date-picker v-model="form.startDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期" prop="endDate">
          <el-date-picker v-model="form.endDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="预算金额" prop="budget">
          <el-input-number v-model="form.budget" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="客户" prop="customer">
          <el-input v-model="form.customer" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入项目描述" />
        </el-form-item>
        <el-form-item class="form-actions">
          <el-button type="primary" class="btn-primary" @click="handleSubmit">{{ isEdit ? '更新' : '创建' }}</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { createProject, updateProject, getProjectDetail, type ProjectForm } from '@/api/modules/project'

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()
const isEdit = computed(() => !!route.query.id)

const form = reactive<ProjectForm>({
  projectName: '', projectCode: '', projectType: '', managerId: '',
  startDate: '', endDate: '', budget: 0, customer: '', description: '',
})

const rules = {
  projectName: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  projectCode: [{ required: true, message: '请输入项目编号', trigger: 'blur' }],
  projectType: [{ required: true, message: '请选择项目类型', trigger: 'change' }],
  startDate: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  endDate: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  try {
    if (isEdit.value) {
      await updateProject(route.query.id as string, form)
      ElMessage.success('更新成功')
    } else {
      await createProject(form)
      ElMessage.success('创建成功')
    }
    router.push('/project')
  } catch { /* handled */ }
}

async function loadProject() {
  if (!isEdit.value) return
  try {
    const res = await getProjectDetail(route.query.id as string)
    Object.assign(form, res)
  } catch { /* handled */ }
}

function goBack() { router.push('/project') }

onMounted(loadProject)
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.page-container {
  padding: $spacing-2xl;
  max-width: 1400px;
}

.form-card {
  @include card-base;
}

.form-content {
  max-width: 700px;

  :deep(.el-form-item) {
    margin-bottom: $spacing-xl;
  }

  :deep(.el-input__wrapper),
  :deep(.el-textarea__inner),
  :deep(.el-select__wrapper) {
    border-radius: $radius-lg;
  }
}

.form-actions {
  display: flex;
  gap: $spacing-md;
  margin-top: $spacing-2xl;

  .btn-primary {
    @include button-primary;
    padding: $spacing-md $spacing-2xl;
    font-size: $font-size-base;
  }
}
</style>

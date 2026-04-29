import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ProjectVO } from '@/api/modules/project'
import { getProjectList, getProjectDetail } from '@/api/modules/project'

export const useProjectStore = defineStore('project', () => {
  const currentProject = ref<ProjectVO | null>(null)
  const projectList = ref<ProjectVO[]>([])
  const loading = ref(false)

  async function fetchProjectList(params: { page: number; limit: number; keyword?: string; status?: string }) {
    loading.value = true
    try {
      const res = await getProjectList(params)
      projectList.value = res.records
      return res
    } finally {
      loading.value = false
    }
  }

  async function fetchProjectDetail(projectId: string) {
    loading.value = true
    try {
      currentProject.value = await getProjectDetail(projectId)
    } finally {
      loading.value = false
    }
  }

  function clearCurrentProject() {
    currentProject.value = null
  }

  return {
    currentProject,
    projectList,
    loading,
    fetchProjectList,
    fetchProjectDetail,
    clearCurrentProject,
  }
})

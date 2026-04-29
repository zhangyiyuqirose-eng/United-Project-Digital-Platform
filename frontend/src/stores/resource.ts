import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PersonVO } from '@/api/modules/resource'
import { getPersons } from '@/api/modules/resource'

export const useResourceStore = defineStore('resource', () => {
  const resourceList = ref<PersonVO[]>([])
  const loading = ref(false)

  async function fetchResourcePool(params: { page: number; limit: number; skill?: string; status?: string; keyword?: string }) {
    loading.value = true
    try {
      const res = await getPersons({ page: params.page, size: params.limit, keyword: params.keyword })
      resourceList.value = res.records as PersonVO[]
      return res
    } finally {
      loading.value = false
    }
  }

  return {
    resourceList,
    loading,
    fetchResourcePool,
  }
})

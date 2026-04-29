import request from '@/utils/request'
import type { PageResult } from '@/api/modules/common'

export interface DefectVO {
  defectId: string
  projectId: string
  projectName: string
  title: string
  severity: string
  priority: string
  status: string
  reporter: string
  assignee: string
  description: string
  createTime: string
  resolveTime: string
}

export interface DefectForm {
  projectId: string
  title: string
  severity: string
  priority: string
  assignee: string
  description: string
}

export interface QualityMetricVO {
  metricId: string
  projectId: string
  projectName: string
  metricName: string
  target: number
  actual: number
  status: string
  period: string
}

export function getDefectList(params: { page: number; limit: number; projectId?: string; severity?: string; status?: string }) {
  return request<PageResult<DefectVO>>({ url: '/quality/defect/list', method: 'get', params })
}

export function createDefect(data: DefectForm) {
  return request({ url: '/quality/defect/create', method: 'post', data })
}

export function updateDefect(defectId: string, data: Partial<DefectForm>) {
  return request({ url: `/quality/defect/${defectId}`, method: 'put', data })
}

export function resolveDefect(defectId: string) {
  return request({ url: `/quality/defect/${defectId}/resolve`, method: 'post' })
}

export function getQualityMetrics(params: { projectId?: string; period?: string }) {
  return request<QualityMetricVO[]>({ url: '/quality/metrics', method: 'get', params })
}

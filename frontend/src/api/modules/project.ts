import request from '@/utils/request'
import type { PageResult } from '@/api/modules/common'

export interface ProjectVO {
  projectId: string
  projectName: string
  projectCode: string
  projectType: string
  status: string
  managerId: string
  managerName: string
  departmentName?: string
  startDate: string
  endDate: string
  budget: number
  customer: string
  description: string
  createTime: string
}

export interface ProjectForm {
  projectName: string
  projectCode: string
  projectType: string
  managerId: string
  startDate: string
  endDate: string
  budget: number
  customer: string
  description: string
}

export interface WbsNodeVO {
  wbsId: string
  projectId: string
  name: string
  code: string
  parentId: string
  level: number
  sortOrder: number
}

export interface TaskVO {
  taskId: string
  projectId: string
  taskName: string
  assigneeId: string
  assigneeName: string
  status: string
  priority: string
  startDate: string
  endDate: string
  progress: number
  wbsId: string
}

export interface RiskVO {
  riskId: string
  projectId: string
  riskName: string
  riskType: string
  probability: number
  impact: number
  level: string
  status: string
  mitigation: string
  ownerName: string
}

export interface GanttTaskVO {
  taskId: string
  taskName: string
  startDate: string
  endDate: string
  progress: number
  parentId: string | null
  assigneeName: string
}

// Project CRUD
export function getProjectList(params: { page: number; limit: number; keyword?: string; status?: string }) {
  return request<PageResult<ProjectVO>>({ url: '/project/list', method: 'get', params })
}

export function getProjectDetail(projectId: string) {
  return request<ProjectVO>({ url: `/project/${projectId}`, method: 'get' })
}

export function createProject(data: ProjectForm) {
  return request({ url: '/project/create', method: 'post', data })
}

export function updateProject(projectId: string, data: ProjectForm) {
  return request({ url: `/project/${projectId}`, method: 'put', data })
}

export function deleteProject(projectId: string) {
  return request({ url: `/project/${projectId}`, method: 'delete' })
}

// WBS
export function getWbsTree(projectId: string) {
  return request<WbsNodeVO[]>({ url: `/project/${projectId}/wbs`, method: 'get' })
}

export function createWbsNode(projectId: string, data: { name: string; parentId: string; code: string }) {
  return request({ url: `/project/${projectId}/wbs`, method: 'post', data })
}

// Tasks
export function getProjectTasks(projectId: string) {
  return request<TaskVO[]>({ url: `/project/${projectId}/tasks`, method: 'get' })
}

export function updateTask(taskId: string, data: Partial<TaskVO>) {
  return request({ url: `/project/tasks/${taskId}`, method: 'put', data })
}

// Risks
export function getProjectRisks(projectId: string) {
  return request<RiskVO[]>({ url: `/project/${projectId}/risks`, method: 'get' })
}

export function createRisk(projectId: string, data: Partial<RiskVO>) {
  return request({ url: `/project/${projectId}/risks`, method: 'post', data })
}

export function updateRisk(riskId: string, data: Partial<RiskVO>) {
  return request({ url: `/project/risks/${riskId}`, method: 'put', data })
}

// Gantt
export function getGanttData(projectId: string) {
  return request<GanttTaskVO[]>({ url: `/project/${projectId}/gantt`, method: 'get' })
}

// Pre-initiation
export function getPreInitiationList(projectId: string) {
  return request({ url: `/project/${projectId}/pre-initiation`, method: 'get' })
}

export function submitPreInitiation(projectId: string, data: Record<string, unknown>) {
  return request({ url: `/project/${projectId}/pre-initiation`, method: 'post', data })
}

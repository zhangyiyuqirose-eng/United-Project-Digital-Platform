import request from '@/utils/request'
import type { PageResult } from '@/api/modules/common'

export interface ProcessInstanceVO {
  instanceId: string
  processKey: string
  processName: string
  businessKey: string
  status: string
  initiator: string
  createTime: string
  endTime: string
}

export interface ApprovalTaskVO {
  taskId: string
  instanceId: string
  processName: string
  taskName: string
  assignee: string
  businessKey: string
  createTime: string
  status: string
}

export interface ProcessHistoryVO {
  historyId: string
  instanceId: string
  processName: string
  activityName: string
  assignee: string
  action: string
  comment: string
  createTime: string
}

export function startProcess(data: { processKey: string; businessKey: string; variables?: Record<string, unknown> }) {
  return request({ url: '/workflow/start', method: 'post', data })
}

export function getProcessStatus(instanceId: string) {
  return request<ProcessInstanceVO>({ url: `/workflow/status/${instanceId}`, method: 'get' })
}

export function getMyTasks(params: { page: number; limit: number; status?: string }) {
  return request<PageResult<ApprovalTaskVO>>({ url: '/workflow/my-tasks', method: 'get', params })
}

export function approveTask(taskId: string, comment: string) {
  return request({ url: `/workflow/tasks/${taskId}/approve`, method: 'post', data: { comment } })
}

export function rejectTask(taskId: string, reason: string) {
  return request({ url: `/workflow/tasks/${taskId}/reject`, method: 'post', data: { reason } })
}

export function getProcessHistory(instanceId: string) {
  return request<ProcessHistoryVO[]>({ url: `/workflow/history/${instanceId}`, method: 'get' })
}

export function getMyInitiatedProcesses(params: { page: number; limit: number }) {
  return request<PageResult<ProcessInstanceVO>>({ url: '/workflow/my-processes', method: 'get', params })
}

import request from '@/utils/request'
import type { PageResult } from '@/api/modules/common'

export interface TimesheetVO {
  timesheetId: string
  userId: string
  userName: string
  projectId: string
  projectName: string
  date: string
  hours: number
  workContent: string
  status: string
  createTime: string
}

export interface TimesheetForm {
  projectId: string
  date: string
  hours: number
  workContent: string
}

export interface TimesheetApprovalVO {
  approvalId: string
  timesheetId: string
  userName: string
  projectName: string
  date: string
  hours: number
  status: string
  submitTime: string
}

export interface WorkReportVO {
  reportId: string
  userId: string
  userName: string
  weekStart: string
  weekEnd: string
  content: string
  nextPlan: string
  issues: string
  status: string
  createTime: string
}

export function getTimesheetList(params: { page: number; limit: number; projectId?: string; status?: string; dateFrom?: string; dateTo?: string }) {
  return request<PageResult<TimesheetVO>>({ url: '/timesheet/list', method: 'get', params })
}

export function createTimesheet(data: TimesheetForm) {
  return request({ url: '/timesheet/create', method: 'post', data })
}

export function updateTimesheet(timesheetId: string, data: TimesheetForm) {
  return request({ url: `/timesheet/${timesheetId}`, method: 'put', data })
}

export function deleteTimesheet(timesheetId: string) {
  return request({ url: `/timesheet/${timesheetId}`, method: 'delete' })
}

export function submitTimesheet(timesheetId: string) {
  return request({ url: `/timesheet/${timesheetId}/submit`, method: 'post' })
}

export function getApprovalQueue(params: { page: number; limit: number; status?: string }) {
  return request<PageResult<TimesheetApprovalVO>>({ url: '/timesheet/approvals', method: 'get', params })
}

export function approveTimesheet(approvalId: string, comment: string) {
  return request({ url: `/timesheet/approvals/${approvalId}/approve`, method: 'post', data: { comment } })
}

export function rejectTimesheet(approvalId: string, reason: string) {
  return request({ url: `/timesheet/approvals/${approvalId}/reject`, method: 'post', data: { reason } })
}

export function getWorkReports(params: { page: number; limit: number; userId?: string }) {
  return request<PageResult<WorkReportVO>>({ url: '/timesheet/reports', method: 'get', params })
}

export function createWorkReport(data: Partial<WorkReportVO>) {
  return request({ url: '/timesheet/reports', method: 'post', data })
}

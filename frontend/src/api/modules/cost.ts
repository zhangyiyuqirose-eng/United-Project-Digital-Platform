import request from '@/utils/request'
import type { PageResult } from '@/api/modules/common'

export interface BudgetVO {
  budgetId: string
  projectId: string
  projectName: string
  category: string
  plannedAmount: number
  actualAmount: number
  committedAmount: number
  status: string
  year: number
}

export interface BudgetForm {
  projectId: string
  category: string
  plannedAmount: number
  year: number
}

export interface CostAlertVO {
  alertId: string
  projectId: string
  projectName: string
  alertType: string
  severity: string
  message: string
  threshold: number
  currentValue: number
  createTime: string
}

export interface EvmDataVO {
  month: string
  pv: number
  ev: number
  ac: number
  cpi: number
  spi: number
}

export function getBudgetList(params: { page: number; limit: number; projectId?: string; year?: number }) {
  return request<PageResult<BudgetVO>>({ url: '/cost/budget/list', method: 'get', params })
}

export function createBudget(data: BudgetForm) {
  return request({ url: '/cost/budget/create', method: 'post', data })
}

export function updateBudget(budgetId: string, data: BudgetForm) {
  return request({ url: `/cost/budget/${budgetId}`, method: 'put', data })
}

export function deleteBudget(budgetId: string) {
  return request({ url: `/cost/budget/${budgetId}`, method: 'delete' })
}

export function getCostDashboard(projectId?: string) {
  return request<{ totalBudget: number; totalSpent: number; alerts: number; evm: EvmDataVO[] }>({
    url: '/cost/dashboard',
    method: 'get',
    params: { projectId },
  })
}

export function getCostAlerts(params: { page: number; limit: number; projectId?: string; severity?: string }) {
  return request<PageResult<CostAlertVO>>({ url: '/cost/alerts', method: 'get', params })
}

export function getEvmData(projectId: string) {
  return request<EvmDataVO[]>({ url: `/cost/evm/${projectId}`, method: 'get' })
}

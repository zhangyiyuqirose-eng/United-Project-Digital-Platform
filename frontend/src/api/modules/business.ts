import request from '@/utils/request'
import type { PageResult } from '@/api/modules/common'

export interface ContractVO {
  contractId: string
  contractCode: string
  contractName: string
  contractType: string
  projectId: string
  projectName: string
  counterparty: string
  amount: number
  signDate: string
  status: string
  attachments: string
}

export interface ContractForm {
  contractName: string
  contractType: string
  projectId: string
  counterparty: string
  amount: number
  signDate: string
  description: string
}

export interface PaymentVO {
  paymentId: string
  contractId: string
  contractName: string
  phase: string
  amount: number
  plannedDate: string
  actualDate: string
  status: string
  remark: string
}

export interface SupplierVO {
  supplierId: string
  supplierName: string
  supplierCode: string
  contactPerson: string
  contactPhone: string
  contactEmail: string
  address: string
  category: string
  rating: string
  status: string
}

export interface SupplierForm {
  supplierName: string
  contactPerson: string
  contactPhone: string
  contactEmail: string
  address: string
  category: string
}

// Contracts
export function getContractList(params: { page: number; limit: number; keyword?: string; type?: string; status?: string }) {
  return request<PageResult<ContractVO>>({ url: '/business/contract/list', method: 'get', params })
}

export function createContract(data: ContractForm) {
  return request({ url: '/business/contract/create', method: 'post', data })
}

export function updateContract(contractId: string, data: ContractForm) {
  return request({ url: `/business/contract/${contractId}`, method: 'put', data })
}

export function deleteContract(contractId: string) {
  return request({ url: `/business/contract/${contractId}`, method: 'delete' })
}

// Payments
export function getPaymentList(params: { page: number; limit: number; contractId?: string; status?: string }) {
  return request<PageResult<PaymentVO>>({ url: '/business/payment/list', method: 'get', params })
}

export function createPayment(data: Partial<PaymentVO>) {
  return request({ url: '/business/payment/create', method: 'post', data })
}

export function updatePayment(paymentId: string, data: Partial<PaymentVO>) {
  return request({ url: `/business/payment/${paymentId}`, method: 'put', data })
}

export function confirmPayment(paymentId: string) {
  return request({ url: `/business/payment/${paymentId}/confirm`, method: 'post' })
}

// Suppliers
export function getSupplierList(params: { page: number; limit: number; keyword?: string; category?: string; status?: string }) {
  return request<PageResult<SupplierVO>>({ url: '/business/supplier/list', method: 'get', params })
}

export function createSupplier(data: SupplierForm) {
  return request({ url: '/business/supplier/create', method: 'post', data })
}

export function updateSupplier(supplierId: string, data: SupplierForm) {
  return request({ url: `/business/supplier/${supplierId}`, method: 'put', data })
}

export function deleteSupplier(supplierId: string) {
  return request({ url: `/business/supplier/${supplierId}`, method: 'delete' })
}

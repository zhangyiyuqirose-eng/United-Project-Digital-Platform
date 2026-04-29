import request from '@/utils/request'
import type { PageResult } from '@/api/modules/common'

export interface DocumentVO {
  documentId: string
  title: string
  category: string
  projectId: string
  projectName: string
  uploader: string
  fileSize: number
  fileType: string
  uploadTime: string
  downloadCount: number
}

export interface TemplateVO {
  templateId: string
  templateName: string
  category: string
  description: string
  fileType: string
  uploadTime: string
}

export function getDocumentList(params: { page: number; limit: number; projectId?: string; category?: string; keyword?: string }) {
  return request<PageResult<DocumentVO>>({ url: '/knowledge/document/list', method: 'get', params })
}

export function uploadDocument(data: FormData) {
  return request({ url: '/knowledge/document/upload', method: 'post', data, headers: { 'Content-Type': 'multipart/form-data' } })
}

export function deleteDocument(documentId: string) {
  return request({ url: `/knowledge/document/${documentId}`, method: 'delete' })
}

export function downloadDocument(documentId: string) {
  return request({ url: `/knowledge/document/${documentId}/download`, method: 'get', responseType: 'blob' })
}

export function getTemplateList(params: { category?: string }) {
  return request<TemplateVO[]>({ url: '/knowledge/template/list', method: 'get', params })
}

export function downloadTemplate(templateId: string) {
  return request({ url: `/knowledge/template/${templateId}/download`, method: 'get', responseType: 'blob' })
}

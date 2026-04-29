import request from '@/utils/request'

export interface FileVO {
  fileId: string
  fileName: string
  originalName: string
  fileSize: number
  fileType: string
  fileUrl: string
  uploadTime: string
  uploader: string
}

export function uploadFile(data: FormData) {
  return request({ url: '/file/upload', method: 'post', data, headers: { 'Content-Type': 'multipart/form-data' } })
}

export function downloadFile(fileId: string) {
  return request({ url: `/file/download/${fileId}`, method: 'get', responseType: 'blob' })
}

export function getFileList(params: { page: number; limit: number; keyword?: string }) {
  return request({ url: '/file/list', method: 'get', params })
}

export function deleteFile(fileId: string) {
  return request({ url: `/file/${fileId}`, method: 'delete' })
}

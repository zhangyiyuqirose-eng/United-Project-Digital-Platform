import request from '@/utils/request'
import type { PageResult } from '@/api/modules/common'

export interface UserVO {
  userId: string
  username: string
  name: string
  deptId: string
  deptName: string
  status: number
  createTime: string
}

export interface RoleVO {
  roleId: string
  roleName: string
  roleCode: string
  description: string
  status: number
}

export interface PermissionVO {
  permissionId: string
  permissionName: string
  permissionCode: string
  type: string
  parentId: string
}

export interface DeptVO {
  deptId: string
  deptName: string
  parentId: string
  sort: number
  status: number
}

export interface AnnouncementVO {
  announcementId: string
  title: string
  content: string
  type: string
  publisher: string
  publishTime: string
  status: number
}

export interface UserForm {
  username: string
  name: string
  deptId: string
  password: string
  phone: string
  email: string
  roleIds: string[]
  status: number
}

export interface RoleForm {
  roleName: string
  roleCode: string
  description: string
  permissionIds: string[]
  status: number
}

export interface DeptForm {
  deptName: string
  parentId: string
  sort: number
  status: number
}

export interface AnnouncementForm {
  title: string
  content: string
  type: string
}

export interface LoginRequest {
  username: string
  password: string
  captchaKey?: string
  captchaCode?: string
}

export interface LoginResult {
  token: string
  refreshToken: string
  userInfo: {
    userId: string
    username: string
    name: string
    deptId: string
    email: string
    phone: string
  }
}

export interface UserInfoVO {
  userId: string
  username: string
  name: string
  deptId: string
  deptName: string
  roles: string[]
  permissions: string[]
  avatar: string
  phone: string
  email: string
  status: number
}

// Auth
export function login(data: LoginRequest) {
  return request<LoginResult>({ url: '/system/auth/login', method: 'post', data })
}

export function getUserInfo() {
  return request<UserInfoVO>({ url: '/system/auth/info', method: 'get' })
}

export function logout() {
  return request({ url: '/system/auth/logout', method: 'post' })
}

export function getCaptcha() {
  return request({ url: '/system/auth/captcha', method: 'get' })
}

// Users
export function getUserList(params: { page: number; limit: number; keyword?: string; deptId?: string; status?: number }) {
  return request<PageResult<UserVO>>({ url: '/system/user/list', method: 'get', params })
}

export function createUser(data: UserForm) {
  return request({ url: '/system/user/create', method: 'post', data })
}

export function updateUser(userId: string, data: UserForm) {
  return request({ url: `/system/user/${userId}`, method: 'put', data })
}

export function deleteUser(userId: string) {
  return request({ url: `/system/user/${userId}`, method: 'delete' })
}

export function assignRoles(userId: string, roleIds: string[]) {
  return request({ url: `/system/user/${userId}/roles`, method: 'put', data: { roleIds } })
}

// Roles
export function getRoleList(params: { page: number; limit: number; keyword?: string }) {
  return request<PageResult<RoleVO>>({ url: '/system/role/list', method: 'get', params })
}

export function getAllRoles() {
  return request<RoleVO[]>({ url: '/system/role/all', method: 'get' })
}

export function createRole(data: RoleForm) {
  return request({ url: '/system/role/create', method: 'post', data })
}

export function updateRole(roleId: string, data: RoleForm) {
  return request({ url: `/system/role/${roleId}`, method: 'put', data })
}

export function deleteRole(roleId: string) {
  return request({ url: `/system/role/${roleId}`, method: 'delete' })
}

export function assignPermissions(roleId: string, permissionIds: string[]) {
  return request({ url: `/system/role/${roleId}/permissions`, method: 'put', data: { permissionIds } })
}

// Permissions
export function getPermissionTree() {
  return request<PermissionVO[]>({ url: '/system/permission/tree', method: 'get' })
}

export function getPermissionsByRole(roleId: string) {
  return request<PermissionVO[]>({ url: `/system/permission/role/${roleId}`, method: 'get' })
}

export function createPermission(data: Partial<PermissionVO>) {
  return request({ url: '/system/permission/create', method: 'post', data })
}

export function updatePermission(permissionId: string, data: Partial<PermissionVO>) {
  return request({ url: `/system/permission/${permissionId}`, method: 'put', data })
}

export function deletePermission(permissionId: string) {
  return request({ url: `/system/permission/${permissionId}`, method: 'delete' })
}

// Departments
export function getDeptTree() {
  return request<DeptVO[]>({ url: '/system/dept/tree', method: 'get' })
}

export function createDept(data: DeptForm) {
  return request({ url: '/system/dept/create', method: 'post', data })
}

export function updateDept(deptId: string, data: DeptForm) {
  return request({ url: `/system/dept/${deptId}`, method: 'put', data })
}

export function deleteDept(deptId: string) {
  return request({ url: `/system/dept/${deptId}`, method: 'delete' })
}

// Announcements
export function getAnnouncementList(params: { page: number; limit: number; type?: string; keyword?: string }) {
  return request<PageResult<AnnouncementVO>>({ url: '/system/announcement/list', method: 'get', params })
}

export function createAnnouncement(data: AnnouncementForm) {
  return request({ url: '/system/announcement/create', method: 'post', data })
}

export function updateAnnouncement(id: string, data: AnnouncementForm) {
  return request({ url: `/system/announcement/${id}`, method: 'put', data })
}

export function deleteAnnouncement(id: string) {
  return request({ url: `/system/announcement/${id}`, method: 'delete' })
}

export function publishAnnouncement(id: string) {
  return request({ url: `/system/announcement/${id}/publish`, method: 'post' })
}

import request from '@/utils/request'
import type { PageResult } from '@/api/modules/common'

// ── Person (F-501) ───────────────────────────────────────────────────

export interface PersonVO {
  personId: string
  empCode: string
  name: string
  phone: string | null
  email: string | null
  skillTags: string[]
  level: number  // 1:初级 2:中级 3:高级 4:专家
  dailyRate: number
  department: string | null
  poolStatus: number  // 0:可用 1:已分配 2:已退场
  currentProject: string | null
  entryDate: string | null
  exitDate: string | null
  backgroundCheck: number | null
  securityReview: number | null
  confidentialityAgreement: number | null
  attendanceGroup: string | null
  skills?: SkillVO[]
}

export interface SkillVO {
  skillId: string
  skillName: string
  proficiency: number  // 1:入门 2:熟练 3:精通
  certName: string | null
  certDate: string | null
  expiryDate: string | null
}

export interface PersonListParams {
  page: number
  size: number
  keyword?: string
  level?: number
  pool_status?: number
  department?: string
}

export function getPersons(params: PersonListParams) {
  return request<PageResult<PersonVO>>({
    url: '/resource/persons',
    method: 'get',
    params,
  })
}

export function getPersonDetail(personId: string) {
  return request<PersonVO>({
    url: `/resource/person/${personId}`,
    method: 'get',
  })
}

export function createPerson(data: {
  empCode: string
  name: string
  level: number
  dailyRate: number
  department?: string
  skillTags?: string[]
  phone?: string
  email?: string
  attendanceGroup?: string
}) {
  return request<{ personId: string }>({
    url: '/resource/persons',
    method: 'post',
    data,
  })
}

export function updatePerson(personId: string, data: Partial<PersonVO>) {
  return request({
    url: `/resource/person/${personId}`,
    method: 'put',
    data,
  })
}

export function deletePerson(personId: string) {
  return request({
    url: `/resource/person/${personId}`,
    method: 'delete',
  })
}

// ── Skills (F-502) ───────────────────────────────────────────────────

export function getPersonSkills(personId: string) {
  return request<SkillVO[]>({
    url: `/resource/skills/${personId}`,
    method: 'get',
  })
}

export function searchSkills(q: string) {
  return request<SkillVO[]>({
    url: '/resource/skills/search',
    method: 'get',
    params: { q },
  })
}

export function createSkill(data: {
  personId: string
  skillName: string
  proficiency: number
  certName?: string
  certDate?: string
  expiryDate?: string
}) {
  return request<{ skillId: string }>({
    url: '/resource/skills',
    method: 'post',
    data,
  })
}

// ── Pool Positions (F-503) ───────────────────────────────────────────

export interface PositionVO {
  positionId: string
  poolId: string
  positionName: string
  level: number
  skillRequirements: string[] | null
  headCount: number
  filledCount: number
  department: string | null
  status: number
}

export function getPositions(poolId?: string) {
  return request<PositionVO[]>({
    url: '/resource/positions',
    method: 'get',
    params: poolId ? { pool_id: poolId } : undefined,
  })
}

// ── Entry / Exit (F-504 / F-511) ────────────────────────────────────

export function applyEntry(personId: string, data: { poolId: string; attendanceGroup?: string }) {
  return request<{ membershipId: string }>({
    url: `/resource/person/${personId}/entry`,
    method: 'post',
    data,
  })
}

export function approveEntry(personId: string, data: { approverId: string }) {
  return request({
    url: `/resource/person/${personId}/entry/approve`,
    method: 'post',
    data,
  })
}

export function applyExit(personId: string, data: { exitDate?: string }) {
  return request<{ membershipId: string }>({
    url: `/resource/person/${personId}/exit`,
    method: 'post',
    data,
  })
}

export function approveExit(personId: string, data: { approverId: string }) {
  return request({
    url: `/resource/person/${personId}/exit/approve`,
    method: 'post',
    data,
  })
}

export interface PendingEntryExitVO {
  membershipId: string
  personId: string
  personName?: string
  department?: string
  type: number  // 0:入场申请 1:退场申请
  applyDate: string
  expectedDate?: string
  status: number  // 0:待审批 1:已通过 2:已拒绝
}

export function getPendingEntryExit() {
  return request<PendingEntryExitVO[]>({
    url: '/resource/entry-exit/pending',
    method: 'get',
  })
}

// ── Skill Match (F-505) ─────────────────────────────────────────────

export interface MatchResultVO {
  personId: string
  name: string
  score: number
  skillMatch: number
  expMatch: number
  perfMatch: number
  idleMatch: number
  level: number
  dailyRate: number
}

export function matchCandidates(data: {
  positionId?: string
  skillRequirements?: string[]
  experienceMin?: number
}) {
  return request<MatchResultVO[]>({
    url: '/resource/match',
    method: 'post',
    data,
  })
}

// ── Attendance (F-506) ──────────────────────────────────────────────

export function attendanceCheckIn(data: {
  personId: string
  gpsLat?: number
  gpsLng?: number
  wifiMac?: string
  projectId?: string
}) {
  return request<{ attendanceId: string }>({
    url: '/resource/attendance/checkin',
    method: 'post',
    data,
  })
}

export function attendanceCheckOut(data: {
  personId: string
  gpsLat?: number
  gpsLng?: number
  wifiMac?: string
  projectId?: string
}) {
  return request<{ attendanceId: string }>({
    url: '/resource/attendance/checkout',
    method: 'post',
    data,
  })
}

export interface AttendanceCalendarVO {
  date: string
  checkIn: string | null
  checkOut: string | null
  status: number
}

export function getAttendanceCalendar(personId: string, month: string) {
  return request<AttendanceCalendarVO[]>({
    url: `/resource/attendance/calendar/${personId}/${month}`,
    method: 'get',
  })
}

export interface AttendanceExceptionVO {
  exceptionId: string
  personId: string
  personName?: string
  department?: string
  date: string
  type: number  // 0:缺卡 1:迟到 2:早退 3:异常签退
  description?: string
  status: number  // 0:未处理 1:已处理
}

export function getAttendanceExceptions(month?: string) {
  return request<AttendanceExceptionVO[]>({
    url: '/resource/attendance/exceptions',
    method: 'get',
    params: month ? { month } : undefined,
  })
}

// ── Settlement (F-508 / F-509) ──────────────────────────────────────

export interface SettlementVO {
  settlementId: string
  personId: string
  personName?: string
  period: string
  validHours: number | null
  standardHours: number | null
  dailyRate: number | null
  performanceCoeff: number | null
  overtimeHours: number | null
  overtimeFee: number | null
  totalAmount: number | null
  status: number  // 0:草稿 1:待确认 2:已确认 3:已开票
  confirmedBy: string | null
  confirmedDate: string | null
  invoiceDate: string | null
}

export function generateSettlement(period: string) {
  return request<{ count: number }>({
    url: `/resource/settlement/generate/${period}`,
    method: 'post',
  })
}

export function getSettlements(params: { period?: string; status?: number }) {
  return request<SettlementVO[]>({
    url: '/resource/settlements',
    method: 'get',
    params,
  })
}

export function confirmSettlement(settlementId: string, data: { confirmedBy: string }) {
  return request({
    url: `/resource/settlement/${settlementId}/confirm`,
    method: 'put',
    data,
  })
}

export function rejectSettlement(settlementId: string, data: { reason?: string }) {
  return request({
    url: `/resource/settlement/${settlementId}/reject`,
    method: 'put',
    data,
  })
}

// ── Performance (F-510) ─────────────────────────────────────────────

export interface PerformanceEvalVO {
  evalId: string
  personId: string
  personName?: string
  projectId: string | null
  period: string | null
  pmSatisfaction: number | null
  timesheetCompliance: number | null
  taskCompletion: number | null
  qualityMetric: number | null
  attendanceCompliance: number | null
  overallScore: number | null
  grade: string | null
  evaluatorId: string | null
  comments: string | null
  createTime: string | null
}

export function evaluatePerson(personId: string, period: string, data: {
  pmSatisfaction: number
  timesheetCompliance: number
  taskCompletion: number
  qualityMetric: number
  attendanceCompliance: number
  evaluatorId?: string
  projectId?: string
  comments?: string
}) {
  return request<{ evalId: string }>({
    url: `/resource/performance/evaluate/${personId}/${period}`,
    method: 'post',
    data,
  })
}

export function getPerformanceHistory(personId: string) {
  return request<PerformanceEvalVO[]>({
    url: `/resource/performance/${personId}/history`,
    method: 'get',
  })
}

// ── Utilization (F-512) ─────────────────────────────────────────────

export interface UtilizationVO {
  personId: string
  name: string
  utilizationRate: number
  billableHours: number
  totalHours: number
  status: string
}

export function getUtilizationWarnings() {
  return request<UtilizationVO[]>({
    url: '/resource/utilization/warnings',
    method: 'get',
  })
}

export interface DepartmentUtilizationVO {
  department: string
  headCount: number
  billableCount: number
  idleCount: number
  utilizationRate: number
  billableHours: number
  totalHours: number
}

export function getUtilizationByDepartment() {
  return request<DepartmentUtilizationVO[]>({
    url: '/resource/utilization/department',
    method: 'get',
  })
}

// ── Reports (F-513) ─────────────────────────────────────────────────

export interface EfficiencyReportVO {
  period?: string
  totalPersons: number
  avgUtilizationRate: number
  avgPerformanceScore: number
  totalBillableHours: number
  totalOvertimeHours: number
  personsOnBench: number
  departmentBreakdown?: DepartmentEfficiencyItem[]
}

export interface DepartmentEfficiencyItem {
  department: string
  headCount: number
  avgUtilizationRate: number
  avgPerformanceScore: number
}

export function getEfficiencyReport(params: { start?: string; end?: string }) {
  return request<EfficiencyReportVO>({
    url: '/resource/reports/efficiency',
    method: 'get',
    params,
  })
}

export interface CostReportVO {
  period?: string
  totalCost: number
  avgDailyRate: number
  totalSettlements: number
  invoicedAmount: number
  uninvoicedAmount: number
  departmentBreakdown?: DepartmentCostItem[]
}

export interface DepartmentCostItem {
  department: string
  headCount: number
  totalCost: number
  avgDailyRate: number
}

export function getCostReport(params: { period?: string }) {
  return request<CostReportVO>({
    url: '/resource/reports/cost',
    method: 'get',
    params,
  })
}

// ── Performance Evaluation (legacy page compatibility) ──────────────

export function getPerformanceEvalList(params: { page: number; limit: number; projectId?: string }) {
  return request<PageResult<PerformanceEvalVO>>({
    url: '/resource/performance/list',
    method: 'get',
    params,
  })
}

export function createPerformanceEval(data: Partial<PerformanceEvalVO>) {
  return request<{ evalId: string }>({
    url: '/resource/performance/evaluate',
    method: 'post',
    data,
  })
}

export function updatePerformanceEval(evalId: string, data: Partial<PerformanceEvalVO>) {
  return request({
    url: `/resource/performance/${evalId}`,
    method: 'put',
    data,
  })
}

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { cancelAllPending } from '@/utils/request'

const WHITE_LIST = ['/login']

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import(/* webpackChunkName: "auth" */ '@/pages/auth/Login.vue'),
  },
  {
    path: '/',
    component: () => import(/* webpackChunkName: "main-layout" */ '@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import(/* webpackChunkName: "dashboard" */ '@/pages/project/Dashboard.vue'),
        meta: { title: '个人工作台', transition: 'page-fade' },
      },
      // Project
      {
        path: 'project',
        name: 'ProjectList',
        component: () => import(/* webpackChunkName: "project" */ '@/pages/project/ProjectList.vue'),
        meta: { title: '项目列表', transition: 'page-fade' },
      },
      {
        path: 'project/create',
        name: 'ProjectCreate',
        component: () => import(/* webpackChunkName: "project" */ '@/pages/project/ProjectCreate.vue'),
        meta: { title: '新建项目', transition: 'page-fade' },
      },
      {
        path: 'project/:id',
        name: 'ProjectDetail',
        component: () => import(/* webpackChunkName: "project" */ '@/pages/project/ProjectDetail.vue'),
        meta: { title: '项目详情', transition: 'page-fade' },
      },
      // Cost
      {
        path: 'cost',
        name: 'CostDashboard',
        component: () => import(/* webpackChunkName: "cost" */ '@/pages/cost/CostDashboard.vue'),
        meta: { title: '成本看板', transition: 'page-fade' },
      },
      {
        path: 'cost/budget',
        name: 'BudgetManagement',
        component: () => import(/* webpackChunkName: "cost" */ '@/pages/cost/BudgetManagement.vue'),
        meta: { title: '预算管理', transition: 'page-fade' },
      },
      // Timesheet
      {
        path: 'timesheet',
        name: 'TimesheetList',
        component: () => import(/* webpackChunkName: "timesheet" */ '@/pages/timesheet/TimesheetList.vue'),
        meta: { title: '工时管理', transition: 'page-fade' },
      },
      // Resource
      {
        path: 'resource',
        name: 'ResourcePool',
        component: () => import(/* webpackChunkName: "resource" */ '@/pages/resource/ResourcePool.vue'),
        meta: { title: '资源池', transition: 'page-fade' },
      },
      {
        path: 'resource/performance',
        name: 'PerformanceEval',
        component: () => import(/* webpackChunkName: "resource" */ '@/pages/resource/PerformanceEval.vue'),
        meta: { title: '绩效评估', transition: 'page-fade' },
      },
      // Business
      {
        path: 'business/contract',
        name: 'ContractList',
        component: () => import(/* webpackChunkName: "business" */ '@/pages/business/ContractList.vue'),
        meta: { title: '合同管理', transition: 'page-fade' },
      },
      {
        path: 'business/payment',
        name: 'PaymentList',
        component: () => import(/* webpackChunkName: "business" */ '@/pages/business/PaymentList.vue'),
        meta: { title: '付款管理', transition: 'page-fade' },
      },
      {
        path: 'business/supplier',
        name: 'SupplierList',
        component: () => import(/* webpackChunkName: "business" */ '@/pages/business/SupplierList.vue'),
        meta: { title: '供应商管理', transition: 'page-fade' },
      },
      // Workflow
      {
        path: 'workflow/tasks',
        name: 'MyTasks',
        component: () => import(/* webpackChunkName: "workflow" */ '@/pages/workflow/MyTasks.vue'),
        meta: { title: '我的待办', transition: 'page-fade' },
      },
      {
        path: 'workflow/history',
        name: 'ProcessHistory',
        component: () => import(/* webpackChunkName: "workflow" */ '@/pages/workflow/ProcessHistory.vue'),
        meta: { title: '流程历史', transition: 'page-fade' },
      },
      // Quality
      {
        path: 'quality',
        name: 'QualityManagement',
        component: () => import(/* webpackChunkName: "quality" */ '@/pages/quality/QualityManagement.vue'),
        meta: { title: '质量管理', transition: 'page-fade' },
      },
      // Knowledge
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: () => import(/* webpackChunkName: "knowledge" */ '@/pages/knowledge/KnowledgeBase.vue'),
        meta: { title: '知识库', transition: 'page-fade' },
      },
      // System
      {
        path: 'system/users',
        name: 'UserManagement',
        component: () => import(/* webpackChunkName: "system" */ '@/pages/system/UserManagement.vue'),
        meta: { title: '用户管理', transition: 'page-fade' },
      },
      {
        path: 'system/roles',
        name: 'RoleManagement',
        component: () => import(/* webpackChunkName: "system" */ '@/pages/system/RoleManagement.vue'),
        meta: { title: '角色管理', transition: 'page-fade' },
      },
      {
        path: 'system/departments',
        name: 'DeptManagement',
        component: () => import(/* webpackChunkName: "system" */ '@/pages/system/DeptManagement.vue'),
        meta: { title: '部门管理', transition: 'page-fade' },
      },
      {
        path: 'system/announcements',
        name: 'AnnouncementList',
        component: () => import(/* webpackChunkName: "system" */ '@/pages/system/AnnouncementList.vue'),
        meta: { title: '公告管理', transition: 'page-fade' },
      },
      {
        path: 'system/permissions',
        name: 'PermissionManagement',
        component: () => import(/* webpackChunkName: "system" */ '@/pages/system/PermissionManagement.vue'),
        meta: { title: '权限管理', transition: 'page-fade' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  cancelAllPending()

  const authStore = useAuthStore()

  if (authStore.isLoggedIn) {
    if (to.path === '/login') {
      next('/dashboard')
      return
    }
    next()
    return
  }

  if (WHITE_LIST.includes(to.path)) {
    next()
    return
  }

  next('/login')
})

export default router

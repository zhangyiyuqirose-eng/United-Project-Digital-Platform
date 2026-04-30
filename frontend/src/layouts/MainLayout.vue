<template>
  <div class="main-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: uiStore.sidebarCollapsed }">
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-icon">
          <el-icon :size="28" color="#fff"><Menu /></el-icon>
        </div>
        <div class="logo-text" v-show="!uiStore.sidebarCollapsed">
          <span class="logo-title">UPDG</span>
          <span class="logo-subtitle">数字化运营平台</span>
        </div>
      </div>

      <!-- Toggle Button (顶部位置) -->
      <button class="sidebar-toggle" @click="uiStore.toggleSidebar">
        <el-icon :size="16">
          <DArrowLeft v-if="!uiStore.sidebarCollapsed" />
          <DArrowRight v-else />
        </el-icon>
      </button>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <!-- Dashboard (个人工作台) - 无二级菜单 -->
        <div class="nav-item" :class="{ active: activeMenu === '/dashboard' }" @click="navigateTo('/dashboard')">
          <el-icon :size="18"><Odometer /></el-icon>
          <span class="nav-text">个人工作台</span>
          <div class="nav-indicator" v-if="activeMenu === '/dashboard'" />
        </div>

        <!-- 项目管理 - 可折叠 -->
        <div class="nav-group-wrapper" :class="{ expanded: isMenuExpanded('project') }">
          <div class="nav-item nav-parent" :class="{ active: activeMenu.startsWith('/project') }" @click="toggleMenu('project')">
            <el-icon :size="18"><FolderOpened /></el-icon>
            <span class="nav-text">项目管理</span>
            <el-icon :size="14" class="nav-expand-icon" v-show="!uiStore.sidebarCollapsed">
              <ArrowDown v-if="isMenuExpanded('project')" />
              <ArrowRight v-else />
            </el-icon>
          </div>
          <Transition name="submenu">
            <div class="nav-submenu" v-show="isMenuExpanded('project') && !uiStore.sidebarCollapsed">
              <div class="nav-sub-item" :class="{ active: activeMenu === '/project' }" @click.stop="navigateTo('/project')">
                <span>项目列表</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/project/create' }" @click.stop="navigateTo('/project/create')">
                <span>新建项目</span>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 成本管理 - 可折叠 -->
        <div class="nav-group-wrapper" :class="{ expanded: isMenuExpanded('cost') }">
          <div class="nav-item nav-parent" :class="{ active: activeMenu.startsWith('/cost') }" @click="toggleMenu('cost')">
            <el-icon :size="18"><Money /></el-icon>
            <span class="nav-text">成本管理</span>
            <el-icon :size="14" class="nav-expand-icon" v-show="!uiStore.sidebarCollapsed">
              <ArrowDown v-if="isMenuExpanded('cost')" />
              <ArrowRight v-else />
            </el-icon>
          </div>
          <Transition name="submenu">
            <div class="nav-submenu" v-show="isMenuExpanded('cost') && !uiStore.sidebarCollapsed">
              <div class="nav-sub-item" :class="{ active: activeMenu === '/cost' }" @click.stop="navigateTo('/cost')">
                <span>成本看板</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/cost/budget' }" @click.stop="navigateTo('/cost/budget')">
                <span>预算管理</span>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 工时管理 - 可折叠 -->
        <div class="nav-group-wrapper" :class="{ expanded: isMenuExpanded('timesheet') }">
          <div class="nav-item nav-parent" :class="{ active: activeMenu.startsWith('/timesheet') }" @click="toggleMenu('timesheet')">
            <el-icon :size="18"><Clock /></el-icon>
            <span class="nav-text">工时管理</span>
            <el-icon :size="14" class="nav-expand-icon" v-show="!uiStore.sidebarCollapsed">
              <ArrowDown v-if="isMenuExpanded('timesheet')" />
              <ArrowRight v-else />
            </el-icon>
          </div>
          <Transition name="submenu">
            <div class="nav-submenu" v-show="isMenuExpanded('timesheet') && !uiStore.sidebarCollapsed">
              <div class="nav-sub-item" :class="{ active: activeMenu === '/timesheet' }" @click.stop="navigateTo('/timesheet')">
                <span>工时填报</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu.startsWith('/timesheet/approval') }" @click.stop="navigateTo('/timesheet')">
                <span>工时审批</span>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 资源池 - 可折叠 -->
        <div class="nav-group-wrapper" :class="{ expanded: isMenuExpanded('resource') }">
          <div class="nav-item nav-parent" :class="{ active: activeMenu.startsWith('/resource') }" @click="toggleMenu('resource')">
            <el-icon :size="18"><UserFilled /></el-icon>
            <span class="nav-text">资源池</span>
            <el-icon :size="14" class="nav-expand-icon" v-show="!uiStore.sidebarCollapsed">
              <ArrowDown v-if="isMenuExpanded('resource')" />
              <ArrowRight v-else />
            </el-icon>
          </div>
          <Transition name="submenu">
            <div class="nav-submenu" v-show="isMenuExpanded('resource') && !uiStore.sidebarCollapsed">
              <div class="nav-sub-item" :class="{ active: activeMenu === '/resource' }" @click.stop="navigateTo('/resource')">
                <span>人员列表</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/resource/performance' }" @click.stop="navigateTo('/resource/performance')">
                <span>绩效评估</span>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 商务管理 - 可折叠 -->
        <div class="nav-group-wrapper" :class="{ expanded: isMenuExpanded('business') }">
          <div class="nav-item nav-parent" :class="{ active: activeMenu.startsWith('/business') }" @click="toggleMenu('business')">
            <el-icon :size="18"><Briefcase /></el-icon>
            <span class="nav-text">商务管理</span>
            <el-icon :size="14" class="nav-expand-icon" v-show="!uiStore.sidebarCollapsed">
              <ArrowDown v-if="isMenuExpanded('business')" />
              <ArrowRight v-else />
            </el-icon>
          </div>
          <Transition name="submenu">
            <div class="nav-submenu" v-show="isMenuExpanded('business') && !uiStore.sidebarCollapsed">
              <div class="nav-sub-item" :class="{ active: activeMenu === '/business/contract' }" @click.stop="navigateTo('/business/contract')">
                <span>合同管理</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/business/payment' }" @click.stop="navigateTo('/business/payment')">
                <span>付款管理</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/business/supplier' }" @click.stop="navigateTo('/business/supplier')">
                <span>供应商管理</span>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 流程审批 - 可折叠 -->
        <div class="nav-group-wrapper" :class="{ expanded: isMenuExpanded('workflow') }">
          <div class="nav-item nav-parent" :class="{ active: activeMenu.startsWith('/workflow') }" @click="toggleMenu('workflow')">
            <el-icon :size="18"><Document /></el-icon>
            <span class="nav-text">流程审批</span>
            <el-icon :size="14" class="nav-expand-icon" v-show="!uiStore.sidebarCollapsed">
              <ArrowDown v-if="isMenuExpanded('workflow')" />
              <ArrowRight v-else />
            </el-icon>
          </div>
          <Transition name="submenu">
            <div class="nav-submenu" v-show="isMenuExpanded('workflow') && !uiStore.sidebarCollapsed">
              <div class="nav-sub-item" :class="{ active: activeMenu === '/workflow/tasks' }" @click.stop="navigateTo('/workflow/tasks')">
                <span>我的待办</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/workflow/history' }" @click.stop="navigateTo('/workflow/history')">
                <span>流程历史</span>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 质量管理 - 无二级菜单 -->
        <div class="nav-item" :class="{ active: activeMenu === '/quality' }" @click="navigateTo('/quality')">
          <el-icon :size="18"><CircleCheck /></el-icon>
          <span class="nav-text">质量管理</span>
          <div class="nav-indicator" v-if="activeMenu === '/quality'" />
        </div>

        <!-- 知识管理 - 无二级菜单 -->
        <div class="nav-item" :class="{ active: activeMenu === '/knowledge' }" @click="navigateTo('/knowledge')">
          <el-icon :size="18"><Reading /></el-icon>
          <span class="nav-text">知识管理</span>
          <div class="nav-indicator" v-if="activeMenu === '/knowledge'" />
        </div>

        <!-- 系统管理 - 可折叠 -->
        <div class="nav-group-wrapper" :class="{ expanded: isMenuExpanded('system') }">
          <div class="nav-item nav-parent" :class="{ active: activeMenu.startsWith('/system') }" @click="toggleMenu('system')">
            <el-icon :size="18"><Setting /></el-icon>
            <span class="nav-text">系统管理</span>
            <el-icon :size="14" class="nav-expand-icon" v-show="!uiStore.sidebarCollapsed">
              <ArrowDown v-if="isMenuExpanded('system')" />
              <ArrowRight v-else />
            </el-icon>
          </div>
          <Transition name="submenu">
            <div class="nav-submenu" v-show="isMenuExpanded('system') && !uiStore.sidebarCollapsed">
              <div class="nav-sub-item" :class="{ active: activeMenu === '/system/users' }" @click.stop="navigateTo('/system/users')">
                <span>用户管理</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/system/roles' }" @click.stop="navigateTo('/system/roles')">
                <span>角色管理</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/system/departments' }" @click.stop="navigateTo('/system/departments')">
                <span>部门管理</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/system/announcements' }" @click.stop="navigateTo('/system/announcements')">
                <span>公告管理</span>
              </div>
              <div class="nav-sub-item" :class="{ active: activeMenu === '/system/permissions' }" @click.stop="navigateTo('/system/permissions')">
                <span>权限管理</span>
              </div>
            </div>
          </Transition>
        </div>
      </nav>
    </aside>

    <!-- Main Container -->
    <div class="main-container">
      <!-- Header -->
      <header class="header">
        <div class="header-left">
          <div class="header-breadcrumb">
            <span class="breadcrumb-home" @click="navigateTo('/dashboard')">
              <el-icon :size="16"><HomeFilled /></el-icon>
            </span>
            <span class="breadcrumb-sep" v-if="currentTitle">/</span>
            <span class="breadcrumb-current" v-if="currentTitle">{{ currentTitle }}</span>
          </div>
        </div>

        <div class="header-center">
          <div class="header-search">
            <el-icon><Search /></el-icon>
            <input type="text" placeholder="搜索项目、任务、文档..." class="search-input">
          </div>
        </div>

        <div class="header-right">
          <ThemeToggle />
          <button class="header-action" title="通知">
            <el-icon :size="18"><Bell /></el-icon>
            <span class="notification-dot" />
          </button>
          <div ref="userMenuRef" class="user-menu-trigger" @click="showUserMenu = !showUserMenu">
            <div class="user-avatar">
              <span>{{ (authStore.userName || 'A').charAt(0).toUpperCase() }}</span>
            </div>
            <div class="user-info">
              <span class="user-name">{{ authStore.userName || '管理员' }}</span>
            </div>
            <el-icon :size="12" class="user-arrow"><ArrowDown /></el-icon>
            <Transition name="dropdown">
              <div v-if="showUserMenu" class="user-dropdown">
                <div class="dropdown-header">
                  <div class="dropdown-avatar">
                    <span>{{ (authStore.userName || 'A').charAt(0).toUpperCase() }}</span>
                  </div>
                  <div>
                    <div class="dropdown-name">{{ authStore.userName || '管理员' }}</div>
                    <div class="dropdown-role">系统管理员</div>
                  </div>
                </div>
                <div class="dropdown-divider" />
                <div class="dropdown-item" @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </header>

      <!-- Content -->
      <main class="main-content">
        <Transition name="page-fade" mode="out-in">
          <router-view />
        </Transition>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import ThemeToggle from '@/components/ThemeToggle.vue'
import {
  Menu,
  Odometer,
  FolderOpened,
  Money,
  Clock,
  UserFilled,
  Briefcase,
  Document,
  CircleCheck,
  Reading,
  Setting,
  DArrowLeft,
  DArrowRight,
  ArrowDown,
  ArrowRight,
  HomeFilled,
  Search,
  Bell,
  SwitchButton,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

const activeMenu = computed(() => route.path as string)
const currentTitle = computed(() => (route.meta.title as string) || '')
const showUserMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

// 折叠状态管理
const expandedMenus = ref<string[]>(['project', 'workflow', 'system']) // 默认展开的菜单

function toggleMenu(menuId: string) {
  if (uiStore.sidebarCollapsed) {
    // 收起状态下直接导航到主页面
    const defaultPaths: Record<string, string> = {
      project: '/project',
      cost: '/cost',
      timesheet: '/timesheet',
      resource: '/resource',
      business: '/business/contract',
      workflow: '/workflow/tasks',
      system: '/system/users',
    }
    navigateTo(defaultPaths[menuId] || '/')
    return
  }
  
  if (expandedMenus.value.includes(menuId)) {
    expandedMenus.value = expandedMenus.value.filter(id => id !== menuId)
  } else {
    expandedMenus.value.push(menuId)
  }
}

function isMenuExpanded(menuId: string): boolean {
  return expandedMenus.value.includes(menuId)
}

// 自动展开当前路由所在的菜单
watch(activeMenu, (path) => {
  const menuMap: Record<string, string[]> = {
    project: ['/project', '/project/create'],
    cost: ['/cost', '/cost/budget'],
    timesheet: ['/timesheet'],
    resource: ['/resource', '/resource/performance'],
    business: ['/business/contract', '/business/payment', '/business/supplier'],
    workflow: ['/workflow/tasks', '/workflow/history'],
    system: ['/system/users', '/system/roles', '/system/departments', '/system/announcements', '/system/permissions'],
  }
  
  for (const [menuId, paths] of Object.entries(menuMap)) {
    if (paths.some(p => path.startsWith(p)) && !expandedMenus.value.includes(menuId)) {
      expandedMenus.value.push(menuId)
    }
  }
}, { immediate: true })

function handleOutsideClick(e: MouseEvent) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target as Node)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  uiStore.initTheme()
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})

function navigateTo(path: string) {
  router.push(path)
  showUserMenu.value = false
}

async function handleLogout() {
  showUserMenu.value = false
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.main-layout {
  display: flex;
  height: 100vh;
  background: $bg-secondary;
}

/* Sidebar */
.sidebar {
  width: $nav-width-expanded;
  background: $nav-bg; // 低饱和度深灰纯色
  display: flex;
  flex-direction: column;
  position: relative;
  transition: width $transition-slow;
  overflow: hidden;
  z-index: 100;

  &.collapsed {
    width: $nav-width-collapsed;
    .logo-text, .nav-text, .nav-expand-icon, .nav-submenu, .nav-indicator { display: none; }
    .sidebar-nav { padding: 8px 0; }
    .nav-item { 
      justify-content: center; 
      padding: $nav-item-padding-y 12px; 
      margin: 4px 12px; 
    }
    .sidebar-toggle {
      left: 50%;
      transform: translateX(-50%);
    }
  }
}

.sidebar-logo {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid $nav-divider-color;

  .logo-icon {
    width: 36px; height: 36px; flex-shrink: 0;
    background: rgba(255, 255, 255, 0.1);
    border-radius: $radius-md;
    display: flex; align-items: center; justify-content: center;
  }

  .logo-text {
    display: flex; flex-direction: column; overflow: hidden;
    .logo-title {
      font-size: 18px; font-weight: $font-weight-bold;
      color: white; letter-spacing: 1px;
    }
    .logo-subtitle {
      font-size: 11px; color: rgba(255, 255, 255, 0.55);
      margin-top: 2px;
    }
  }
}

// 收起/展开开关 (顶部位置)
.sidebar-toggle {
  position: absolute;
  top: 72px;
  left: 12px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.6);
  transition: all $transition-normal;
  z-index: 10;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    transform: scale(1.1);
  }
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0; // 上下内边距16px
  padding-top: 48px; // 为toggle按钮留空间
  overflow-y: auto;
  overflow-x: hidden;
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 2px; }
}

// 一级菜单项
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: $nav-item-padding-y $nav-item-padding-x;
  margin: 3px $nav-item-margin-x;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all $transition-normal;
  color: $nav-text-color;
  position: relative;
  font-size: $nav-font-size-level1; // 14px
  font-weight: $nav-font-weight-level1; // 500

  // hover动效
  &:hover {
    background: $nav-hover-bg;
    color: white;
    transform: translateX(2px);
  }

  // 激活状态
  &.active {
    background: $nav-active-bg;
    color: $nav-active-color;
    
    .nav-indicator {
      position: absolute;
      left: 0;
      top: 0;
      width: 4px;
      height: 100%;
      background: $nav-indicator-color;
      border-radius: 0 4px 4px 0;
    }
  }

  .nav-text {
    white-space: nowrap;
    flex: 1;
  }
  
  // 展开/收起图标
  .nav-expand-icon {
    color: rgba(255, 255, 255, 0.5);
    transition: transform $transition-normal;
  }
}

// 有二级菜单的一级菜单项
.nav-parent {
  &:hover {
    .nav-expand-icon {
      color: white;
    }
  }
}

// 菜单组容器
.nav-group-wrapper {
  &.expanded .nav-parent .nav-expand-icon {
    transform: rotate(0deg); // 展开时图标向下
  }
  
  &:not(.expanded) .nav-parent .nav-expand-icon {
    transform: rotate(-90deg); // 收起时图标向右
  }
}

// 二级菜单容器
.nav-submenu {
  max-height: 500px;
  overflow: hidden;
  transition: max-height $transition-slow ease-out, opacity $transition-normal;
}

// 二级菜单项
.nav-sub-item {
  padding: 12px $nav-item-padding-x 12px $nav-submenu-indent; // 左侧缩进52px
  margin: 2px $nav-item-margin-x;
  border-radius: $radius-sm;
  cursor: pointer;
  color: $nav-sub-text-color;
  font-size: $nav-font-size-level2; // 13px
  font-weight: $nav-font-weight-level2; // 400
  transition: all $transition-normal;
  display: flex;
  align-items: center;
  
  &:hover {
    background: rgba(255, 255, 255, 0.06);
    color: white;
  }
  
  &.active {
    background: rgba($accent-color, 0.15);
    color: $nav-sub-text-color-active;
    
    // 激活指示器
    &::before {
      content: '';
      position: absolute;
      left: $nav-submenu-indent - 8px;
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: $nav-indicator-color;
    }
  }
}

// 子菜单展开/收起动画
.submenu-enter-active {
  transition: max-height $transition-slow ease-out, opacity $transition-normal;
}
.submenu-leave-active {
  transition: max-height $transition-fast ease-in, opacity $transition-fast;
}
.submenu-enter-from,
.submenu-leave-to {
  max-height: 0;
  opacity: 0;
}

/* Header */
.header {
  height: $header-height;
  background: $bg-primary;
  display: flex; align-items: center;
  padding: 0 $spacing-2xl; // 32px
  border-bottom: 1px solid $border-color;
  gap: $spacing-xl;
}

.header-left { flex-shrink: 0; }
.header-breadcrumb {
  display: flex; align-items: center; gap: 8px;
  font-size: $font-size-md;
  .breadcrumb-home {
    cursor: pointer; color: $text-muted;
    display: flex; align-items: center;
    &:hover { color: $accent-color; }
  }
  .breadcrumb-sep { color: $text-light; }
  .breadcrumb-current { color: $text-primary; font-weight: $font-weight-medium; }
}

.header-center {
  flex: 1; display: flex; justify-content: center;
  .header-search {
    display: flex; align-items: center; gap: 8px;
    background: $bg-secondary; border: 1px solid $border-color;
    border-radius: 24px; padding: 8px 16px;
    width: 100%; max-width: 400px;
    transition: all $transition-normal;
    color: $text-muted;
    &:focus-within { border-color: $accent-color; background: $bg-primary; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
    .search-input {
      flex: 1; border: none; background: transparent;
      font-size: $font-size-md; color: $text-primary; outline: none;
      &::placeholder { color: $text-muted; }
    }
  }
}

.header-right {
  display: flex; align-items: center; gap: 8px; flex-shrink: 0;
  .header-action {
    width: 36px; height: 36px; border-radius: $radius-md;
    background: transparent; border: none; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    color: $text-secondary; transition: all $transition-normal;
    position: relative;
    &:hover { background: $bg-secondary; color: $accent-color; }
    .notification-dot {
      position: absolute; top: 8px; right: 8px;
      width: 8px; height: 8px; border-radius: 50%;
      background: $danger-color; border: 2px solid $bg-primary;
    }
  }
}

.user-menu-trigger {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 8px; border-radius: $radius-md;
  cursor: pointer; transition: all $transition-normal;
  position: relative;
  &:hover { background: $bg-secondary; }
  .user-avatar {
    width: 32px; height: 32px; border-radius: $radius-md;
    background: $accent-gradient; display: flex; align-items: center;
    justify-content: center; color: white; font-weight: $font-weight-bold;
    font-size: $font-size-sm;
  }
  .user-info { display: flex; flex-direction: column; }
  .user-name { font-size: $font-size-sm; font-weight: $font-weight-semibold; color: $text-primary; }
  .user-arrow { color: $text-muted; }
}

.user-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  min-width: 220px; background: $bg-primary;
  border-radius: $radius-lg; box-shadow: $shadow-xl;
  border: 1px solid $border-color; padding: 8px; z-index: 1000;
  .dropdown-header {
    display: flex; align-items: center; gap: 12px;
    padding: 12px; border-radius: $radius-md;
    .dropdown-avatar {
      width: 40px; height: 40px; border-radius: $radius-md;
      background: $accent-gradient; display: flex; align-items: center;
      justify-content: center; color: white; font-weight: $font-weight-bold;
      font-size: $font-size-lg;
    }
    .dropdown-name { font-size: $font-size-md; font-weight: $font-weight-semibold; color: $text-primary; }
    .dropdown-role { font-size: $font-size-xs; color: $text-muted; }
  }
  .dropdown-divider { height: 1px; background: $border-color; margin: 4px 0; }
  .dropdown-item {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 12px; border-radius: $radius-sm;
    font-size: $font-size-sm; color: $text-secondary;
    cursor: pointer; transition: all $transition-fast;
    &:hover { background: $bg-secondary; color: $text-primary; }
  }
}

.dropdown-enter-active, .dropdown-leave-active {
  transition: opacity 150ms ease, transform 150ms ease;
}
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0; transform: translateY(-8px);
}

/* Main Content */
.main-content {
  flex: 1;
  padding: $spacing-2xl; // 32px 外边距
  overflow-y: auto;
  background: $bg-secondary;
  max-width: 1440px;
}

/* Responsive */
@media (max-width: 1024px) {
  .sidebar { width: $nav-width-collapsed; 
    .logo-text, .nav-text, .nav-expand-icon, .nav-submenu, .nav-indicator { display: none; } 
  }
  .sidebar-toggle {
    left: 50%;
    transform: translateX(-50%);
  }
  .header-center { display: none; }
  .main-content { padding: $spacing-xl; } // 24px
}
@media (max-width: 768px) {
  .user-info { display: none; }
  .main-content { padding: $spacing-lg; } // 16px
}
</style>
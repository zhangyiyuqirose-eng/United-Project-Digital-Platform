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

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <!-- Single items -->
        <div class="nav-item" :class="{ active: activeMenu === '/dashboard' }" @click="navigateTo('/dashboard')">
          <el-icon :size="18"><Odometer /></el-icon>
          <span class="nav-text">个人工作台</span>
          <div class="nav-indicator" v-if="activeMenu === '/dashboard'" />
        </div>

        <div class="nav-item" :class="{ active: activeMenu.startsWith('/project') }" @click="navigateTo('/project')">
          <el-icon :size="18"><Folder /></el-icon>
          <span class="nav-text">项目管理</span>
          <div class="nav-indicator" v-if="activeMenu.startsWith('/project')" />
        </div>

        <div class="nav-item" :class="{ active: activeMenu.startsWith('/cost') }" @click="navigateTo('/cost')">
          <el-icon :size="18"><Money /></el-icon>
          <span class="nav-text">成本管理</span>
          <div class="nav-indicator" v-if="activeMenu.startsWith('/cost')" />
        </div>

        <div class="nav-item" :class="{ active: activeMenu.startsWith('/timesheet') }" @click="navigateTo('/timesheet')">
          <el-icon :size="18"><Clock /></el-icon>
          <span class="nav-text">工时管理</span>
          <div class="nav-indicator" v-if="activeMenu.startsWith('/timesheet')" />
        </div>

        <div class="nav-item" :class="{ active: activeMenu.startsWith('/resource') }" @click="navigateTo('/resource')">
          <el-icon :size="18"><UserFilled /></el-icon>
          <span class="nav-text">资源池</span>
          <div class="nav-indicator" v-if="activeMenu.startsWith('/resource')" />
        </div>

        <!-- Groups -->
        <div class="nav-group" v-show="!uiStore.sidebarCollapsed">
          <div class="nav-group-title">
            <el-icon :size="14"><Briefcase /></el-icon>
            <span>商务管理</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu === '/business/contract' }" @click="navigateTo('/business/contract')">
            <span>合同管理</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu === '/business/payment' }" @click="navigateTo('/business/payment')">
            <span>付款管理</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu === '/business/supplier' }" @click="navigateTo('/business/supplier')">
            <span>供应商管理</span>
          </div>
        </div>

        <div class="nav-group" v-show="!uiStore.sidebarCollapsed">
          <div class="nav-group-title">
            <el-icon :size="14"><Document /></el-icon>
            <span>流程审批</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu === '/workflow/tasks' }" @click="navigateTo('/workflow/tasks')">
            <span>我的待办</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu === '/workflow/history' }" @click="navigateTo('/workflow/history')">
            <span>流程历史</span>
          </div>
        </div>

        <div class="nav-item" :class="{ active: activeMenu === '/quality' }" @click="navigateTo('/quality')">
          <el-icon :size="18"><CircleCheck /></el-icon>
          <span class="nav-text">质量管理</span>
          <div class="nav-indicator" v-if="activeMenu === '/quality'" />
        </div>

        <div class="nav-item" :class="{ active: activeMenu === '/knowledge' }" @click="navigateTo('/knowledge')">
          <el-icon :size="18"><Reading /></el-icon>
          <span class="nav-text">知识管理</span>
          <div class="nav-indicator" v-if="activeMenu === '/knowledge'" />
        </div>

        <div class="nav-group" v-show="!uiStore.sidebarCollapsed">
          <div class="nav-group-title">
            <el-icon :size="14"><Setting /></el-icon>
            <span>系统管理</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu.startsWith('/system') && activeMenu !== '/system/announcements' }" @click="navigateTo('/system/users')">
            <span>用户管理</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu === '/system/roles' }" @click="navigateTo('/system/roles')">
            <span>角色管理</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu === '/system/departments' }" @click="navigateTo('/system/departments')">
            <span>部门管理</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu === '/system/announcements' }" @click="navigateTo('/system/announcements')">
            <span>公告管理</span>
          </div>
          <div class="nav-sub-item" :class="{ active: activeMenu === '/system/permissions' }" @click="navigateTo('/system/permissions')">
            <span>权限管理</span>
          </div>
        </div>
      </nav>

      <!-- Collapse button -->
      <button class="sidebar-collapse" @click="uiStore.toggleSidebar">
        <el-icon><DArrowLeft v-if="!uiStore.sidebarCollapsed" /><DArrowRight v-else /></el-icon>
      </button>
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
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

const activeMenu = computed(() => route.path as string)
const currentTitle = computed(() => (route.meta.title as string) || '')
const showUserMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

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
  width: $sidebar-width;
  background: $bg-sidebar;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: width $transition-slow;
  overflow: hidden;
  z-index: 100;

  &.collapsed {
    width: $sidebar-collapsed-width;
    .logo-text, .nav-text, .nav-group { display: none; }
    .sidebar-nav { padding: 8px 0; }
    .nav-item { justify-content: center; padding: 12px; margin: 4px 12px; }
    .nav-item .nav-indicator { display: none; }
  }
}

.sidebar-logo {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

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

.sidebar-nav {
  flex: 1;
  padding: 12px 0;
  overflow-y: auto;
  overflow-x: hidden;
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 2px; }
}

.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 20px; margin: 3px 10px;
  border-radius: $radius-md; cursor: pointer;
  transition: all $transition-normal;
  color: rgba(255, 255, 255, 0.7);
  position: relative;
  font-size: $font-size-md;

  &:hover { background: rgba(255, 255, 255, 0.08); color: white; }

  &.active {
    background: rgba(99, 102, 241, 0.2);
    color: white;
    .nav-indicator {
      position: absolute; right: 12px; top: 50%;
      width: 6px; height: 6px; border-radius: 50%;
      background: #818cf8; transform: translateY(-50%);
    }
  }

  .nav-text {
    white-space: nowrap;
    font-weight: $font-weight-medium;
  }
}

.nav-group {
  margin: 6px 0;
  .nav-group-title {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 24px; color: rgba(255, 255, 255, 0.35);
    font-size: $font-size-xs; font-weight: $font-weight-semibold;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .nav-sub-item {
    padding: 9px 20px 9px 52px; margin: 2px 10px;
    border-radius: $radius-sm; cursor: pointer;
    color: rgba(255, 255, 255, 0.6); font-size: $font-size-sm;
    transition: all $transition-normal;
    &:hover { background: rgba(255,255,255,0.06); color: white; }
    &.active { background: rgba(99, 102, 241, 0.15); color: #a5b4fc; }
  }
}

.sidebar-collapse {
  position: absolute; bottom: 16px; right: 12px;
  width: 28px; height: 28px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.1); border: none;
  cursor: pointer; display: flex; align-items: center;
  justify-content: center; color: rgba(255, 255, 255, 0.6);
  transition: all $transition-normal;
  &:hover { background: rgba(255,255,255,0.2); color: white; }
}

/* Header */
.header {
  height: $header-height;
  background: $bg-primary;
  display: flex; align-items: center;
  padding: 0 $spacing-xl;
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
  padding: $content-padding;
  overflow-y: auto;
  background: $bg-secondary;
}

/* Responsive */
@media (max-width: 1024px) {
  .sidebar { width: $sidebar-collapsed-width; .logo-text, .nav-text, .nav-group { display: none; } }
  .header-center { display: none; }
}
@media (max-width: 768px) {
  .user-info { display: none; }
}
</style>

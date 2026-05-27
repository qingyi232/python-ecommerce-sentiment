<template>
  <el-container class="main-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo-area">
        <el-icon :size="28" color="#fff"><TrendCharts /></el-icon>
        <span v-if="!isCollapse" class="logo-text">评论分析系统</span>
      </div>
      <el-menu
        :default-active="currentRoute"
        :collapse="isCollapse"
        background-color="#1a2e23"
        text-color="#a3b8aa"
        active-text-color="#ffffff"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据总览</template>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <template #title>商品管理</template>
        </el-menu-item>
        <el-menu-item index="/reviews">
          <el-icon><ChatDotSquare /></el-icon>
          <template #title>评论管理</template>
        </el-menu-item>
        <el-menu-item index="/sentiment">
          <el-icon><TrendCharts /></el-icon>
          <template #title>情感分析</template>
        </el-menu-item>
        <el-menu-item index="/demand">
          <el-icon><Aim /></el-icon>
          <template #title>需求挖掘</template>
        </el-menu-item>
        <el-menu-item index="/crawl">
          <el-icon><Download /></el-icon>
          <template #title>数据采集</template>
        </el-menu-item>
        <el-menu-item index="/visualization">
          <el-icon><PieChart /></el-icon>
          <template #title>可视化展示</template>
        </el-menu-item>
        <el-menu-item v-if="userInfo?.role === 'admin'" index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <el-header class="top-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="userInfo?.avatar || ''">
                {{ userInfo?.nickname?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="user-name">{{ userInfo?.nickname || userInfo?.username || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)

const userInfo = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}')
  } catch { return {} }
})

const currentRoute = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title || '首页')

const handleCommand = (command) => {
  if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }
}
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: var(--bg-sidebar);
  transition: width 0.3s ease;
  overflow: hidden;

  .logo-area {
    height: 64px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    gap: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);

    .el-icon {
      flex-shrink: 0;
    }

    .logo-text {
      font-size: 16px;
      font-weight: 600;
      color: #fff;
      white-space: nowrap;
    }
  }

  .sidebar-menu {
    border: none;

    :deep(.el-menu-item) {
      height: 48px;
      line-height: 48px;
      margin: 2px 8px;
      border-radius: 8px;

      &.is-active {
        background: var(--bg-sidebar-active) !important;
        color: #fff !important;
      }

      &:hover:not(.is-active) {
        background: rgba(255, 255, 255, 0.06) !important;
      }
    }
  }
}

.main-container {
  background: var(--bg-primary);
}

.top-header {
  height: 64px;
  background: var(--bg-white);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: var(--shadow-sm);

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      color: var(--text-secondary);
      transition: color 0.2s;

      &:hover { color: var(--primary-color); }
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 8px;
      transition: background 0.2s;

      &:hover { background: var(--bg-primary); }

      .user-name {
        font-size: 14px;
        color: var(--text-primary);
        font-weight: 500;
      }
    }
  }
}

.main-content {
  padding: 24px;
  overflow-y: auto;
  background: var(--bg-primary);
}
</style>

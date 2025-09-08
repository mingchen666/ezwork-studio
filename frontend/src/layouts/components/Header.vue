<!-- components/layout/HeaderComponent.vue -->
<template>
  <header class="layout-header">
    <div class="header-container">
      <!-- Logo区域 -->
      <div class="logo-section">
        <div class="logo-icon">
          <n-icon size="32" color="#6366f1">
            <PictureOutlined />
          </n-icon>
        </div>
        <div class="logo-text">
          <h1>AI绘图助手</h1>
          <span class="logo-subtitle">Creative AI Studio</span>
        </div>
      </div>

      <!-- 主导航菜单 -->
      <nav v-if="!isMobile" class="main-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActiveRoute(item.path) }"
        >
          <n-icon :size="20">
            <component :is="item.icon" />
          </n-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- 用户操作区 -->
      <div class="user-actions">
        <!-- 快速设置按钮 -->
        <n-dropdown :options="quickSettingsOptions" @select="handleQuickSettings">
          <n-button circle quaternary>
            <n-icon size="18">
              <SettingOutlined />
            </n-icon>
          </n-button>
        </n-dropdown>

        <!-- 用户菜单 -->
        <n-dropdown :options="userMenuOptions" @select="handleUserMenuSelect">
          <n-button circle quaternary>
            <n-icon size="18">
              <UserOutlined />
            </n-icon>
          </n-button>
        </n-dropdown>
      </div>

      <!-- 移动端菜单按钮 -->
      <n-button
        v-if="isMobile"
        class="mobile-menu-btn"
        quaternary
        circle
        @click="$emit('toggle-mobile-menu')"
      >
        <n-icon size="20">
          <component :is="showMobileMenu ? CloseOutlined : MenuOutlined" />
        </n-icon>
      </n-button>
    </div>

    <!-- 移动端侧边菜单 -->
    <div v-if="isMobile" class="mobile-menu" :class="{ show: showMobileMenu }">
      <nav class="mobile-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="mobile-nav-item"
          :class="{ active: isActiveRoute(item.path) }"
          @click="$emit('toggle-mobile-menu')"
        >
          <n-icon :size="20">
            <component :is="item.icon" />
          </n-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  PictureOutlined,
  DashboardOutlined,
  SettingOutlined,
  FileImageOutlined,
  MenuOutlined,
  CloseOutlined,
  UserOutlined,
  LogoutOutlined,
  InfoCircleOutlined,
  ApiOutlined,
  ClearOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'

defineProps({
  isMobile: Boolean,
  showMobileMenu: Boolean
})

defineEmits(['toggle-mobile-menu'])

const route = useRoute()
const router = useRouter()

// 主菜单项
const menuItems = [
  {
    path: '/dashboard',
    label: '工作台',
    icon: DashboardOutlined
  },
  {
    path: '/draw',
    label: 'AI绘图',
    icon: PictureOutlined
  },
  {
    path: '/gallery',
    label: '作品画廊',
    icon: FileImageOutlined
  },
  {
    path: '/settings',
    label: '系统设置',
    icon: SettingOutlined
  }
]

// 快速设置选项
const quickSettingsOptions = [
  {
    label: 'API配置',
    key: 'api-config',
    icon: () => h(ApiOutlined)
  },
  {
    label: '清除缓存',
    key: 'clear-cache',
    icon: () => h(ClearOutlined)
  },
  {
    label: '重载服务',
    key: 'reload-services',
    icon: () => h(ReloadOutlined)
  },
  {
    type: 'divider'
  },
  {
    label: '完整设置',
    key: 'full-settings',
    icon: () => h(SettingOutlined)
  }
]

// 用户菜单选项
const userMenuOptions = [
  {
    label: '关于',
    key: 'about',
    icon: () => h(InfoCircleOutlined)
  },
  {
    label: '退出',
    key: 'logout',
    icon: () => h(LogoutOutlined)
  }
]

// 方法
const isActiveRoute = (path) => {
  return route.path.startsWith(path)
}

const handleQuickSettings = (key) => {
  switch (key) {
    case 'api-config':
      router.push('/settings')
      break
    case 'clear-cache':
      localStorage.clear()
      sessionStorage.clear()
      window.$message?.success('缓存已清除')
      break
    case 'reload-services':
      window.location.reload()
      break
    case 'full-settings':
      router.push('/settings')
      break
  }
}

const handleUserMenuSelect = (key) => {
  switch (key) {
    case 'about':
      window.$message?.info('AI绘图助手 v1.0.0')
      break
    case 'logout':
      window.$message?.success('已退出')
      break
  }
}
</script>

<style scoped>
.layout-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.logo-text h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.logo-subtitle {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: #f1f5f9;
  color: #1e293b;
  transform: translateY(-1px);
}

.nav-item.active {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.mobile-menu-btn {
  display: none;
}

/* 移动端菜单 */
.mobile-menu {
  position: fixed;
  top: 64px;
  left: 0;
  width: 280px;
  height: calc(100vh - 64px);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-right: 1px solid #e2e8f0;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  z-index: 999;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
}

.mobile-menu.show {
  transform: translateX(0);
}

.mobile-nav {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  font-size: 15px;
  transition: all 0.2s ease;
}

.mobile-nav-item:hover {
  background: #f8fafc;
  color: #1e293b;
}

.mobile-nav-item.active {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
}

/* 移动端适配 */
@media (max-width: 1024px) {
  .main-nav {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
  }

  .header-container {
    padding: 0 16px;
  }
}

@media (max-width: 768px) {
  .logo-text h1 {
    font-size: 18px;
  }

  .logo-subtitle {
    display: none;
  }

  .header-container {
    height: 56px;
  }

  .mobile-menu {
    top: 56px;
    height: calc(100vh - 56px);
  }
}
</style>

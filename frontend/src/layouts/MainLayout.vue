<template>
  <div class="app-layout">
    <!-- 头部 -->
    <header class="app-header">
      <div class="header-content">
        <!-- 左侧Logo和项目名 -->
        <div class="header-left">
          <router-link to="/" class="logo-link">
            <div class="logo">
              <div class="logo-icon">🎨</div>
              <div class="logo-text">
                <h1>Ezwork Studio</h1>
                <span class="tagline">AI绘画工具客户端</span>
              </div>
            </div>
          </router-link>
        </div>

        <!-- 右侧用户信息和操作 -->
        <div class="header-right">
          <!-- 用户信息 -->
          <div class="user-section" v-if="userStore.isLoggedIn">
            <el-dropdown @command="handleCommand" trigger="click">
              <div class="user-info">
                <el-avatar :size="36" :src="userStore.userInfo?.avatar" class="user-avatar">
                  {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}
                </el-avatar>
                <div class="user-details" v-if="!isMobile">
                  <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
                  <span class="user-email">{{ userStore.userInfo?.email }}</span>
                </div>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon>
                    <span>设置</span>
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    <span>退出登录</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <!-- 未登录状态 -->
          <div class="auth-actions" v-else>
            <el-button type="primary" @click="goToAuth" size="default"> 登录 / 注册 </el-button>
          </div>

          <!-- 设置按钮（独立） -->
          <el-button circle class="settings-btn" @click="openSettings" v-if="!isMobile">
            <el-icon><Setting /></el-icon>
          </el-button>

          <!-- 移动端菜单按钮 -->
          <el-button circle class="mobile-menu-btn" @click="showMobileMenu = true" v-if="isMobile">
            <el-icon><Menu /></el-icon>
          </el-button>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="app-main">
      <router-view />
    </main>

    <!-- 移动端菜单抽屉 -->
    <el-drawer v-model="showMobileMenu" title="菜单" direction="rtl" size="280px" v-if="isMobile">
      <div class="mobile-menu">
        <!-- 用户信息 -->
        <div class="mobile-user-info" v-if="userStore.isLoggedIn">
          <el-avatar :size="60" :src="userStore.userInfo?.avatar" class="mobile-avatar">
            {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}
          </el-avatar>
          <div class="mobile-user-details">
            <h3>{{ userStore.userInfo?.username || '用户' }}</h3>
            <p>{{ userStore.userInfo?.email }}</p>
          </div>
        </div>

        <!-- 菜单项 -->
        <div class="mobile-menu-items">
          <!-- <div class="menu-item" @click="handleCommand('profile')" v-if="userStore.isLoggedIn">
            <el-icon><User /></el-icon>
            <span>个人资料</span>
          </div> -->
          <div class="menu-item" @click="openSettings">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </div>
          <div class="menu-item" @click="handleCommand('logout')" v-if="userStore.isLoggedIn">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </div>
          <div class="menu-item" @click="goToAuth" v-else>
            <el-icon><UserFilled /></el-icon>
            <span>登录 / 注册</span>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 设置弹窗 -->
    <SettingsDialog v-model="showSettings" @save="handleSettingsSave" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, User, Setting, SwitchButton, Menu, UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useResponsive } from '@/hooks/useResponsive'
import SettingsDialog from '@/views/gemini-draw/components/SettingsModal.vue'

const router = useRouter()
const userStore = useUserStore()
const { isMobile } = useResponsive()

// 响应式数据
const showSettings = ref(false)
const showMobileMenu = ref(false)

// 处理下拉菜单命令
const handleCommand = async (command) => {
  showMobileMenu.value = false

  switch (command) {
    case 'profile':
      // 跳转到个人资料页面
      router.push('/profile')
      break
    case 'settings':
      openSettings()
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '确认退出', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })

        await userStore.logout()
        ElMessage.success('已退出登录')
        router.push('/auth')
      } catch {
        // 用户取消
      }
      break
  }
}

// 打开设置
const openSettings = () => {
  showSettings.value = true
  showMobileMenu.value = false
}

// 跳转到登录页面
const goToAuth = () => {
  router.push('/auth')
  showMobileMenu.value = false
}

// 处理设置保存
const handleSettingsSave = (config) => {
  ElMessage.success('设置已保存')
}
</script>

<style lang="scss" scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.app-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  flex-shrink: 0; // 防止头部被压缩
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 10px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  .logo-link {
    text-decoration: none;
    color: inherit;

    &:hover .logo {
      transform: translateY(-1px);
    }
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    transition: transform 0.2s ease;

    .logo-icon {
      font-size: 1.8rem;
      filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }

    .logo-text {
      h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.2;
      }

      .tagline {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 500;
      }
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-section {
  .user-info {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 10px;
    transition: all 0.2s ease;

    &:hover {
      background: #f8fafc;
    }

    .user-avatar {
      background: linear-gradient(45deg, #70a3ef 0%, #599af4 100%);
      color: white;
      font-weight: 600;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
    }

    .user-details {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 2px;

      .username {
        font-size: 0.9rem;
        font-weight: 600;
        color: #1e293b;
        line-height: 1.2;
      }

      .user-email {
        font-size: 0.75rem;
        color: #64748b;
        line-height: 1.2;
      }
    }

    .dropdown-icon {
      color: #64748b;
      font-size: 0.8rem;
      transition: transform 0.2s ease;
    }

    &:hover .dropdown-icon {
      transform: rotate(180deg);
    }
  }
}

.auth-actions {
  .el-button {
    border-radius: 8px;
    font-weight: 600;
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    border: none;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
  }
}

.settings-btn {
  background: #7ab5e8;
  border-color: #0f7ce1;
  color: #0d0d0d;
  transition: all 0.3s ease;

  &:hover {
    transform: rotate(90deg) scale(1.1);
  }
}

.mobile-menu-btn {
  background: #f8fafc;
  border-color: #e2e8f0;
  color: #64748b;

  &:hover {
    background: #e2e8f0;
    border-color: #cbd5e1;
    color: #475569;
  }
}

.app-main {
  flex: 1;
  min-height: 0; // 重要：允许子元素正确计算高度

  // 确保路由视图占满整个高度
  > * {
    height: 100%;
    min-height: calc(100vh - 64px); // 减去头部高度
  }
}

// 移动端菜单样式
.mobile-menu {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0 20px;
}

.mobile-user-info {
  padding: 20px 0;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 20px;

  .mobile-avatar {
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
    margin-bottom: 12px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
  }

  .mobile-user-details {
    h3 {
      margin: 0 0 4px 0;
      font-size: 1.1rem;
      color: #1e293b;
      font-weight: 600;
    }

    p {
      margin: 0;
      font-size: 0.9rem;
      color: #64748b;
    }
  }
}

.mobile-menu-items {
  flex: 1;

  .menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 0;
    cursor: pointer;
    border-bottom: 1px solid #f1f5f9;
    transition: all 0.2s ease;

    &:hover {
      background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
      margin: 0 -20px;
      padding-left: 20px;
      padding-right: 20px;
      border-radius: 8px;
    }

    .el-icon {
      color: #64748b;
      font-size: 1.1rem;
    }

    span {
      font-size: 0.95rem;
      color: #374151;
      font-weight: 500;
    }
  }
}

// 下拉菜单样式优化
:deep(.el-dropdown-menu) {
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid #e2e8f0;
  overflow: hidden;

  .el-dropdown-menu__item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    transition: all 0.2s ease;

    &:hover {
      background: linear-gradient(90deg, rgba(102, 126, 234, 0.08) 0%, transparent 100%);
    }

    .el-icon {
      color: #64748b;
      font-size: 1rem;
    }

    span {
      font-size: 0.9rem;
      color: #374151;
    }
  }
}

// 抽屉样式优化
:deep(.el-drawer) {
  .el-drawer__header {
    padding: 20px;
    border-bottom: 1px solid #e2e8f0;

    .el-drawer__title {
      font-weight: 600;
      color: #1e293b;
    }
  }

  .el-drawer__body {
    padding: 0;
  }
}

// 移动端适配
@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
    height: 56px;
  }

  .logo {
    .logo-text {
      h1 {
        font-size: 1.2rem;
      }

      .tagline {
        font-size: 0.7rem;
      }
    }
  }

  .app-main > * {
    min-height: calc(100vh - 56px); // 移动端头部高度
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 12px;
  }

  .logo {
    .logo-icon {
      font-size: 1.5rem;
    }

    .logo-text {
      h1 {
        font-size: 1.1rem;
      }

      .tagline {
        display: none;
      }
    }
  }
}
</style>

<template>
  <div class="auth-container">
    <div class="auth-content">
      <!-- 左侧介绍区域 -->
      <div class="intro-section">
        <div class="intro-content">
          <div class="logo">
            <div class="logo-icon">🎨</div>
            <h1>Ezwork Studio</h1>
            <span class="subtitle">AI绘画工具客户端</span>
          </div>
          <p class="intro-text">
            释放创意无限可能<br>
            让每一个想象都能成为艺术
          </p>
          
          <!-- 装饰元素 -->
          <div class="decoration-elements">
            <div class="floating-shape shape-1"></div>
            <div class="floating-shape shape-2"></div>
            <div class="floating-shape shape-3"></div>
          </div>
        </div>
      </div>
      
      <!-- 右侧表单区域 -->
      <div class="form-section">
        <div class="form-container">
          <!-- 移动端logo -->
          <div class="mobile-logo" v-if="isMobile">
            <div class="logo-icon">🎨</div>
            <h1>Ezwork Studio</h1>
            <span class="subtitle">AI绘画工具客户端</span>
          </div>
          
          <!-- 切换按钮 -->
          <div class="tab-switcher">
            <button 
              :class="['tab-btn', { active: activeTab === 'login' }]"
              @click="activeTab = 'login'"
            >
              登录
            </button>
            <button 
              :class="['tab-btn', { active: activeTab === 'register' }]"
              @click="activeTab = 'register'"
            >
              注册
            </button>
            <div class="tab-indicator" :class="{ 'move-right': activeTab === 'register' }"></div>
          </div>
          
          <!-- 表单内容 -->
          <div class="form-content">
            <transition name="slide" mode="out-in">
              <LoginForm v-if="activeTab === 'login'" @success="handleAuthSuccess" />
              <RegisterForm v-else @success="handleAuthSuccess" />
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import LoginForm from './components/LoginForm.vue'
import RegisterForm from './components/RegisterForm.vue'
import { useResponsive } from '@/hooks/useResponsive'

const router = useRouter()
const { isMobile } = useResponsive()
const activeTab = ref('login')

// 认证成功处理
const handleAuthSuccess = (message) => {
  ElMessage.success(message)
  router.push('/')
}
</script>

<style lang="scss" scoped>
.auth-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1000px;
  width: 100%;
  height: 600px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.intro-section {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  overflow: hidden;

  // 背景装饰
  &::before {
    content: '';
    position: absolute;
    top: -20%;
    left: -20%;
    width: 140%;
    height: 140%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
    animation: float 8s ease-in-out infinite;
  }
}

.intro-content {
  text-align: center;
  position: relative;
  z-index: 2;
}

.logo {
  margin-bottom: 40px;
  
  .logo-icon {
    font-size: 4rem;
    margin-bottom: 20px;
    display: block;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.1));
  }
  
  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0 0 12px 0;
    color: #0f172a;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .subtitle {
    display: block;
    font-size: 1.1rem;
    color: #475569;
    font-weight: 500;
    letter-spacing: 0.5px;
  }
}

.intro-text {
  font-size: 1.2rem;
  line-height: 1.8;
  color: #334155;
  font-weight: 400;
  max-width: 280px;
  margin: 0 auto;
}

.decoration-elements {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;

  .floating-shape {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.4);
    animation: float 6s ease-in-out infinite;

    &.shape-1 {
      width: 60px;
      height: 60px;
      top: 15%;
      left: 10%;
      animation-delay: 0s;
    }

    &.shape-2 {
      width: 40px;
      height: 40px;
      top: 70%;
      right: 15%;
      animation-delay: 2s;
    }

    &.shape-3 {
      width: 80px;
      height: 80px;
      bottom: 20%;
      left: 20%;
      animation-delay: 4s;
    }
  }
}

.form-section {
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #fafbfc;
}

.form-container {
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
}

.mobile-logo {
  text-align: center;
  margin-bottom: 24px;
  display: none;

  .logo-icon {
    font-size: 2.5rem;
    margin-bottom: 8px;
    display: block;
  }

  h1 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0 0 4px 0;
    color: #1e293b;
  }

  .subtitle {
    font-size: 0.9rem;
    color: #64748b;
    font-weight: 500;
  }
}

.tab-switcher {
  position: relative;
  display: flex;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 30px;
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
  
  &.active {
    color: #1e293b;
  }
}

.tab-indicator {
  position: absolute;
  top: 4px;
  left: 4px;
  width: calc(50% - 4px);
  height: calc(100% - 8px);
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  z-index: 1;
  
  &.move-right {
    transform: translateX(100%);
  }
}

.form-content {
  height: 450px;
  display: flex;
  flex-direction: column;
}

// 动画定义
@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-15px) rotate(180deg);
  }
}

// 切换动画
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

// 响应式设计
@media (max-width: 768px) {
  .auth-container {
    padding: 16px;
  }

  .auth-content {
    grid-template-columns: 1fr;
    max-width: 400px;
    height: auto;
    min-height: 600px;
  }
  
  .intro-section {
    display: none;
  }

  .mobile-logo {
    display: block !important;
  }
  
  .form-section {
    padding: 30px;
    background: white;
  }
  
  .form-content {
    height: auto;
    min-height: 400px;
  }
}

@media (max-width: 480px) {
  .auth-container {
    padding: 12px;
  }
  
  .form-section {
    padding: 24px;
  }

  .mobile-logo {
    margin-bottom: 20px;

    h1 {
      font-size: 1.3rem;
    }

    .subtitle {
      font-size: 0.8rem;
    }
  }
}

// 平板适配
@media (max-width: 1024px) and (min-width: 769px) {
  .auth-content {
    max-width: 900px;
  }

  .intro-section {
    padding: 32px;
  }

  .logo h1 {
    font-size: 2.2rem;
  }
}
</style>

<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <HeaderComponent
      :is-mobile="isMobile"
      :show-mobile-menu="showMobileMenu"
      @toggle-mobile-menu="toggleMobileMenu"
    />

    <!-- 主要内容区域 -->
    <main class="main-container">
      <router-view />
    </main>

    <!-- 页脚 -->
    <FooterComponent v-if="showFooter" />

    <!-- 移动端遮罩层 -->
    <div v-if="isMobile && showMobileMenu" class="mobile-overlay" @click="closeMobileMenu" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useBreakpoints, breakpointsTailwind } from '@vueuse/core'
import HeaderComponent from './components/Header.vue'
import FooterComponent from './components/Footer.vue'

// 响应式断点
const breakpoints = useBreakpoints(breakpointsTailwind)
const isMobile = breakpoints.smaller('lg')

// 界面状态
const showMobileMenu = ref(false)

// 是否显示页脚
const showFooter = computed(() => false) // 根据需要控制

// 方法
const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const closeMobileMenu = () => {
  showMobileMenu.value = false
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  /* background: #f8fafc; */
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.mobile-overlay {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
}

@media (max-width: 768px) {
  .mobile-overlay {
    top: 56px;
  }
}
</style>

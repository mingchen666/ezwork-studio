<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup></script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 选中文本样式 */
::selection {
  background: #6366f1;
  color: white;
}

/* 链接样式 */
a {
  color: #6366f1;
  text-decoration: none;
  transition: color 0.2s;
}

a:hover {
  color: #8b5cf6;
}

/* 图片样式 */
img {
  max-width: 100%;
  height: auto;
  display: block;
}

/* 输入框样式 */
input,
textarea,
select {
  font-family: inherit;
}

/* 按钮样式 */
button {
  font-family: inherit;
  cursor: pointer;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

/* 响应式工具类 */
.mobile-only {
  display: none;
}

.desktop-only {
  display: block;
}

@media (max-width: 768px) {
  .mobile-only {
    display: block;
  }

  .desktop-only {
    display: none;
  }

  html {
    font-size: 13px;
  }
}

/* 加载动画 */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading {
  animation: spin 1s linear infinite;
}

/* 打印样式 */
@media print {
  .no-print {
    display: none !important;
  }

  body {
    background: white !important;
    color: black !important;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  * {
    border-width: 2px !important;
  }
}

/* 减少动画 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
</style>

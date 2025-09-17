<template>
  <div class="ai-image-generator">
    <!-- 桌面端布局 -->
    <div
      class="desktop-layout"
      v-if="!isMobile"
      :class="{ 'gallery-collapsed': isGalleryCollapsed }"
    >
      <ControlPanel
        class="control-panel"
        :loading="loading"
        :elapsed-time="elapsedTime"
        @generate="handleGenerate"
        @open-settings="settingsVisible = true"
      />
      <ResultPanel
        class="result-panel"
        :loading="loading"
        :result-image="resultImage"
        :model-response="modelResponse"
        :elapsed-time="elapsedTime"
      />
      <GalleryPanel class="gallery-panel" @select-image="handleSelectGalleryImage" />
    </div>

    <!-- 移动端布局 -->
    <div class="mobile-layout" v-else>
      <el-tabs v-model="activeTab" class="mobile-tabs">
        <el-tab-pane label="生成" name="generate">
          <ControlPanel
            :loading="loading"
            :elapsed-time="elapsedTime"
            @generate="handleGenerate"
            @open-settings="settingsVisible = true"
          />
        </el-tab-pane>
        <el-tab-pane label="结果" name="result">
          <ResultPanel
            :loading="loading"
            :result-image="resultImage"
            :model-response="modelResponse"
            :elapsed-time="elapsedTime"
          />
        </el-tab-pane>
        <el-tab-pane label="图库" name="gallery">
          <GalleryPanel @select-image="handleSelectGalleryImage" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 设置弹窗 -->
    <SettingsModal v-model="settingsVisible" @save="handleSaveSettings" />

    <!-- 全局返回顶部 -->
    <el-backtop :right="20" :bottom="20" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import ControlPanel from './components/ControlPanel.vue'
import ResultPanel from './components/ResultPanel.vue'
import GalleryPanel from './components/GalleryPanel.vue'
import SettingsModal from './components/SettingsModal.vue'
import { useImageGenerator } from './hooks/useImageGenerator'
import { useResponsive } from '@/hooks/useResponsive'
import { useGalleryStore } from '@/stores/gallery'

// 响应式检测
const { isMobile } = useResponsive()

// 图库store
const galleryStore = useGalleryStore()

// 移动端标签页
const activeTab = ref('generate')

// 设置弹窗
const settingsVisible = ref(false)

// 计算属性 - 图库是否折叠
const isGalleryCollapsed = computed(() => galleryStore.isCollapsed)

// 使用图片生成逻辑
const { loading, resultImage, modelResponse, elapsedTime, generateImage, selectGalleryImage } =
  useImageGenerator()
watch(resultImage, (newValue, oldValue) => {
  console.log(`新值: ${newValue}, 旧值: ${oldValue}`)
})
// 处理生成请求
const handleGenerate = async (params) => {
  try {
    await generateImage(params)
    if (isMobile.value) {
      activeTab.value = 'result'
    }
    ElMessage.success('图片生成成功！')
  } catch (error) {
    ElMessage.error(error.message || '生成失败，请重试')
  }
}

// 处理图库选择
const handleSelectGalleryImage = (imageData) => {
  selectGalleryImage(imageData)
  if (isMobile.value) {
    activeTab.value = 'result'
  }
}

// 处理设置保存
const handleSaveSettings = (settings) => {
  ElMessage.success('设置已保存')
  settingsVisible.value = false
}

// 初始化
onMounted(async () => {
  // 初始化图库
  await galleryStore.initialize()
})
</script>

<style lang="scss" scoped>
.ai-image-generator {
  height: calc(100vh - 60px); // 减去头部高度

  .desktop-layout {
    display: grid;
    grid-template-columns: 330px 1fr 330px;
    height: 100vh;
    gap: 0;
    transition: grid-template-columns 0.3s ease;

    &.gallery-collapsed {
      grid-template-columns: 380px 1fr 80px; // 左边变宽，右边变窄
    }

    .control-panel {
      border-right: 1px solid #e5e7eb;
    }

    .result-panel {
      border-right: 1px solid #e5e7eb;
    }

    .gallery-panel {
      transition: all 0.3s ease;
    }
  }

  .mobile-layout {
    height: calc(100vh - 80px);

    .mobile-tabs {
      height: 100%;

      :deep(.el-tabs__content) {
        height: calc(100% - 40px);
        overflow-y: auto;
        padding: 0;
      }

      :deep(.el-tab-pane) {
        height: 100%;
      }
    }
  }
}

@media (max-width: 768px) {
  .desktop-layout {
    display: none !important;
  }
}

@media (min-width: 769px) {
  .mobile-layout,
  .mobile-header {
    display: none !important;
  }
}
</style>

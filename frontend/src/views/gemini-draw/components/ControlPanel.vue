<template>
  <div class="control-panel">
    <!-- 桌面端标题 -->
    <div class="control-header" v-if="!isMobile">
      <div class="header-content">
        <h1>Ezwork Studio</h1>
        <p>绘图客户端</p>
      </div>
      <!-- 设置按钮移到右上角 -->
      <el-button
        class="settings-btn-header"
        circle
        type="primary"
        size="medium"
        @click="$emit('open-settings')"
      >
        <el-icon><Setting /></el-icon>
      </el-button>
    </div>

    <!-- 模型选择 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <span class="section-title">模型选择</span>
      </template>
      <el-select
        v-model="selectedModel"
        placeholder="选择模型"
        class="w-full"
        @change="handleModelChange"
      >
        <el-option
          label="gemini-2.5-flash-image-preview (默认)"
          value="gemini-2.5-flash-image-preview"
        />
        <el-option
          label="gemini-2.5-flash-image-preview-bs"
          value="gemini-2.5-flash-image-preview-bs"
        />
        <el-option label="自定义模型" value="custom" />
      </el-select>
      <el-input
        v-if="selectedModel === 'custom'"
        v-model="customModel"
        placeholder="请输入自定义模型名称"
        class="mt-2"
      />
    </el-card>

    <!-- 提示词输入 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <span class="section-title">提示词</span>
      </template>
      <el-input
        v-model="prompt"
        type="textarea"
        :rows="3"
        placeholder="描述您想要生成的图片内容，推荐使用英文，生图成功率更高..."
        maxlength="1000"
        show-word-limit
        resize="vertical"
      />
      <div class="prompt-tip">默认会添加"请帮我画图"</div>
    </el-card>

    <!-- 图片上传 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <span class="section-title">
          上传图片（选填）
          <span class="upload-count">({{ uploadedImages.length }}/5)</span>
        </span>
      </template>
      <ImageUpload v-model="uploadedImages" :max-count="5" @error="handleUploadError" />
    </el-card>

    <!-- 生成按钮和状态 -->
    <el-card class="section-card" shadow="never">
      <el-button
        type="primary"
        size="large"
        class="generate-btn"
        :loading="loading"
        @click="handleGenerate"
        :disabled="!canGenerate"
      >
        <span v-if="!loading">提交生成</span>
        <span v-else>生成中...</span>
      </el-button>

      <!-- 注意事项 -->
      <el-alert class="mt-3" type="warning" :closable="false" show-icon>
        <template #title>
          注意，因为Google官方审核问题，您的绘图有概率会不返回图片结果，但是依旧会记录本次产生的费用。遇到此类问题，尝试重新生图即可。
        </template>
      </el-alert>

      <!-- 用时显示 -->
      <div v-if="elapsedTime" class="time-info">⏱️ 用时: {{ elapsedTime }}s</div>
    </el-card>

    <!-- 移动端设置按钮 -->
    <el-button
      v-if="isMobile"
      class="settings-btn-mobile"
      type="primary"
      @click="$emit('open-settings')"
    >
      <el-icon><Setting /></el-icon>
      <span>API设置</span>
    </el-button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting } from '@element-plus/icons-vue'
import ImageUpload from './ImageUpload.vue'
import { useResponsive } from '@/hooks/useResponsive'
import { useSettingsStore } from '@/stores/settings'
import { useGeneratorStore } from '@/stores/generator'

const { isMobile } = useResponsive()
const settingsStore = useSettingsStore()
const generatorStore = useGeneratorStore()

// Props
const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  elapsedTime: {
    type: String,
    default: '',
  },
})

// Emits
const emit = defineEmits(['generate', 'open-settings'])

// 表单数据
const selectedModel = ref(settingsStore.currentModel)
const customModel = ref('')
const prompt = ref('')

// 计算属性
const uploadedImages = computed({
  get: () => generatorStore.uploadedImages,
  set: (value) => generatorStore.setUploadedImages(value),
})

const canGenerate = computed(() => {
  return generatorStore.canGenerate(prompt.value) && settingsStore.isApiConfigured
})

// 方法
const handleModelChange = () => {
  if (selectedModel.value !== 'custom') {
    customModel.value = ''
  }

  // 保存模型选择
  const model = selectedModel.value === 'custom' ? customModel.value : selectedModel.value
  settingsStore.updateApiConfig({ model })
}

const handleGenerate = () => {
  if (!canGenerate.value) {
    if (!settingsStore.isApiConfigured) {
      ElMessage.warning('请先配置API设置')
      emit('open-settings')
      return
    }
    ElMessage.warning('请填写提示词')
    return
  }

  const model = selectedModel.value === 'custom' ? customModel.value : selectedModel.value

  if (selectedModel.value === 'custom' && !customModel.value.trim()) {
    ElMessage.warning('请输入自定义模型名称')
    return
  }

  emit('generate', {
    model,
    prompt: prompt.value,
    images: uploadedImages.value,
  })
}

const handleUploadError = (error) => {
  ElMessage.error(error)
}

// 初始化
onMounted(() => {
  // 根据设置初始化模型选择
  const currentModel = settingsStore.currentModel
  if (
    ['gemini-2.5-flash-image-preview', 'gemini-2.5-flash-image-preview-bs'].includes(currentModel)
  ) {
    selectedModel.value = currentModel
  } else {
    selectedModel.value = 'custom'
    customModel.value = currentModel
  }
})
</script>

<style lang="scss" scoped>
.control-panel {
  background: #f8f9fb;
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  position: relative;

  .control-header {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 12px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .header-content {
      flex: 1;

      h1 {
        font-size: 1.2rem;
        margin: 0 0 4px 0;
        color: #1f2937;
        font-weight: 600;
      }

      p {
        font-size: 0.8rem;
        margin: 0;
        color: #6b7280;
      }
    }

    .settings-btn-header {
      flex-shrink: 0;
      background: #64b3f9;
      border-color: #6eb5f8;

      &:hover {
        transform: rotate(90deg) scale(1.2);
      }
    }
  }

  .section-card {
    margin-bottom: 6px;
    border: 1px solid #e5e7eb;

    :deep(.el-card__header) {
      padding: 12px;
      background: #fafbfc;
      border-bottom: 1px solid #e5e7eb;
    }

    :deep(.el-card__body) {
      padding: 16px;
    }

    .section-title {
      font-weight: 500;
      color: #374151;
      font-size: 0.95rem;
    }

    .upload-count {
      color: #0b5345;
      font-weight: normal;
    }
  }

  .generate-btn {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(45deg, #0b5345, #16a085);
    border: none;

    &:hover:not(:disabled) {
      background: linear-gradient(45deg, #16a085, #0b5345);
      transform: translateY(-1px);
    }

    &:disabled {
      opacity: 0.7;
    }
  }

  .prompt-tip {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 8px;
    font-style: italic;
  }

  .time-info {
    margin-top: 12px;
    padding: 8px 12px;
    background: #f3f4f6;
    border-radius: 6px;
    font-size: 0.85rem;
    color: #374151;
    text-align: center;
  }

  // 移动端设置按钮
  .settings-btn-mobile {
    margin-top: 20px;
    width: 100%;
    border-radius: 8px;
    background: #0b5345;
    border-color: #0b5345;

    &:hover {
      background: #16a085;
      border-color: #16a085;
    }
  }
}

@media (max-width: 768px) {
  .control-panel {
    padding: 12px;

    .control-header {
      .settings-btn-header {
        transform: none !important;

        &:hover {
          transform: none !important;
        }
      }
    }
  }
}
</style>

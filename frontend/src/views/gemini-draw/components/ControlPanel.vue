<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, Edit } from '@element-plus/icons-vue'
import ImageUpload from './ImageUpload.vue'
import TranslateIcon from '@/components/icons/TranslateIcon.vue'
import { useResponsive } from '@/hooks/useResponsive'
import { useSettingsStore } from '@/stores/settings'
import { useGeneratorStore } from '@/stores/generator'
import { translateToEnglish, checkTranslationConfig } from '@/apis/translate'

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
const translating = ref(false)

// 计算属性
const uploadedImages = computed({
  get: () => generatorStore.uploadedImages,
  set: (value) => generatorStore.setUploadedImages(value),
})

const canGenerate = computed(() => {
  return generatorStore.canGenerate(prompt.value) && settingsStore.isApiConfigured
})

const canTranslate = computed(() => {
  return checkTranslationConfig()
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

// 处理翻译
const handleTranslate = async () => {
  if (!prompt.value.trim()) {
    ElMessage.warning('请先输入提示词')
    return
  }

  if (!canTranslate.value) {
    ElMessage.warning('请先配置API设置')
    emit('open-settings')
    return
  }

  translating.value = true

  try {
    const result = await translateToEnglish(prompt.value)

    if (result.success) {
      // 替换提示词内容
      prompt.value = result.data.translated
      ElMessage.success('翻译完成！')
    } else {
      ElMessage.error('翻译失败')
    }
  } catch (error) {
    console.error('Translation error:', error)
    ElMessage.error(error.message || '翻译失败，请重试')
  } finally {
    translating.value = false
  }
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

<template>
  <div class="control-panel">
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
        <div class="prompt-header">
          <span class="section-title">提示词</span>
          <el-button
            type="primary"
            size="small"
            plain
            :loading="translating"
            :disabled="!prompt.trim() || !canTranslate"
            @click="handleTranslate"
            class="translate-btn"
          >
            <el-icon> <TranslateIcon /></el-icon> 
            {{ translating ? ' 翻译中...' : ' 英文翻译' }}
          </el-button>
        </div>
      </template>
      <el-input
        v-model="prompt"
        type="textarea"
        :rows="3"
        placeholder="描述您想要生成的图片内容，推荐使用英文，生图成功率更高..."
        maxlength="8000"
        show-word-limit
        resize="vertical"
      />
      <div class="prompt-tip">默认会添加"请帮我画图"</div>
      <div v-if="!canTranslate" class="translate-tip">翻译功能需要先配置API设置</div>
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

<style lang="scss" scoped>
.control-panel {
  background: #f8f9fb;
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  position: relative;

  .section-card {
    margin-bottom: 4px;
    border: 1px solid #e5e7eb;

    :deep(.el-card__header) {
      padding: 8px;
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

    .prompt-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .translate-btn {
        border-color: #0b5345;
        color: #0b5345;

        &:hover:not(:disabled) {
          background: #0b5345;
          color: white;
        }

        &:disabled {
          opacity: 0.5;
        }
      }
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

  .translate-tip {
    font-size: 0.75rem;
    color: #f56565;
    margin-top: 6px;
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

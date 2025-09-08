<template>
  <div class="image-upload">
    <el-upload
      ref="uploadRef"
      :file-list="fileList"
      :auto-upload="false"
      :show-file-list="false"
      multiple
      accept="image/*"
      :on-change="handleFileChange"
      :before-upload="beforeUpload"
      drag
      class="upload-dragger"
    >
      <div class="upload-content">
        <el-icon class="upload-icon"><Plus /></el-icon>
        <div class="upload-text">
          <p>点击选择图片或拖拽到此处</p>
          <small>支持多选、粘贴，最多{{ maxCount }}张</small>
        </div>
      </div>
    </el-upload>

    <!-- 已上传图片预览 -->
    <div v-if="modelValue.length > 0" class="uploaded-images">
      <div v-for="(image, index) in modelValue" :key="image.id" class="uploaded-image">
        <el-image
          :src="image.dataUrl"
          :alt="image.name"
          fit="cover"
          class="image-preview"
          :preview-src-list="[image.dataUrl]"
          :initial-index="0"
          preview-teleported
        />
        <el-button class="remove-btn" circle size="small" type="danger" @click="removeImage(index)">
          <el-icon><Close /></el-icon>
        </el-button>
        <div class="image-name" :title="image.name">{{ image.name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Plus, Close } from '@element-plus/icons-vue'
import { useImageUpload } from '../hooks/useImageUpload'

// Props
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  maxCount: {
    type: Number,
    default: 5,
  },
})

// Emits
const emit = defineEmits(['update:modelValue', 'error'])

// 使用图片上传逻辑
const { processImages, validateFile } = useImageUpload()

const uploadRef = ref()
const fileList = ref([])

// 文件变化处理
const handleFileChange = async (file, fileList) => {
  const files = fileList.slice(props.modelValue.length).map((item) => item.raw)

  if (props.modelValue.length + files.length > props.maxCount) {
    emit('error', `最多只能上传${props.maxCount}张图片`)
    // 重置文件列表
    uploadRef.value?.clearFiles()
    return
  }

  try {
    const processedImages = await processImages(files)
    emit('update:modelValue', [...props.modelValue, ...processedImages])
    // 清空文件列表以允许重复选择
    uploadRef.value?.clearFiles()
  } catch (error) {
    emit('error', error.message)
    uploadRef.value?.clearFiles()
  }
}

// 上传前验证
const beforeUpload = (file) => {
  try {
    return validateFile(file)
  } catch (error) {
    emit('error', error.message)
    return false
  }
}

// 移除图片
const removeImage = (index) => {
  const newImages = [...props.modelValue]
  newImages.splice(index, 1)
  emit('update:modelValue', newImages)
}

// 监听粘贴事件
const handlePaste = async (event) => {
  const items = event.clipboardData?.items
  if (!items) return

  const files = []
  for (let item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) files.push(file)
    }
  }

  if (files.length > 0) {
    event.preventDefault()

    if (props.modelValue.length + files.length > props.maxCount) {
      emit('error', `最多只能上传${props.maxCount}张图片`)
      return
    }

    try {
      const processedImages = await processImages(files)
      emit('update:modelValue', [...props.modelValue, ...processedImages])
    } catch (error) {
      emit('error', error.message)
    }
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('paste', handlePaste)
})

onUnmounted(() => {
  document.removeEventListener('paste', handlePaste)
})
</script>

<style lang="scss" scoped>
.image-upload {
  .upload-dragger {
    width: 100%;

    :deep(.el-upload-dragger) {
      border: 2px dashed #d1d5db;
      border-radius: 8px;
      background: #fafbfc;
      width: 100%;
      height: auto;
      padding: 20px;

      &:hover {
        border-color: #0b5345;
        background: rgba(11, 83, 69, 0.05);
      }

      &.is-dragover {
        border-color: #0b5345;
        background: rgba(11, 83, 69, 0.1);
      }
    }
  }

  .upload-content {
    text-align: center;

    .upload-icon {
      font-size: 2rem;
      color: #c0c4cc;
      margin-bottom: 10px;
    }

    .upload-text {
      color: #606266;

      p {
        margin: 0 0 5px 0;
        font-size: 14px;
      }

      small {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .uploaded-images {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 10px;
    margin-top: 15px;

    .uploaded-image {
      position: relative;
      border-radius: 8px;
      overflow: hidden;
      background: #f8f9fa;
      border: 1px solid #e1e5e9;

      .image-preview {
        width: 100%;
        height: 80px;
        cursor: pointer;
      }

      .remove-btn {
        position: absolute;
        top: 4px;
        right: 4px;
        width: 20px;
        height: 20px;
        min-height: 20px;
        padding: 0;
        z-index: 10;
      }

      .image-name {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
        color: white;
        font-size: 10px;
        padding: 4px;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
  }
}

@media (max-width: 768px) {
  .image-upload {
    .uploaded-images {
      grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
      gap: 8px;

      .uploaded-image {
        .image-preview {
          height: 60px;
        }

        .remove-btn {
          width: 16px;
          height: 16px;
          min-height: 16px;
          top: 2px;
          right: 2px;
        }

        .image-name {
          font-size: 9px;
          padding: 2px;
        }
      }
    }
  }
}
</style>

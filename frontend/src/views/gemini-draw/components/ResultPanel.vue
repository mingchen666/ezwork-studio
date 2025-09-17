<template>
  <div class="result-panel">
    <el-card class="result-card" shadow="never">
      <template #header>
        <div class="header-content">
          <span class="section-title">生成结果</span>
          <div class="action-buttons">
            <!-- 修改此图按钮 -->
            <el-button
              type="success"
              size="small"
              @click="editCurrentImage"
              class="edit-btn"
              :disabled="!resultImage"
            >
              <el-icon><Edit /></el-icon>
              修改此图
            </el-button>
            <!-- 下载按钮移到右上角 -->
            <el-button type="primary" size="small" @click="downloadImage" class="download-btn">
              <el-icon><Download /></el-icon>
              下载图片
            </el-button>
          </div>
        </div>
      </template>

      <div class="result-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <p>正在生成图片，请稍候...</p>
        </div>
        <div v-else>
          <!-- 预览状态 -->
          <div v-if="!resultImage" class="preview-state">
            <div class="preview-container">
              <el-image
                src="src/assets/images/nano-banana-1.webp"
                alt="预览图片"
                fit="cover"
                class="preview-image"
              />
              <div class="preview-overlay">
                <div class="preview-content">
                  <div class="preview-text">预览示例</div>
                  <div class="preview-subtitle">生成结果将显示在这里</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 结果显示 -->
          <div v-else class="result-content">
            <el-image
              :src="resultImage"
              alt="生成的图片"
              fit="contain"
              class="result-image"
              :preview-src-list="[resultImage]"
              :initial-index="0"
              preview-teleported
            >
              <template #error>
                <div class="image-slot">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </div>
        </div>
      </div>

      <!-- 模型回复 -->
      <div v-if="modelResponse" class="model-response">
        <h4>模型回复:</h4>
        <p>{{ modelResponse }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { Loading, Download, Picture, Edit } from '@element-plus/icons-vue'
import { useGeneratorStore } from '@/stores/generator'
import { urlToBase64Service } from '@/apis/images'
// Props - 保持原有的props接口
const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  resultImage: {
    type: String,
    default: '',
  },
  modelResponse: {
    type: String,
    default: '',
  },
  elapsedTime: {
    type: String,
    default: '',
  },
})

// 使用 generator store
const generatorStore = useGeneratorStore()

// 下载图片
const downloadImage = () => {
  if (!props.resultImage) {
    ElMessage.error('没有可下载的图片！')
    return
  }

  try {
    const link = document.createElement('a')
    link.href = props.resultImage
    link.download = `ai-generated-image-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('图片下载成功！')
  } catch (error) {
    console.error('Download error:', error)
    ElMessage.error('图片下载失败！')
  }
}

// 修改此图 - 将当前结果图片添加到上传区域
const editCurrentImage = async () => {
  if (!props.resultImage) {
    ElMessage.error('没有可编辑的图片！')
    return
  }

  let loadingMessage = null

  try {
    // 检查上传图片数量限制
    const currentImages = generatorStore.uploadedImages
    if (currentImages.length >= 5) {
      ElMessage.error('上传图片数量已达上限（5张），请先删除一些图片')
      return
    }

    // 显示处理中的消息
    loadingMessage = ElMessage({
      message: '正在处理图片...',
      type: 'info',
      duration: 0,
      showClose: false,
    })

    console.log('开始处理图片URL:', props.resultImage)

    // 调用后端API将URL转换为base64
    const response = await urlToBase64Service(props.resultImage)

    console.log('后端API响应:', response)

    // 关闭加载消息
    if (loadingMessage) {
      loadingMessage.close()
      loadingMessage = null
    }

    if (response && response.code === 200 && response.data) {
      // 创建文件名
      const fileName = `ai-generated-${Date.now()}.png`

      // 按照useImageUpload的数据结构创建图片对象
      const processedImage = {
        id: Date.now() + Math.random(),
        name: fileName,
        base64: response.data.base64, // 纯base64数据
        mimeType: response.data.mimeType || 'image/png', // MIME类型
        dataUrl: response.data.dataUrl, // 完整的data URL
        size: response.data.size || 0, // 文件大小
      }

      console.log('准备添加图片到上传区域:', processedImage)
      console.log('当前上传的图片数量:', currentImages.length)

      // 添加到上传图片列表
      const newImages = [...currentImages, processedImage]
      generatorStore.setUploadedImages(newImages)

      console.log('图片已添加，新的图片列表长度:', newImages.length)

      // 显示成功消息
      ElMessage.success('图片已添加到上传区域，可以继续修改！')
    } else {
      const errorMsg = response?.message || '图片转换失败，请重试'
      console.error('API调用失败:', errorMsg, response)
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('Edit image error:', error)
    // 确保在任何错误情况下都关闭加载消息
    if (loadingMessage) {
      loadingMessage.close()
    }
    ElMessage.error('图片处理失败，请重试: ' + error.message)
  }
}
</script>

<style lang="scss" scoped>
.result-panel {
  padding: 10px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .result-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    :deep(.el-card__header) {
      padding: 10px 12px;
      background: #fafbfc;
      border-bottom: 1px solid #e5e7eb;
      flex-shrink: 0;
    }

    :deep(.el-card__body) {
      flex: 1;
      padding: 16px;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      min-height: 0;
    }

    .header-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;

      .section-title {
        font-weight: 500;
        color: #374151;
        font-size: 0.95rem;
      }

      .action-buttons {
        display: flex;
        gap: 8px;
      }

      .edit-btn {
        background: linear-gradient(45deg, #10b981, #059669);
        border: none;

        &:hover:not(:disabled) {
          background: linear-gradient(45deg, #059669, #047857);
          transform: translateY(-1px);
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }

      .download-btn {
        background: linear-gradient(45deg, #4089f8, #1875f6);
        border: none;

        &:hover {
          background: linear-gradient(45deg, #16a085, #0b5345);
          transform: translateY(-1px);
        }
      }
    }
  }

  .result-container {
    flex: 1;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    min-height: 300px;
    border-radius: 12px;
    overflow-y: auto;
    max-height: none;
    padding: 12px;
  }

  .loading-state {
    text-align: center;
    color: #6b7280;

    .loading-icon {
      font-size: 3rem;
      color: #0b5345;
      margin-bottom: 16px;
      animation: spin 1s linear infinite;
    }

    p {
      font-size: 16px;
      margin: 0;
    }
  }

  .preview-state {
    width: 100%;
    text-align: center;

    .preview-container {
      position: relative;
      display: inline-block;
      width: 100%;

      .preview-image {
        width: 100%;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
      }

      .preview-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 12px;
        color: white;

        .preview-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          padding: 20px;

          .preview-text {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 12px;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
            letter-spacing: 0.5px;
          }

          .preview-subtitle {
            font-size: 15px;
            opacity: 0.95;
            line-height: 1.5;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
            max-width: 200px;
          }
        }
      }
    }
  }

  .result-content {
    width: 100%;
    height: auto;
    text-align: center;
    overflow-y: auto;
    max-height: 100%;

    .result-image {
      width: calc(100% - 32px);
      height: auto;
      max-height: none;
      cursor: pointer;
      object-fit: contain;
      border-radius: 12px;
      margin: 16px;
      border: none;
      box-shadow: none;
      background: transparent;
    }
  }

  .model-response {
    margin-top: 12px;
    padding: 10px 16px;
    background: #f1f3f4;
    border-radius: 8px;
    border-left: 4px solid #0b5345;
    flex-shrink: 0;
    max-height: 200px;
    overflow-y: auto;

    h4 {
      margin: 0 0 8px 0;
      color: #333;
      font-size: 14px;
    }

    p {
      margin: 0;
      color: #555;
      line-height: 1.6;
      font-size: 14px;
      word-wrap: break-word;
    }
  }
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
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .result-panel {
    padding: 12px;

    .result-container {
      padding: 15px;
      min-height: 150px;
    }

    .result-content {
      .result-image {
        max-height: 50vh;
      }
    }

    .preview-state .preview-container {
      .preview-overlay {
        .preview-text {
          font-size: 16px;
        }

        .preview-subtitle {
          font-size: 12px;
        }
      }
    }

    .header-content {
      .action-buttons {
        gap: 6px;

        .edit-btn,
        .download-btn {
          font-size: 12px;
          padding: 6px 12px;

          .el-icon {
            font-size: 14px;
          }
        }
      }
    }
  }
}
</style>

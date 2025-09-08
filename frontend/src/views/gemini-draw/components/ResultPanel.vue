<template>
  <div class="result-panel">
    <el-card class="result-card" shadow="never">
      <template #header>
        <div class="header-content">
          <span class="section-title">生成结果</span>
          <!-- 下载按钮移到右上角 -->
          <el-button type="primary" size="small" @click="downloadImage" class="download-btn">
            <el-icon><Download /></el-icon>
            下载图片
          </el-button>
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
                <div class="preview-text">预览示例</div>
                <div class="preview-subtitle">生成结果将显示在这里</div>
              </div>
            </div>
          </div>

          <!-- 结果显示 -->
          <div v-else class="result-content">
            <el-image
              :src="resultImage"
              alt="生成的图片"
              fit="cover"
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
import { Loading, Download, Picture } from '@element-plus/icons-vue'
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
</script>

<style lang="scss" scoped>
.result-panel {
  padding: 10px;
  height: 100%;
  overflow-y: auto;

  .result-card {
    height: 100%;
    display: flex;
    flex-direction: column;

    :deep(.el-card__header) {
      padding: 12px 16px;
      background: #fafbfc;
      border-bottom: 1px solid #e5e7eb;
    }

    :deep(.el-card__body) {
      flex: 1;
      padding: 16px;
      display: flex;
      flex-direction: column;
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
    align-items: center;
    justify-content: center;
    min-height: 300px;
    border-radius: 12px;
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
        background: rgba(0, 0, 0, 0.3);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-radius: 12px;
        color: white;

        .preview-text {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 8px;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }

        .preview-subtitle {
          font-size: 14px;
          opacity: 0.9;
          text-align: center;
          line-height: 1.4;
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }
      }
    }
  }

  .result-content {
    width: 100%;
    height: auto;
    text-align: center;
    // transform: scale(0.8);

    .result-image {
      width: 100%;
       height: auto;
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
      cursor: pointer;
      object-fit: cover;
    }
  }

  .model-response {
    margin-top: 20px;
    padding: 16px;
    background: #f1f3f4;
    border-radius: 8px;
    border-left: 4px solid #0b5345;

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
</style>

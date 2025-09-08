<template>
  <div class="gallery-panel" :class="{ collapsed: isCollapsed }">
    <el-card class="gallery-card" shadow="never">
      <template #header>
        <div class="gallery-header">
          <div class="header-content">
            <span class="section-title" v-if="!isCollapsed">历史图库</span>
            <span class="gallery-count" v-if="!isCollapsed">({{ imageCount }}/{{ maxCount }})</span>
          </div>
          <el-button
            class="collapse-btn"
            circle
            size="small"
            @click="toggleCollapse"
            :title="isCollapsed ? '展开图库' : '折叠图库'"
          >
            <el-icon>
              <ArrowLeft v-if="!isCollapsed" />
              <ArrowRight v-else />
            </el-icon>
          </el-button>
        </div>
      </template>

      <div class="gallery-content">
        <!-- 空状态 -->
        <div v-if="imageCount === 0" class="gallery-empty">
          <el-empty
            :description="isCollapsed ? '' : '暂无历史记录'"
            :image-size="isCollapsed ? 40 : 80"
          />
        </div>

        <!-- 折叠状态 - 小图标列表 -->
        <div v-else-if="isCollapsed" class="gallery-collapsed">
          <div
            v-for="item in displayImages"
            :key="item.id"
            class="collapsed-item"
            :class="{ selected: selectedImage?.id === item.id }"
            @click="selectImage(item)"
            :title="item.promptPreview"
          >
            <el-image
              :src="item.imageUrl"
              alt="Generated Image"
              fit="cover"
              class="collapsed-image"
              loading="lazy"
            />
          </div>

          <!-- 显示更多指示器 -->
          <div v-if="imageCount > 6" class="more-indicator">
            <span>+{{ imageCount - 6 }}</span>
          </div>
        </div>

        <!-- 展开状态 - 详细列表 -->
        <div v-else class="gallery-expanded">
          <div
            v-for="item in displayImages"
            :key="item.id"
            class="expanded-item"
            :class="{ selected: selectedImage?.id === item.id }"
            @click="selectImage(item)"
          >
            <div class="item-image">
              <el-image
                :src="item.imageUrl"
                alt="Generated Image"
                fit="cover"
                class="expanded-image"
                loading="lazy"
                :preview-src-list="[item.imageUrl]"
                :initial-index="0"
                preview-teleported
              />
            </div>

            <div class="item-content">
              <div class="item-title" :title="item.prompt">
                {{ item.promptPreview }}
              </div>
              <div class="item-meta">
                <span class="item-model">{{ item.model }}</span>
                <span class="item-time">{{ formatDateTime(item.timestamp) }}</span>
                <span class="item-elapsed">{{ item.elapsedTime }}s</span>
              </div>
            </div>

            <el-button
              class="delete-btn"
              circle
              size="medium"
              type="danger"
              @click.stop="deleteImage(item.id)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 操作按钮 - 只在展开状态显示 -->
        <!-- <div v-if="imageCount > 0 && !isCollapsed" class="gallery-actions">
          <el-button type="danger" size="medium" plain @click="clearAll"> 清空图库 </el-button>
        </div> -->
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { useGalleryStore } from '@/stores/gallery'

// Emits
const emit = defineEmits(['select-image'])

// 使用图库store
const galleryStore = useGalleryStore()

// 计算属性
const displayImages = computed(() => galleryStore.displayImages)
const imageCount = computed(() => galleryStore.imageCount)
const maxCount = computed(() => galleryStore.maxCount)
const selectedImage = computed(() => galleryStore.selectedImage)
const isCollapsed = computed(() => galleryStore.isCollapsed)

// 方法
const toggleCollapse = () => {
  galleryStore.toggleCollapse()
}

const selectImage = (imageData) => {
  galleryStore.selectImage(imageData.id)
  emit('select-image', imageData)
}

const deleteImage = async (imageId) => {
  try {
    await ElMessageBox.confirm('确定要删除这张图片吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const result = await galleryStore.removeImage(imageId)
    if (result.success) {
      ElMessage.success('图片已删除')
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch {
    // 用户取消删除
  }
}

const clearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有图片吗？此操作不可恢复。', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    galleryStore.clearAll()
    ElMessage.success('图库已清空')
  } catch {
    // 用户取消
  }
}

// 格式化日期时间 - 显示月日时分
const formatDateTime = (timestamp) => {
  if (!timestamp) return ''

  try {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    if (timestamp.includes(' ')) {
      return timestamp
    }
    return timestamp
  }
}
</script>

<style lang="scss" scoped>
.gallery-panel {
  padding: 10px;
  height: 100%;
  overflow: hidden;
  transition: all 0.3s ease;

  &.collapsed {
    padding: 16px 8px;
    // overflow: hidden;
  }

  .gallery-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    border: 1px solid #e5e7eb;

    :deep(.el-card__header) {
      padding: 12px 16px;
      background: #fafbfc;
      border-bottom: 1px solid #e5e7eb;
    }

    :deep(.el-card__body) {
      flex: 1;
      padding: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
  }

  .gallery-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .header-content {
      display: flex;
      align-items: center;
      gap: 8px;

      .section-title {
        font-weight: 500;
        color: #374151;
        font-size: 0.95rem;
      }

      .gallery-count {
        font-size: 0.8rem;
        color: #6b7280;
      }
    }

    .collapse-btn {
      background: #f3f4f6;
      border-color: #d1d5db;
      color: #6b7280;

      &:hover {
        background: #0b5345;
        border-color: #0b5345;
        color: white;
      }
    }
  }

  .gallery-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .gallery-empty {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  // 折叠状态样式
  .gallery-collapsed {
    display: flex;
    flex-direction: column;
    gap: 8px;
    overflow-y: auto;
    overflow-x: hidden; //隐藏横向滚动条

    .collapsed-item {
      width: 48px;
      height: 48px;
      border-radius: 6px;
      overflow: hidden;
      cursor: pointer;
      border: 2px solid #e5e7eb;
      transition: all 0.3s ease;
      flex-shrink: 0;

      &:hover {
        border-color: #0b5345;
        transform: scale(1.05);
      }

      &.selected {
        border-color: #0b5345;
        box-shadow: 0 0 0 2px rgba(11, 83, 69, 0.2);
      }

      .collapsed-image {
        width: 100%;
        height: 100%;
      }
    }

    .more-indicator {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 32px;
      background: #f3f4f6;
      border-radius: 6px;
      font-size: 12px;
      color: #6b7280;
      font-weight: 500;
    }
  }

  // 展开状态样式
  .gallery-expanded {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 6px;

    .expanded-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 4px;
      border: 2px solid #e5e7eb;
      background: #f9fafb;
      cursor: pointer;
      transition: all 0.3s ease;
      position: relative;

      &:hover {
        border-color: #0b5345;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

        .delete-btn {
          opacity: 1;
        }
      }

      &.selected {
        border-color: #0b5345;
        background: rgba(11, 83, 69, 0.05);
        box-shadow: 0 0 0 2px rgba(11, 83, 69, 0.2);
      }

      .item-image {
        flex-shrink: 0;
        width: 60px;
        height: 60px;
        border-radius: 6px;
        overflow: hidden;

        .expanded-image {
          width: 100%;
          height: 100%;
        }
      }

      .item-content {
        flex: 1;
        min-width: 0;

        .item-title {
          font-size: 14px;
          font-weight: 500;
          color: #374151;
          margin-bottom: 4px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .item-meta {
          display: flex;
          flex-direction: column;
          gap: 2px;

          .item-model {
            font-size: 11px;
            color: #9ca3af;
            font-style: italic;
          }

          .item-time {
            font-size: 12px;
            color: #6b7280;
          }

          .item-elapsed {
            font-size: 11px;
            color: #059669;
            font-weight: 500;
          }
        }
      }

      .delete-btn {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 20px;
        height: 20px;
        min-height: 20px;
        padding: 0;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 10;
      }
    }
  }

  .gallery-actions {
    margin-top: 4px;
    text-align: center;
    padding-top: 10px;
    border-top: 1px solid #e5e7eb;
  }
}

// 折叠状态下的特殊样式
.collapsed {
  .gallery-card {
    :deep(.el-card__header) {
      padding: 8px;
    }

    :deep(.el-card__body) {
      padding: 8px;
    }
  }
}

@media (max-width: 768px) {
  .gallery-panel {
    padding: 12px;

    &.collapsed {
      padding: 12px 8px;
    }

    .gallery-expanded {
      .expanded-item {
        padding: 8px;
        gap: 8px;

        .item-image {
          width: 50px;
          height: 50px;
        }

        .item-content {
          .item-title {
            font-size: 13px;
            margin-bottom: 3px;
          }

          .item-meta {
            gap: 1px;

            .item-model {
              font-size: 10px;
            }

            .item-time {
              font-size: 11px;
            }

            .item-elapsed {
              font-size: 10px;
            }
          }
        }

        .delete-btn {
          opacity: 1;
          width: 18px;
          height: 18px;
          min-height: 18px;
          top: 4px;
          right: 4px;
        }
      }
    }

    .gallery-collapsed {
      .collapsed-item {
        width: 40px;
        height: 40px;
      }

      .more-indicator {
        width: 40px;
        height: 28px;
        font-size: 11px;
      }
    }
  }
}
</style>

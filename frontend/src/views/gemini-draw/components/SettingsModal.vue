<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Close } from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'
import { useUserStore } from '@/stores/user'
import { useResponsive } from '@/hooks/useResponsive'
import { useRouter } from 'vue-router'

const settingsStore = useSettingsStore()
const userStore = useUserStore()
const { isMobile } = useResponsive()
const router = useRouter()

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

// Emits
const emit = defineEmits(['update:modelValue', 'save'])

// 响应式数据
const visible = ref(false)
const saving = ref(false)
const formRef = ref()

// 表单数据
const form = ref({
  baseUrl: '',
  apiKey: '',
  translationModel: 'gpt-4.1',
})

// 计算属性
const isConfigured = computed(() => settingsStore.isApiConfigured)

// 响应式计算属性
const dialogWidth = computed(() => {
  return isMobile.value ? '90%' : '500px'
})

const labelWidth = computed(() => {
  return isMobile.value ? '80px' : '120px'
})

// 表单验证规则
const rules = {
  baseUrl: [
    { required: true, message: '请输入API Base URL', trigger: 'blur' },
    {
      pattern: /^https?:\/\/.+/,
      message: '请输入有效的URL地址',
      trigger: 'blur',
    },
  ],
  apiKey: [
    { required: true, message: '请输入API Key', trigger: 'blur' },
    { min: 10, message: 'API Key长度不能少于10位', trigger: 'blur' },
  ],
}

// 监听显示状态
watch(
  () => props.modelValue,
  (newVal) => {
    visible.value = newVal
    if (newVal) {
      loadSettings()
    }
  },
)

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 加载设置
const loadSettings = () => {
  const config = settingsStore.apiConfig
  form.value = {
    baseUrl: config.baseUrl || 'https://api.juheai.top',
    apiKey: config.apiKey || '',
    translationModel: config.translationModel || 'gpt-4.1',
  }
}

// 保存设置
const handleSave = async () => {
  try {
    await formRef.value?.validate()

    saving.value = true

    // 保存到store
    settingsStore.updateApiConfig({
      baseUrl: form.value.baseUrl.trim(),
      apiKey: form.value.apiKey.trim(),
      translationModel: form.value.translationModel.trim(),
    })

    // 延迟一下模拟保存过程
    await new Promise((resolve) => setTimeout(resolve, 500))

    emit('save', settingsStore.apiConfig)
    visible.value = false
  } catch (error) {
    console.error('Settings save error:', error)
  } finally {
    saving.value = false
  }
}

// 关闭弹窗
const handleClose = () => {
  visible.value = false
}

// 打开API Key获取页面
const openApiKeyPage = () => {
  window.open('https://www.juhenext.com/zh/price', '_blank')
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '确认退出', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    userStore.logout()
    ElMessage.success('已退出登录')
    visible.value = false

    // 跳转到登录页面
    router.push('/auth')
  } catch {
    // 用户取消
  }
}
</script>

<template>
  <el-dialog
    v-model="visible"
    title="API设置"
    top="5vh"
    :width="dialogWidth"
    :before-close="handleClose"
    destroy-on-close
    :class="{ 'mobile-dialog': isMobile, 'custom-settings-dialog': true }"
  >
    <template #header>
      <div class="custom-dialog-header">
        <div class="header-left">
          <div class="header-icon">
            <el-icon><Setting /></el-icon>
          </div>
          <span class="header-title">API设置</span>
        </div>
      </div>
    </template>

    <div class="custom-dialog-body">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="custom-form">
        <div class="form-section">
          <el-form-item label="API Base URL:" prop="baseUrl">
            <el-input v-model="form.baseUrl" placeholder="https://api.juheai.top" />
          </el-form-item>

          <el-form-item label="API Key:" prop="apiKey">
            <el-input
              v-model="form.apiKey"
              type="password"
              placeholder="请输入您的API Key"
              show-password
            />
            <div class="form-item-extra">
              <el-button
                type="primary"
                plain
                size="small"
                @click="openApiKeyPage"
                class="get-key-btn"
              >
                立即获取
              </el-button>
            </div>
          </el-form-item>

          <!-- 翻译模型选择 -->
          <el-form-item label="翻译模型:">
            <el-select
              v-model="form.translationModel"
              placeholder="选择翻译模型"
              style="width: 100%"
            >
              <el-option label="gpt-4.1 (推荐)" value="gpt-4.1" />
              <el-option label="gpt-4.1-mini" value="gpt-4.1-mini" />
              <el-option label="gpt-4.1-nano" value="gpt-4.1-nano" />
            </el-select>
            <div class="form-item-tip">用于提示词的英文翻译功能</div>
          </el-form-item>

          <!-- 配置状态显示 -->
          <el-form-item label="配置状态:">
            <el-tag :type="isConfigured ? 'success' : 'warning'">
              {{ isConfigured ? '已配置' : '未配置' }}
            </el-tag>
          </el-form-item>
        </div>
      </el-form>
    </div>

    <template #footer>
      <div class="custom-dialog-footer">
        <el-button
          v-if="userStore.isAuthenticated"
          type="danger"
          plain
          @click="handleLogout"
          class="logout-btn"
        >
          退出登录
        </el-button>
        <div class="footer-actions">
          <el-button @click="handleClose"> 取消 </el-button>
          <el-button type="primary" @click="handleSave" :loading="saving"> 保存设置 </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<style lang="scss" scoped>
// 自定义弹窗样式
:deep(.custom-settings-dialog) {
  .el-dialog {
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .el-dialog__header {
    padding: 0;
    margin: 0;
  }

  .el-dialog__body {
    padding: 0;
  }

  .el-dialog__footer {
    padding: 0;
  }
}

// 自定义头部样式
.custom-dialog-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  border-radius: 8px 8px 0 0;

  .header-left {
    display: flex;
    align-items: center;
    gap: 10px;

    .header-icon {
      width: 24px;
      height: 24px;
      border-radius: 4px;
      background: #e5e7eb;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #6b7280;

      .el-icon {
        font-size: 14px;
      }
    }

    .header-title {
      font-size: 16px;
      font-weight: 600;
      color: #1f2937;
    }
  }
}

// 自定义弹窗主体
.custom-dialog-body {
  padding: 12px;

  .form-section {
    .el-form-item {
      margin-bottom: 12px;

      &:last-child {
        margin-bottom: 0;
      }

      :deep(.el-form-item__label) {
        font-weight: 500;
        color: #374151;
        margin-bottom: 6px;
        padding: 0;
      }

      .form-item-extra {
        margin-top: 8px;

        .get-key-btn {
          font-size: 12px;
          padding: 6px 12px;
        }
      }

      .form-item-tip {
        margin-top: 6px;
        font-size: 12px;
        color: #6b7280;
        line-height: 1.4;
      }
    }
  }
}

// 自定义底部样式
.custom-dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid #a4a7a7;
  border-radius: 0 0 8px 8px;

  .logout-btn {
    font-size: 13px;
    padding: 8px 16px;
  }

  .footer-actions {
    display: flex;
    gap: 12px;

    .el-button {
      padding: 8px 20px;
    }
  }
}

// 移动端适配
@media (max-width: 768px) {
  :deep(.mobile-dialog.custom-settings-dialog) {
    margin: 20px !important;
    max-height: calc(100vh - 40px);

    .el-dialog {
      border-radius: 8px;
    }
  }

  .custom-dialog-header {
    padding: 14px 16px;

    .header-left {
      gap: 8px;

      .header-icon {
        width: 22px;
        height: 22px;

        .el-icon {
          font-size: 13px;
        }
      }

      .header-title {
        font-size: 15px;
      }
    }
  }

  .custom-dialog-body {
    padding: 16px;
    max-height: calc(100vh - 220px);
    overflow-y: auto;

    .form-section {
      .el-form-item {
        margin-bottom: 14px;

        :deep(.el-form-item__label) {
          font-size: 13px;
          margin-bottom: 5px;
        }

        .form-item-extra {
          margin-top: 6px;

          .get-key-btn {
            font-size: 11px;
            padding: 5px 10px;
          }
        }

        .form-item-tip {
          font-size: 11px;
          margin-top: 5px;
        }
      }
    }
  }

  .custom-dialog-footer {
    padding: 14px 16px;
    flex-direction: column;
    gap: 10px;

    .logout-btn {
      width: 100%;
      padding: 8px 16px;
      font-size: 12px;
    }

    .footer-actions {
      width: 100%;
      gap: 10px;

      .el-button {
        flex: 1;
        padding: 8px 16px;
        font-size: 13px;
      }
    }
  }
}

// 小屏幕设备（手机竖屏）
@media (max-width: 480px) {
  :deep(.mobile-dialog.custom-settings-dialog) {
    margin: 10px !important;
    max-height: calc(100vh - 20px);
  }

  .custom-dialog-header {
    padding: 12px 14px;
  }

  .custom-dialog-body {
    padding: 14px;
  }

  .custom-dialog-footer {
    padding: 12px 14px;
  }
}
</style>

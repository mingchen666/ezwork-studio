<template>
  <el-dialog
    v-model="visible"
    title="API设置"
    :width="dialogWidth"
    :before-close="handleClose"
    destroy-on-close
    :class="{ 'mobile-dialog': isMobile }"
  >
    <template #header>
      <div class="dialog-header">
        <el-icon><Setting /></el-icon>
        <span>API设置</span>
      </div>
    </template>
    
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      :label-width="labelWidth"
      label-position="left"
    >
      <el-form-item label="API Base URL" prop="baseUrl">
        <el-input
          v-model="form.baseUrl"
          placeholder="例如: https://api.juheai.top"
          clearable
        />
      </el-form-item>
      
      <el-form-item label="API Key" prop="apiKey">
        <el-input
          v-model="form.apiKey"
          type="password"
          placeholder="请输入您的API Key"
          show-password
          clearable
        />
        <div class="form-item-extra">
          <el-button
            type="primary"
            link
            @click="openApiKeyPage"
          >
            立即获取 API Key
          </el-button>
        </div>
      </el-form-item>

      <!-- 配置状态显示 -->
      <el-form-item label="配置状态">
        <el-tag :type="isConfigured ? 'success' : 'warning'">
          {{ isConfigured ? '已配置' : '未配置' }}
        </el-tag>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          保存设置
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting } from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'
import { useResponsive } from '@/hooks/useResponsive'

const settingsStore = useSettingsStore()
const { isMobile } = useResponsive()

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
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
  apiKey: ''
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
      trigger: 'blur' 
    }
  ],
  apiKey: [
    { required: true, message: '请输入API Key', trigger: 'blur' },
    { min: 10, message: 'API Key长度不能少于10位', trigger: 'blur' }
  ]
}

// 监听显示状态
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    loadSettings()
  }
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 加载设置
const loadSettings = () => {
  const config = settingsStore.apiConfig
  form.value = {
    baseUrl: config.baseUrl || 'https://api.juheai.top',
    apiKey: config.apiKey || ''
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
      apiKey: form.value.apiKey.trim()
    })
    
    // 延迟一下模拟保存过程
    await new Promise(resolve => setTimeout(resolve, 500))
    
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
</script>

<style lang="scss" scoped>
.dialog-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.form-item-extra {
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-dialog) {
  border-radius: 12px;
}

:deep(.el-dialog__header) {
  padding: 20px 20px 10px 20px;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  padding: 10px 20px 20px 20px;
  border-top: 1px solid #e4e7ed;
}

// 移动端适配
@media (max-width: 768px) {
  :deep(.mobile-dialog) {
    margin: 20px !important;
    max-height: calc(100vh - 40px);
    
    .el-dialog__header {
      padding: 16px 16px 8px 16px;
      
      .dialog-header {
        font-size: 14px;
      }
    }
    
    .el-dialog__body {
      padding: 16px;
      max-height: calc(100vh - 200px);
      overflow-y: auto;
      
      .el-form {
        .el-form-item {
          margin-bottom: 16px;
          
          .el-form-item__label {
            font-size: 14px;
            line-height: 1.4;
            padding-right: 8px;
          }
          
          .el-form-item__content {
            .el-input {
              .el-input__wrapper {
                font-size: 14px;
              }
            }
            
            .el-tag {
              font-size: 12px;
            }
          }
        }
      }
    }
    
    .el-dialog__footer {
      padding: 8px 16px 16px 16px;
      
      .dialog-footer {
        gap: 8px;
        
        .el-button {
          flex: 1;
          font-size: 14px;
        }
      }
    }
  }
}

// 小屏幕设备（手机竖屏）
@media (max-width: 480px) {
  :deep(.mobile-dialog) {
    margin: 10px !important;
    max-height: calc(100vh - 20px);
    
    .el-dialog__header {
      padding: 12px 12px 6px 12px;
    }
    
    .el-dialog__body {
      padding: 12px;
      
      .el-form {
        .el-form-item {
          margin-bottom: 12px;
          
          .el-form-item__label {
            font-size: 13px;
          }
          
          .el-form-item__content {
            .el-input {
              .el-input__wrapper {
                font-size: 13px;
              }
            }
          }
        }
      }
    }
    
    .el-dialog__footer {
      padding: 6px 12px 12px 12px;
      
      .dialog-footer {
        .el-button {
          font-size: 13px;
          padding: 8px 16px;
        }
      }
    }
  }
}
</style>

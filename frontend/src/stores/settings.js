import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', () => {
  // 状态
  const baseUrl = ref('https://api.juheai.top')
  const apiKey = ref('')
  const model = ref('gemini-2.5-flash-image-preview')
  const version = ref('1.0.2')
  const theme = ref('light')
  const language = ref('zh-CN')

  // 计算属性
  const isApiConfigured = computed(() => {
    return !!(baseUrl.value && apiKey.value)
  })

  const currentModel = computed(() => {
    return model.value || 'gemini-2.5-flash-image-preview'
  })

  const apiConfig = computed(() => ({
    baseUrl: baseUrl.value,
    apiKey: apiKey.value,
    model: model.value
  }))

  // 动作
  const updateApiConfig = (config) => {
    if (config.baseUrl !== undefined) {
      baseUrl.value = config.baseUrl
    }
    if (config.apiKey !== undefined) {
      apiKey.value = config.apiKey
    }
    if (config.model !== undefined) {
      model.value = config.model
    }
  }

  const resetApiConfig = () => {
    baseUrl.value = 'https://api.juheai.top'
    apiKey.value = ''
    model.value = 'gemini-2.5-flash-image-preview'
  }

  const updateVersion = (newVersion) => {
    version.value = newVersion
  }

  const checkVersionUpdate = (newVersion) => {
    if (version.value !== newVersion) {
      updateVersion(newVersion)
      return true
    }
    return false
  }

  return {
    // 状态
    baseUrl,
    apiKey,
    model,
    version,
    theme,
    language,

    // 计算属性
    isApiConfigured,
    currentModel,
    apiConfig,

    // 动作
    updateApiConfig,
    resetApiConfig,
    updateVersion,
    checkVersionUpdate
  }
}, {
  persist: {
    key: 'ai-image-generator-settings',
    storage: localStorage,
    pick: ['baseUrl', 'apiKey', 'model', 'version', 'theme', 'language']
  }
})

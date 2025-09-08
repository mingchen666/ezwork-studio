
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSystemStore = defineStore('system', () => {
  // 系统设置
  const settings = ref({
    // 界面设置
    theme: 'light',
    language: 'zh-CN',
    animations: true,
    compactMode: false,

    // 性能设置
    maxConcurrentTasks: 3,
    autoSaveHistory: true,
    maxHistoryItems: 1000,
    imagePreload: true,

    // 默认设置
    defaultImageSize: '1024x1024',
    defaultImageQuality: 'standard',
    autoOptimizePrompt: false,
    saveOriginalPrompt: true,

    // 高级设置
    developerMode: false,
    verboseLogging: false,
    experimentalFeatures: false,
    errorReporting: true
  })

  // 用户信息
  const userInfo = ref({
    username: '',
    email: '',
    nickname: '',
    avatar: ''
  })

  // 用户偏好
  const preferences = ref({
    defaultService: 'openai',
    autoFavorite: false,
    promptSuggestions: true
  })

  // 更新设置
  const updateSettings = (newSettings) => {
    settings.value = { ...settings.value, ...newSettings }
  }

  // 更新用户信息
  const updateUserInfo = (newUserInfo) => {
    userInfo.value = { ...userInfo.value, ...newUserInfo }
  }

  // 更新偏好设置
  const updatePreferences = (newPreferences) => {
    preferences.value = { ...preferences.value, ...newPreferences }
  }

  // 重置设置
  const resetSettings = () => {
    settings.value = {
      theme: 'light',
      language: 'zh-CN',
      animations: true,
      compactMode: false,
      maxConcurrentTasks: 3,
      autoSaveHistory: true,
      maxHistoryItems: 1000,
      imagePreload: true,
      defaultImageSize: '1024x1024',
      defaultImageQuality: 'standard',
      autoOptimizePrompt: false,
      saveOriginalPrompt: true,
      developerMode: false,
      verboseLogging: false,
      experimentalFeatures: false,
      errorReporting: true
    }
  }

  // 应用设置
  const applySettings = () => {
    // 应用主题
    if (settings.value.theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }

    // 应用动画设置
    if (!settings.value.animations) {
      document.documentElement.classList.add('no-animations')
    } else {
      document.documentElement.classList.remove('no-animations')
    }

    // 应用紧凑模式
    if (settings.value.compactMode) {
      document.documentElement.classList.add('compact')
    } else {
      document.documentElement.classList.remove('compact')
    }
  }

  return {
    settings,
    userInfo,
    preferences,
    updateSettings,
    updateUserInfo,
    updatePreferences,
    resetSettings,
    applySettings
  }
}, {
  persist: {
    key: 'ai-drawing-system',
    storage: localStorage
  }
})

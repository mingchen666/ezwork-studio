import { defineStore } from 'pinia'
import { Login, Register, RegisterSendCode } from '@/apis/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    // 用户信息
    userInfo: null,
    token: '',

    // 存储信息
    storageInfo: null,

    // 登录状态
    isLoggedIn: false
  }),

  getters: {
    // 是否已登录
    isAuthenticated: (state) => {
      return !!(state.token && state.userInfo)
    },

    // 用户名显示
    displayName: (state) => {
      if (!state.userInfo) return ''
      return state.userInfo.username || state.userInfo.email?.split('@')[0] || '用户'
    },

    // 存储使用率
    storageUsagePercentage: (state) => {
      if (!state.storageInfo) return 0
      return state.storageInfo.usage_percentage || 0
    },

    // 剩余存储空间（格式化）
    remainingStorageFormatted: (state) => {
      if (!state.storageInfo) return '0 MB'
      const remaining = state.storageInfo.remaining_space || 0
      return formatFileSize(remaining)
    }
  },

  actions: {
    // 登录 - 只支持邮箱密码登录
    async login(loginData) {
      try {
        const response = await Login(loginData)

        if (response.code === 200) {
          const { user, access_token } = response.data

          // 保存用户信息和token
          this.userInfo = user
          this.token = access_token
          this.isLoggedIn = true

          return { success: true, message: response.message }
        } else {
          return { success: false, message: response.message }
        }
      } catch (error) {
        console.error('Login error:', error)
        return {
          success: false,
          message: error.response?.data?.message || '登录失败，请重试'
        }
      }
    },

    // 注册
    async register(registerData) {
      try {
        const response = await Register(registerData)

        if (response.code === 200) {
          const { user, access_token } = response.data

          // 保存用户信息和token
          this.userInfo = user
          this.token = access_token
          this.isLoggedIn = true

          return { success: true, message: response.message }
        } else {
          return { success: false, message: response.message }
        }
      } catch (error) {
        console.error('Register error:', error)
        return {
          success: false,
          message: error.response?.data?.message || '注册失败，请重试'
        }
      }
    },

    // 发送注册验证码
    async sendVerificationCode(email) {
      try {
        const response = await RegisterSendCode({
          email,
          send_type: 1 // 1=注册
        })

        if (response.code === 200) {
          return { success: true, message: response.message }
        } else {
          return { success: false, message: response.message }
        }
      } catch (error) {
        console.error('Send code error:', error)
        return {
          success: false,
          message: error.response?.data?.message || '验证码发送失败，请重试'
        }
      }
    },

    // 退出登录
    logout() {
      this.userInfo = null
      this.token = ''
      this.storageInfo = null
      this.isLoggedIn = false
    },

    // 更新用户信息
    updateUserInfo(userInfo) {
      this.userInfo = { ...this.userInfo, ...userInfo }
    },

    // 更新存储信息
    updateStorageInfo(storageInfo) {
      this.storageInfo = storageInfo
    },

    // 检查token有效性
    checkTokenValidity() {
      if (!this.token) {
        this.logout()
        return false
      }

      try {
        // 简单的token过期检查（如果token是JWT格式）
        const payload = JSON.parse(atob(this.token.split('.')[1]))
        const currentTime = Date.now() / 1000

        if (payload.exp && payload.exp < currentTime) {
          this.logout()
          return false
        }

        return true
      } catch (error) {
        // 如果token格式不正确，清除登录状态
        this.logout()
        return false
      }
    }
  },

  persist: {
    key: 'ai-image-generator-user',
    storage: localStorage,
    pick: ['userInfo', 'token', 'storageInfo', 'isLoggedIn']
  }
})

// 文件大小格式化工具函数
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

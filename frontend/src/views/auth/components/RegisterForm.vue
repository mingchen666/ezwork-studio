<template>
  <div class="register-form">
    <div class="form-header">
      <h2>创建账户</h2>
      <p>加入我们，开启AI创作之旅</p>
    </div>
    
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
    >
      <el-form-item prop="email">
        <el-input
          v-model="form.email"
          type="email"
          placeholder="请输入邮箱地址"
          class="custom-input"
          size="default"
        >
          <template #prefix>
            <el-icon class="input-icon"><Message /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item prop="username">
        <el-input
          v-model="form.username"
          placeholder="请输入用户名（可选）"
          class="custom-input"
          size="default"
        >
          <template #prefix>
            <el-icon class="input-icon"><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="code">
        <div class="code-input-wrapper">
          <el-input
            v-model="form.code"
            placeholder="请输入验证码"
            class="custom-input code-input"
            size="default"
          >
            <template #prefix>
              <el-icon class="input-icon"><Key /></el-icon>
            </template>
          </el-input>
          <el-button
            class="code-btn"
            size="default"
            :loading="sendingCode"
            :disabled="!canSendCode"
            @click="sendCode"
          >
            {{ codeButtonText }}
          </el-button>
        </div>
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          show-password
          class="custom-input"
          size="default"
        >
          <template #prefix>
            <el-icon class="input-icon"><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          show-password
          class="custom-input"
          size="default"
        >
          <template #prefix>
            <el-icon class="input-icon"><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>



      <el-form-item class="submit-item">
        <el-button
          type="primary"
          class="register-btn"
          :loading="loading"
          @click="handleRegister"
        >
          <span v-if="!loading">立即注册</span>
          <span v-else>注册中...</span>
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Message, Lock, Key, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const emit = defineEmits(['success'])
const userStore = useUserStore()

const form = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
  code: ''
})

const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
const formRef = ref()

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  username: [
    { min: 2, message: '用户名长度不能少于2位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
  ]
}

const canSendCode = computed(() => {
  return form.email && countdown.value === 0 && !sendingCode.value
})

const codeButtonText = computed(() => {
  if (sendingCode.value) return '发送中'
  if (countdown.value > 0) return `${countdown.value}s`
  return '发送验证码'
})

const sendCode = async () => {
  if (!form.email) {
    ElMessage.warning('请先输入邮箱')
    return
  }

  sendingCode.value = true
  
  try {
    const result = await userStore.sendVerificationCode(form.email)
    
    if (result.success) {
      ElMessage.success(result.message)
      startCountdown()
    } else {
      ElMessage.error(result.message)
    }
  } finally {
    sendingCode.value = false
  }
}

const startCountdown = () => {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

const handleRegister = async () => {
  try {
    await formRef.value?.validate()
    
    loading.value = true
    
    const registerData = {
      email: form.email,
      password: form.password,
      code: form.code
    }
    
    if (form.username) {
      registerData.username = form.username
    }
    
    const result = await userStore.register(registerData)
    
    if (result.success) {
      emit('success', result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('Register validation failed:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-form {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .form-header {
    text-align: center;
    margin-bottom: 12px;
    
    h2 {
      font-size: 1.5rem;
      font-weight: 600;
      color: #1e293b;
      margin: 0 0 6px 0;
    }
    
    p {
      color: #64748b;
      font-size: 0.9rem;
      margin: 0;
    }
  }
  
  .custom-input {
    :deep(.el-input__wrapper) {
      border-radius: 6px;
      border: 1px solid #e2e8f0;
      box-shadow: none;
      padding: 0px 12px;
      height: 40px;
      transition: all 0.2s ease;
      
      &:hover {
        border-color: #1e293b;
      }
      
      &.is-focus {
        border-color: #1e293b;
      }
    }
    
    :deep(.el-input__inner) {
      font-size: 14px;
      color: #1e293b;
      height: 40px;
      line-height: 40px;
      
      &::placeholder {
        color: #94a3b8;
      }
    }
    
    .input-icon {
      color: #64748b;
      font-size: 16px;
    }
  }
  
  .code-input-wrapper {
    display: flex;
    gap: 8px;
    
    .code-input {
      flex: 1;
    }
    
    .code-btn {
      flex-shrink: 0;
      min-width: 90px;
      height: 40px;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      background: white;
      color: #1e293b;
      font-size: 12px;
      font-weight: 500;
      transition: all 0.2s ease;
      
      &:hover:not(:disabled) {
        border-color: #1e293b;
        background: #f8fafc;
      }
      
      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }
  }
  
  .register-btn {
    width: 100%;
    height: 42px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 8px;
   background: #4e8cf1;
    border: none;
    transition: all 0.2s ease;
    
    &:hover {
      background: #334155;
      transform: translateY(-1px);
    }
    
    &:active {
      transform: translateY(0);
    }
    
    &.is-loading {
      transform: none;
    }
  }
  
  .submit-item {
    margin-top: auto;
  }
}

:deep(.el-form-item) {
  margin-bottom: 20px;
  
  .el-form-item__error {
    font-size: 12px;
    color: #ef4444;
    margin-top: 4px;
  }
}
</style>

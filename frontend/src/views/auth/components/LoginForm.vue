<template>
  <div class="login-form">
    <div class="form-header">
      <h2>欢迎回来</h2>
      <p>登录您的账户，继续创作之旅</p>
    </div>
    
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      @submit.prevent="handleLogin"
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

      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          show-password
          class="custom-input"
          size="default"
          @keyup.enter="handleLogin"
        >
          <template #prefix>
            <el-icon class="input-icon"><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item class="submit-item">
        <el-button
          type="primary"
          class="login-btn"
          :loading="loading"
          @click="handleLogin"
        >
          <span v-if="!loading">立即登录</span>
          <span v-else>登录中...</span>
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Message, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const emit = defineEmits(['success'])
const userStore = useUserStore()

const form = reactive({
  email: '',
  password: ''
})

const loading = ref(false)
const formRef = ref()

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  try {
    await formRef.value?.validate()
    
    loading.value = true
    
    const result = await userStore.login({
      email: form.email,
      login_type: 'password',
      password: form.password
    })
    
    if (result.success) {
      emit('success', result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('Login validation failed:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-form {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .form-header {
    text-align: center;
    margin-bottom: 24px;
    
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
      padding: 0 10px;
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
  
  .login-btn {
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

<template>
  <div class="not-found-page">
    <div class="not-found-container">
      <div class="error-illustration">
        <div class="error-code">404</div>
        <div class="error-icon">
          <n-icon size="120" color="#6366f1">
            <SearchOutlined />
          </n-icon>
        </div>
      </div>
      
      <div class="error-content">
        <h1>页面未找到</h1>
        <p class="error-description">
          抱歉，您访问的页面不存在或已被移动。
        </p>
        
        <div class="error-actions">
          <n-button type="primary" size="large" @click="goHome">
            <template #icon>
              <n-icon><HomeOutlined /></n-icon>
            </template>
            返回首页
          </n-button>
          
          <n-button size="large" @click="goBack">
            <template #icon>
              <n-icon><ArrowLeftOutlined /></n-icon>
            </template>
            返回上页
          </n-button>
        </div>
        
        <div class="helpful-links">
          <h3>您可能想要访问：</h3>
          <div class="links-grid">
            <router-link to="/dashboard" class="help-link">
              <n-icon size="20"><DashboardOutlined /></n-icon>
              <span>工作台</span>
            </router-link>
            
            <router-link to="/draw" class="help-link">
              <n-icon size="20"><PictureOutlined /></n-icon>
              <span>AI绘图</span>
            </router-link>
            
            <router-link to="/gallery" class="help-link">
              <n-icon size="20"><FileImageOutlined /></n-icon>
              <span>作品画廊</span>
            </router-link>
            
            <router-link to="/settings" class="help-link">
              <n-icon size="20"><SettingOutlined /></n-icon>
              <span>系统设置</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {
  SearchOutlined,
  HomeOutlined,
  ArrowLeftOutlined,
  DashboardOutlined,
  PictureOutlined,
  FileImageOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 24px;
}

.not-found-container {
  max-width: 800px;
  width: 100%;
  text-align: center;
}

.error-illustration {
  position: relative;
  margin-bottom: 48px;
}

.error-code {
  font-size: 180px;
  font-weight: 900;
  color: #e2e8f0;
  line-height: 1;
  margin-bottom: -60px;
  position: relative;
  z-index: 1;
}

.error-icon {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: -60px;
}

.error-content h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 16px 0;
}

.error-description {
  font-size: 18px;
  color: #64748b;
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 48px;
  flex-wrap: wrap;
}

.helpful-links {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.helpful-links h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 24px 0;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.help-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  transition: all 0.2s ease;
}

.help-link:hover {
  background: #f1f5f9;
  border-color: #6366f1;
  color: #6366f1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .not-found-page {
    padding: 16px;
  }

  .error-code {
    font-size: 120px;
    margin-bottom: -40px;
  }

  .error-icon {
    margin-top: -40px;
  }

  .error-icon .n-icon {
    font-size: 80px !important;
  }

  .error-content h1 {
    font-size: 24px;
  }

  .error-description {
    font-size: 16px;
  }

  .error-actions {
    flex-direction: column;
    align-items: center;
  }

  .error-actions .n-button {
    width: 100%;
    max-width: 200px;
  }

  .helpful-links {
    padding: 24px;
  }

  .links-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .error-code {
    font-size: 100px;
  }

  .error-content h1 {
    font-size: 20px;
  }

  .helpful-links h3 {
    font-size: 18px;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .not-found-page {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  }

  .error-code {
    color: #334155;
  }

  .error-content h1 {
    color: #f1f5f9;
  }

  .error-description {
    color: #94a3b8;
  }

  .helpful-links {
    background: #1e293b;
    border-color: #334155;
  }

  .helpful-links h3 {
    color: #f1f5f9;
  }

  .help-link {
    background: #334155;
    border-color: #475569;
    color: #94a3b8;
  }

  .help-link:hover {
    background: #475569;
    border-color: #6366f1;
    color: #6366f1;
  }
}
</style>

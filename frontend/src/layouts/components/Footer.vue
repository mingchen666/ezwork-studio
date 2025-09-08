<!-- components/layout/FooterComponent.vue -->
<template>
  <footer class="layout-footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-section">
          <h4>AI绘图助手</h4>
          <p>专业的AI图像生成平台，支持多种AI服务商</p>
        </div>

        <div class="footer-section">
          <h4>功能特性</h4>
          <ul>
            <li>多AI服务商支持</li>
            <li>智能参数配置</li>
            <li>作品管理</li>
            <li>历史记录</li>
          </ul>
        </div>

        <div class="footer-section">
          <h4>技术支持</h4>
          <ul>
            <li>OpenAI DALL-E</li>
            <li>Midjourney</li>
            <li>Google Gemini</li>
            <li>ChatGPT Vision</li>
          </ul>
        </div>

        <div class="footer-section">
          <h4>联系我们</h4>
          <p>Email: support@ai-drawing.com</p>
          <p>版本: v1.0.0</p>
        </div>
      </div>

      <div class="footer-bottom">
        <p>&copy; 2024 AI绘图助手. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
// 无需额外逻辑
</script>

<style scoped>
.layout-footer {
  background: #1e293b;
  color: #e2e8f0;
  margin-top: auto;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 48px 24px 24px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
  margin-bottom: 32px;
}

.footer-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
}

.footer-section p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #94a3b8;
  line-height: 1.5;
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section li {
  padding: 4px 0;
  font-size: 14px;
  color: #94a3b8;
}

.footer-bottom {
  padding-top: 24px;
  border-top: 1px solid #334155;
  text-align: center;
}

.footer-bottom p {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

@media (max-width: 1024px) {
  .footer-container {
    padding: 32px 16px 16px;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style>

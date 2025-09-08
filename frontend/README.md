# AI绘图助手

一个基于Vue 3构建的现代化AI绘图应用，支持多种AI绘图服务，具备响应式设计，完美适配移动端和PC端。

## 🌟 特性

- **多AI服务支持**: 集成OpenAI DALL-E、Midjourney、Google Gemini、ChatGPT
- **响应式设计**: 完美适配移动端和PC端
- **多任务处理**: 支持同时处理多个绘图任务
- **本地存储**: API密钥和历史记录安全存储在本地
- **作品管理**: 历史记录、收藏功能、搜索筛选
- **暗色主题**: 自动适配系统主题偏好
- **离线支持**: PWA应用，支持离线使用

## 🚀 快速开始

### 环境要求

- Node.js >= 20.19.0 或 >= 22.12.0
- pnpm >= 8.0.0

### 安装依赖

```bash
pnpm install
```

### 启动开发服务器

```bash
pnpm dev
```

应用将在 `http://localhost:5173` 启动

### 构建生产版本

```bash
pnpm build
```

### 预览生产构建

```bash
pnpm preview
```

## 📖 使用指南

### 1. 配置API密钥

首次使用需要配置AI服务的API密钥：

1. 点击导航栏的"API设置"或首页的"配置API"
2. 根据需要配置以下服务：
   - **OpenAI DALL-E**: 访问 [OpenAI API Keys](https://platform.openai.com/api-keys) 获取密钥
   - **Midjourney**: 联系官方获取API访问权限
   - **Google Gemini**: 访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 创建密钥
   - **ChatGPT**: 使用OpenAI相同的API密钥
3. 开启需要使用的服务
4. 点击"测试连接"验证配置
5. 保存配置

### 2. 开始创作

1. 点击"创作绘图"进入绘图界面
2. 选择AI服务
3. 输入详细的图像描述
4. 根据需要调整高级参数
5. 点击"生成图像"开始创作

### 3. 管理作品

- **查看历史**: 在"作品画廊"查看所有创作记录
- **收藏作品**: 点击心形图标收藏喜欢的作品
- **下载图片**: 点击下载按钮保存图片到本地
- **搜索筛选**: 使用搜索框和筛选器快速找到作品

### 4. 任务管理

- 点击右上角的任务图标查看任务面板
- 查看任务进度和状态
- 可以取消、重试或删除任务

## 🛠️ 技术栈

- **前端框架**: Vue 3.5+ (Composition API)
- **状态管理**: Pinia 3.0+
- **路由**: Vue Router 4.0+
- **UI组件**: Naive UI 2.42+
- **图标**: Ant Design Icons Vue
- **构建工具**: Vite 7.0+
- **工具库**: VueUse
- **HTTP客户端**: Axios
- **样式**: CSS3 + 响应式设计

## 📁 项目结构

```
src/
├── components/          # 可复用组件
│   ├── AppLayout.vue   # 主布局组件
│   ├── ApiConfig.vue   # API配置组件
│   ├── DrawingInterface.vue # 绘图界面
│   ├── TaskPanel.vue   # 任务面板
│   └── SettingsPanel.vue # 设置面板
├── views/              # 页面组件
│   ├── Dashboard.vue   # 工作台
│   ├── Draw.vue        # 绘图页面
│   ├── Gallery.vue     # 作品画廊
│   └── Settings.vue    # 设置页面
├── stores/             # Pinia状态管理
│   ├── config.js       # API配置管理
│   ├── task.js         # 任务管理
│   └── history.js      # 历史记录管理
├── services/           # API服务层
│   ├── api-base.js     # 基础API工具
│   ├── openai.js       # OpenAI服务
│   ├── midjourney.js   # Midjourney服务
│   ├── gemini.js       # Gemini服务
│   ├── chatgpt.js      # ChatGPT服务
│   └── index.js        # 服务管理器
├── router/             # 路由配置
│   └── index.js
├── App.vue             # 根组件
└── main.js             # 应用入口
```

## 🔐 隐私与安全

- **本地存储**: 所有API密钥和用户数据仅存储在浏览器本地，不会上传到任何服务器
- **HTTPS支持**: 生产环境建议使用HTTPS确保API通信安全
- **密钥管理**: 建议定期更换API密钥

## 📱 移动端支持

应用采用响应式设计，完美支持移动设备：

- 自适应布局
- 触摸友好的交互
- 移动端优化的导航
- 支持手势操作

## 🌙 主题支持

- 自动检测系统主题偏好
- 支持浅色/深色主题切换
- 高对比度模式支持

## 🛡️ 错误处理

- 全局错误捕获
- 用户友好的错误提示
- API请求失败重试机制
- 网络状态监控

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License

---

🎨 **开始您的AI绘图创作之旅吧！**

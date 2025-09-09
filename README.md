# Ezwork Studio

一站式AI绘图客户端，基于 Gemini AI模型的智能图像生成工具。

## 项目介绍

EZWork Studio 是一个现代化的AI绘图客户端，支持文字生成图片、图片编辑、历史记录管理等功能。采用前后端分离架构，提供流畅的用户体验。

## 主要功能

- 🎨 AI图像生成（基于Google Gemini模型）
- 🖼️ 图片编辑
- 📚 历史记录管理

## 技术栈

- **前端**: Vue 3
- **后端**: Flask 
- **部署**: Docker + Docker Compose

## 快速开始


### 1.Docker Compose部署

#### 构建并启动服务

```bash
git clone https://github.com/mingchen666/ezwork-studio.git
cd ezwork-studio

# 启动服务
docker compose up --build -d

```

### 2.Docker手动构建镜像部署

#### (1).创建网络
```bash
docker network create ezwork-net

```
#### (2).构建镜像
```bash
# 前端
docker build -t ezworkstudio-frontend ./frontend

# 后端
docker build -t ezworkstudio-backend ./backend

```


#### (3).启动容器

```bash
# 前端
docker run -d --name ezworkstudio-frontend \
  --network ezwork-net \
  -p 1580:8080 \
  ezworkstudio-frontend

# 后端
docker run -d --name ezworkstudio-backend \
  --network ezwork-net \
  --env-file ./backend/.env \
  -p 5000:5000 \
  ezworkstudio-backend

```


### 3.本地开发
>环境要求

- Node.js 20+
- Python 3.10+
- Docker

#### 前端打包

```bash
cd frontend
pnpm install
pnpm dev
```

#### 后端启动

```bash
cd backend
pip install -r requirements.txt

python app.py
```

#### 后端环境配置(.env文件)

```bash
# 数据库
DATABASE_URL=xxxx

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# 邮件服务
MAIL_SERVER=smtp.qq.com
MAIL_USERNAME=your-email@qq.com
MAIL_PASSWORD=your-email-password

.......
```

部署成功请访问：http://localhost:1580

## 发布记录

| 版本   | 日期       | 说明                                                                 |
|--------|------------|----------------------------------------------------------------------|
| v0.0.0 | 2025-09-09 | 初始版本发布：AI 绘图、图片编辑、历史记录、Docker 部署等                 |
| v0.0.1 | 待定 | 待定                            |



## 许可证

Apache-2.0
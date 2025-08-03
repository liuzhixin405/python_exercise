# FeedMusic Clone - 音乐新闻网站

这是一个基于 feedmusic.com 设计的音乐新闻网站，包含完整的前后端功能。

## 项目结构

```
├── frontend/          # React前端应用
├── backend/           # Python Flask后端API
├── deployment/        # 部署相关文件
└── README.md         # 项目说明
```

## 功能特性

### 前端功能
- 动态背景和文字滚动效果
- 响应式设计（PC端和移动端）
- 新闻展示
- 屏幕切换动画效果
- 管理后台链接

### 后端功能
- 用户认证系统
- 新闻CRUD操作
- 图片上传支持
- 权限控制

### 管理后台
- 独立的管理后台界面
- 用户管理
- 新闻管理
- 统计概览

## 技术栈

- **前端**: React, TypeScript, Tailwind CSS
- **后端**: Python Flask, SQLAlchemy, JWT
- **数据库**: SQLite (开发) / PostgreSQL (生产)

## 🚀 快速开始

### 一键启动（推荐）
- **Windows**: 双击运行 `start.bat`
- **Linux/Mac**: 运行 `./start.sh`

### 手动启动

#### 后端启动
```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### 管理后台启动
```bash
cd backend
python admin.py
```

#### 前端启动
```bash
cd frontend
npm install
npm start
```

### 访问应用
- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:5000
- **管理后台**: http://localhost:5001/admin

> 📖 详细部署说明请参考 [QUICKSTART.md](QUICKSTART.md) 和 [deployment/README.md](deployment/README.md)

## 部署说明

详细部署说明请参考 `deployment/` 目录下的文档。 
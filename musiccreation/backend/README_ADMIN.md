# 后台管理系统架构说明

## 项目结构

```
backend/
├── admin/                          # 后台管理应用包
│   ├── __init__.py                 # 应用工厂函数
│   ├── models/                     # 数据模型
│   │   ├── __init__.py
│   │   └── data_store.py          # 内存数据存储
│   ├── routes/                     # 路由模块
│   │   ├── __init__.py
│   │   ├── auth.py                # 认证路由
│   │   ├── dashboard.py           # 仪表板路由
│   │   ├── users.py               # 用户管理路由
│   │   ├── news.py                # 新闻管理路由
│   │   └── api.py                 # API路由
│   ├── utils/                      # 工具函数
│   │   ├── __init__.py
│   │   ├── auth.py                # 认证工具
│   │   └── file_upload.py         # 文件上传工具
│   └── templates/                  # 模板文件
│       ├── simple_login.html
│       ├── register.html
│       ├── simple_dashboard.html
│       ├── simple_users.html
│       ├── simple_news.html
│       ├── create_news.html
│       └── edit_news.html
├── config.py                       # 配置文件
├── run_admin.py                    # 启动文件
└── requirements.txt                # 依赖文件
```

## 架构特点

### 1. **模块化设计**
- **模型层 (Models)**: 数据存储和业务逻辑
- **路由层 (Routes)**: 请求处理和响应
- **工具层 (Utils)**: 通用功能函数
- **模板层 (Templates)**: 前端页面

### 2. **蓝图架构**
- `auth_bp`: 认证相关路由
- `dashboard_bp`: 仪表板路由
- `users_bp`: 用户管理路由
- `news_bp`: 新闻管理路由
- `api_bp`: RESTful API路由

### 3. **配置管理**
- 支持多环境配置 (开发/生产/测试)
- 统一的配置管理
- 环境变量支持

### 4. **数据存储**
- 内存数据存储 (可扩展为数据库)
- 类型提示支持
- 统一的数据访问接口

## 启动方式

```bash
# 方式1: 直接启动
python run_admin.py

# 方式2: 使用启动脚本
start.bat
```

## 访问地址

- **管理后台**: http://localhost:5001
- **API测试**: http://localhost:5001/test
- **默认账号**: admin / admin123

## 功能模块

### 认证模块
- 用户注册
- 用户登录
- 用户登出
- 权限控制

### 仪表板
- 系统统计
- 快速操作
- 数据概览

### 用户管理
- 用户列表
- 用户统计
- 角色管理

### 新闻管理
- 新闻列表 (分页)
- 创建新闻
- 编辑新闻
- 删除新闻
- 图片上传

### API接口
- RESTful API设计
- JSON响应格式
- 错误处理
- 权限验证

## 扩展说明

### 添加新功能
1. 在 `models/` 中添加数据模型
2. 在 `routes/` 中添加路由处理
3. 在 `utils/` 中添加工具函数
4. 在 `templates/` 中添加页面模板

### 数据库集成
1. 修改 `models/data_store.py`
2. 添加数据库连接配置
3. 实现数据持久化

### 新路由添加
1. 创建新的路由文件
2. 在 `__init__.py` 中注册蓝图
3. 添加相应的模板文件 
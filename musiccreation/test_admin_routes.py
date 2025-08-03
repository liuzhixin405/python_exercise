#!/usr/bin/env python3
"""
测试后台管理路由
"""
import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from flask import Flask
from admin.routes.auth import auth_bp
from admin.routes.dashboard import dashboard_bp
from admin.routes.users import users_bp
from admin.routes.news import news_bp
from admin.routes.api import api_bp
from admin.models.mysql_data_store import mysql_data_store
from admin.utils.auth import bcrypt, hash_password

def create_simple_admin_app():
    """创建简化的后台管理应用"""
    # 获取当前文件所在目录的backend目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    app = Flask(__name__, 
                template_folder=os.path.join(backend_dir, 'templates'),
                static_folder=os.path.join(backend_dir, 'static'))
    
    # 基础配置
    app.config['SECRET_KEY'] = 'admin-secret-key'
    app.config['DEBUG'] = True
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # MySQL数据库配置
    app.config['MYSQL_HOST'] = '127.0.0.1'
    app.config['MYSQL_PORT'] = 3307
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '123456'
    app.config['MYSQL_DATABASE'] = 'musiccreation'
    
    # 初始化扩展
    bcrypt.init_app(app)
    
    # 初始化数据库
    from database import db
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(api_bp)
    
    return app

def init_data_store():
    """初始化数据存储"""
    # 检查是否需要创建管理员用户
    admin_user = mysql_data_store.get_user_by_username('admin')
    if not admin_user:
        # 创建管理员用户
        password_hash = hash_password('admin123')
        mysql_data_store.create_user('admin', 'admin@feedmusic.com', password_hash, is_admin=True)
        print("✅ 创建管理员用户: admin / admin123")

if __name__ == "__main__":
    app = create_simple_admin_app()
    
    # 在应用上下文中初始化数据存储
    with app.app_context():
        init_data_store()
    
    print("🚀 启动后台管理应用...")
    print("📊 后台管理地址: http://localhost:5000/admin/login")
    print("🔑 默认管理员账号: admin / admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
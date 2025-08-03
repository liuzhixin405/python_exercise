"""
后台管理应用包
"""
import os
from flask import Flask
from flask_cors import CORS
from config import config
from admin.models.admin_data_store import admin_data_store
from admin.utils.auth import bcrypt, hash_password

def create_app(config_name='default'):
    """应用工厂函数"""
    # 获取当前文件所在目录的上级目录（backend目录）
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(__name__, 
                template_folder=os.path.join(backend_dir, 'templates'),
                static_folder=os.path.join(backend_dir, 'static'))
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # MySQL数据库配置
    app.config['MYSQL_HOST'] = '127.0.0.1'
    app.config['MYSQL_PORT'] = 3307
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '123456'
    app.config['MYSQL_DATABASE'] = 'musiccreation'
    
    # 初始化扩展
    CORS(app)
    bcrypt.init_app(app)
    
    # 初始化数据库
    from database import db
    db.init_app(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    return app

def init_data_store():
    """初始化数据存储"""
    # 检查是否需要创建管理员用户
    admin_user = admin_data_store.get_admin_user_by_username('admin')
    if not admin_user:
        # 创建管理员用户
        password_hash = hash_password('admin123')
        admin_data_store.create_admin_user('admin', 'admin@feedmusic.com', password_hash, real_name='系统管理员', role='admin')

def register_blueprints(app):
    """注册蓝图"""
    from admin.routes.auth import auth_bp
    from admin.routes.dashboard import dashboard_bp
    from admin.routes.users import users_bp
    from admin.routes.news import news_bp
    from admin.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(api_bp) 
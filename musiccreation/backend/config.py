import os
from datetime import timedelta

class Config:
    """基础配置类"""
    # 基础配置
    SECRET_KEY = 'admin-secret-key'
    DEBUG = True
    
    # 文件上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # 分页配置
    NEWS_PER_PAGE = 10
    USERS_PER_PAGE = 20
    
    # JWT配置
    JWT_SECRET_KEY = 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # 数据库配置（如果将来需要）
    DATABASE_URL = 'sqlite:///admin.db'
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建上传目录
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    WTF_CSRF_ENABLED = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 
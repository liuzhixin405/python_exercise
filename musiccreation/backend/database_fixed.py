"""
MySQL数据库连接和配置（修复版本）
"""

import mysql.connector
from mysql.connector import Error
from flask import g
import os

class Database:
    """数据库连接管理类"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化数据库配置"""
        self.app = app
        
        # 数据库配置
        app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', '127.0.0.1')
        app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3307))
        app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
        app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '123456')
        app.config['MYSQL_DATABASE'] = os.getenv('MYSQL_DATABASE', 'musiccreation')
        
        # 注册关闭数据库连接的函数
        app.teardown_appcontext(self.close_db)
    
    def get_db(self):
        """获取数据库连接"""
        if 'db' not in g:
            try:
                g.db = mysql.connector.connect(
                    host=self.app.config['MYSQL_HOST'],
                    port=self.app.config['MYSQL_PORT'],
                    user=self.app.config['MYSQL_USER'],
                    password=self.app.config['MYSQL_PASSWORD'],
                    database=self.app.config['MYSQL_DATABASE'],
                    charset='utf8mb4',
                    autocommit=True
                )
                print("✅ 数据库连接成功")
            except Error as e:
                print(f"❌ 数据库连接失败: {e}")
                raise e
        return g.db
    
    def close_db(self, e=None):
        """关闭数据库连接"""
        db = g.pop('db', None)
        if db is not None:
            db.close()
            print("✅ 数据库连接已关闭")
    
    def execute_query(self, query, params=None):
        """执行查询"""
        db = self.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def execute_update(self, query, params=None):
        """执行更新操作"""
        db = self.get_db()
        cursor = db.cursor()
        try:
            cursor.execute(query, params or ())
            db.commit()
            return cursor.rowcount
        finally:
            cursor.close()
    
    def execute_insert(self, query, params=None):
        """执行插入操作"""
        db = self.get_db()
        cursor = db.cursor()
        try:
            cursor.execute(query, params or ())
            db.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

# 创建数据库实例
db = Database()

def get_db():
    """获取数据库连接"""
    return db.get_db()

def init_database():
    """初始化数据库表"""
    try:
        # 创建用户表（修复索引长度问题）
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        # 创建新闻表
        create_news_table = """
        CREATE TABLE IF NOT EXISTS news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            image_url VARCHAR(500),
            author VARCHAR(50) NOT NULL,
            author_id INT,
            status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        # 执行创建表操作
        db.execute_update(create_users_table)
        db.execute_update(create_news_table)
        
        print("✅ 数据库表初始化完成")
        
        # 检查是否需要插入初始数据
        check_admin = "SELECT COUNT(*) as count FROM users WHERE username = 'admin'"
        result = db.execute_query(check_admin)
        
        if result[0]['count'] == 0:
            # 插入管理员用户
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
            
            insert_admin = """
            INSERT INTO users (username, email, password_hash, is_admin) 
            VALUES ('admin', 'admin@feedmusic.com', %s, TRUE)
            """
            db.execute_insert(insert_admin, (password_hash,))
            
            # 插入示例新闻
            sample_news = [
                ('Taylor Swift 发布新专辑《Midnights》', 
                 '流行天后 Taylor Swift 发布了她的第十张录音室专辑《Midnights》，这张专辑融合了流行、电子和另类音乐元素，展现了她在音乐创作上的新突破。专辑中的每首歌都代表了午夜时分的不同情绪和思考。',
                 'https://picsum.photos/400/300?random=1', 'admin', 1),
                ('BTS 成员开始个人活动',
                 '韩国男团 BTS 的成员们开始各自的个人音乐活动，每位成员都展现了独特的音乐风格和个人魅力。从 RM 的深度思考到 Jungkook 的青春活力，粉丝们对此表示热烈支持。',
                 'https://picsum.photos/400/300?random=2', 'admin', 1),
                ('Billie Eilish 获得格莱美大奖',
                 'Billie Eilish 在今年的格莱美颁奖典礼上获得了多个重要奖项，包括年度专辑和年度歌曲。她的音乐才华和独特风格得到了业界的广泛认可。',
                 'https://picsum.photos/400/300?random=3', 'admin', 1),
                ('Ed Sheeran 世界巡回演唱会启动',
                 '英国创作歌手 Ed Sheeran 宣布启动他的世界巡回演唱会，将在全球多个城市进行演出，为歌迷带来精彩的音乐盛宴。巡演将包括新专辑中的热门歌曲。',
                 'https://picsum.photos/400/300?random=4', 'admin', 1),
                ('Drake 新单曲打破流媒体记录',
                 '说唱歌手 Drake 的最新单曲在各大流媒体平台上创造了新的播放记录，再次证明了他作为音乐巨星的强大影响力。新歌融合了多种音乐风格。',
                 'https://picsum.photos/400/300?random=5', 'admin', 1)
            ]
            
            insert_news = """
            INSERT INTO news (title, description, image_url, author, author_id) 
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for news in sample_news:
                db.execute_insert(insert_news, news)
            
            print("✅ 初始数据插入完成")
        
    except Error as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise e 
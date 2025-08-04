#!/usr/bin/env python3
"""
重新创建数据库
"""
import pymysql
from pymysql.cursors import DictCursor

def recreate_database():
    """重新创建数据库"""
    try:
        # 连接参数
        host = '127.0.0.1'
        port = 3307
        user = 'root'
        password = '123456'
        database = 'musiccreation'
        
        print("正在重新创建数据库...")
        
        # 连接到MySQL服务器
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        
        with connection.cursor() as cursor:
            # 删除数据库（如果存在）
            cursor.execute(f"DROP DATABASE IF EXISTS {database}")
            print(f"✅ 删除旧数据库 {database}")
            
            # 创建新数据库
            cursor.execute(f"CREATE DATABASE {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ 创建新数据库 {database}")
        
        connection.close()
        
        # 连接到新数据库
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        
        with connection.cursor() as cursor:
            # 创建用户表
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    real_name VARCHAR(100),
                    role ENUM('user', 'admin', 'viewer') DEFAULT 'user',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    INDEX idx_username (username),
                    INDEX idx_email (email),
                    INDEX idx_role (role)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ 用户表创建成功")
            
            # 创建新闻表
            cursor.execute("""
                CREATE TABLE news (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    content LONGTEXT,
                    image_url VARCHAR(500),
                    author_id INT,
                    author_name VARCHAR(100),
                    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
                    view_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    published_at TIMESTAMP NULL,
                    INDEX idx_author_id (author_id),
                    INDEX idx_status (status),
                    INDEX idx_created_at (created_at),
                    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ 新闻表创建成功")
            
            # 创建默认管理员用户
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            admin_password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, real_name, role) 
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', 'admin@feedmusic.com', admin_password_hash, '系统管理员', 'admin'))
            print("✅ 默认管理员用户创建成功")
            
            # 插入示例新闻数据
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin_id = cursor.fetchone()['id']
            
            sample_news = [
                ('Taylor Swift 发布新专辑《Midnights》', '流行天后 Taylor Swift 发布了她的第十张录音室专辑《Midnights》，这张专辑融合了流行、电子和另类音乐元素，展现了她在音乐创作上的新突破。专辑中的每首歌都代表了午夜时分的不同情绪和思考。', 'https://picsum.photos/400/300?random=1', admin_id, 'admin'),
                ('BTS 成员开始个人活动', '韩国男团 BTS 的成员们开始各自的个人音乐活动，每位成员都展现了独特的音乐风格和个人魅力。从 RM 的深度思考到 Jungkook 的青春活力，粉丝们对此表示热烈支持。', 'https://picsum.photos/400/300?random=2', admin_id, 'admin'),
                ('Billie Eilish 获得格莱美大奖', 'Billie Eilish 在今年的格莱美颁奖典礼上获得了多个重要奖项，包括年度专辑和年度歌曲。她的音乐才华和独特风格得到了业界的广泛认可。', 'https://picsum.photos/400/300?random=3', admin_id, 'admin')
            ]
            
            for title, description, image_url, author_id, author_name in sample_news:
                cursor.execute("""
                    INSERT INTO news (title, description, content, image_url, author_id, author_name, status, published_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, description, description, image_url, author_id, author_name, 'published', '2024-01-15 10:30:00'))
            
            print("✅ 示例新闻数据创建成功")
            
            connection.commit()
        
        connection.close()
        print("✅ 数据库重新创建完成！")
        return True
        
    except Exception as e:
        print(f"❌ 重新创建数据库失败: {e}")
        return False

if __name__ == "__main__":
    recreate_database() 
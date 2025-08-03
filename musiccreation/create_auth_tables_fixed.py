#!/usr/bin/env python3
"""
创建用户认证相关数据库表的脚本（修复版本）
"""

import mysql.connector
from mysql.connector import Error
from flask_bcrypt import Bcrypt

def create_auth_tables():
    """创建用户认证相关的表"""
    config = {
        'host': '127.0.0.1',
        'port': 3307,
        'user': 'root',
        'password': '123456',
        'database': 'musiccreation'
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("✅ 数据库连接成功")
        
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
        
        cursor.execute(create_users_table)
        print("✅ 用户表创建成功")
        
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
        
        cursor.execute(create_news_table)
        print("✅ 新闻表创建成功")
        
        # 创建索引（修复长度问题）
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_news_author_id ON news(author_id)",
            "CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Error as e:
                print(f"索引可能已存在: {e}")
        
        print("✅ 索引创建完成")
        
        # 检查是否需要插入初始数据
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("正在插入初始管理员用户...")
            
            bcrypt = Bcrypt()
            password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
            
            insert_admin = """
            INSERT INTO users (username, email, password_hash, is_admin) 
            VALUES ('admin', 'admin@feedmusic.com', %s, TRUE)
            """
            cursor.execute(insert_admin, (password_hash,))
            admin_id = cursor.lastrowid
            
            # 插入示例新闻
            sample_news = [
                ('Taylor Swift 发布新专辑《Midnights》', 
                 '流行天后 Taylor Swift 发布了她的第十张录音室专辑《Midnights》。',
                 'https://picsum.photos/400/300?random=1', 'admin', admin_id, 'published'),
                ('BTS 成员开始个人活动',
                 '韩国男团 BTS 的成员们开始各自的个人音乐活动。',
                 'https://picsum.photos/400/300?random=2', 'admin', admin_id, 'published'),
                ('Billie Eilish 获得格莱美大奖',
                 'Billie Eilish 在今年的格莱美颁奖典礼上获得了多个重要奖项。',
                 'https://picsum.photos/400/300?random=3', 'admin', admin_id, 'published')
            ]
            
            insert_news = """
            INSERT INTO news (title, description, image_url, author, author_id, status) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            for news in sample_news:
                cursor.execute(insert_news, news)
            
            print("✅ 初始数据插入完成")
        
        connection.commit()
        print("✅ 数据库更改已提交")
        
        # 显示各表的记录数
        tables = ['users', 'news', 'music']
        print(f"\n📊 各表记录数:")
        for table_name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  {table_name}表: {count}条")
            except Error as e:
                print(f"  {table_name}表: 查询失败")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ 数据库操作失败: {e}")

if __name__ == "__main__":
    print("=== 开始创建用户认证相关表 ===")
    create_auth_tables()
    print("=== 用户认证表创建完成 ===") 
#!/usr/bin/env python3
"""
测试数据库连接的脚本
"""

import mysql.connector
from mysql.connector import Error

def test_database_connection():
    """测试数据库连接"""
    config = {
        'host': '127.0.0.1',
        'port': 3307,
        'user': 'root',
        'password': '123456',
        'database': 'musiccreation'
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        print("✅ 数据库连接成功")
        
        # 测试用户表
        print("\n=== 用户表测试 ===")
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"用户数量: {len(users)}")
        for user in users:
            print(f"  - {user['username']} ({user['email']}) - 管理员: {user['is_admin']}")
        
        # 测试新闻表
        print("\n=== 新闻表测试 ===")
        cursor.execute("SELECT * FROM news")
        news = cursor.fetchall()
        print(f"新闻数量: {len(news)}")
        for item in news:
            print(f"  - {item['title']} (作者: {item['author']})")
        
        # 测试音乐表
        print("\n=== 音乐表测试 ===")
        cursor.execute("SELECT * FROM music")
        music = cursor.fetchall()
        print(f"音乐数量: {len(music)}")
        for item in music:
            print(f"  - {item['title']} (艺术家: {item['artist']}, 流派: {item['genre']})")
        
        # 测试用户登录
        print("\n=== 用户登录测试 ===")
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        if admin:
            print(f"找到管理员用户: {admin['username']}")
            print(f"密码哈希: {admin['password_hash'][:20]}...")
        else:
            print("未找到管理员用户")
        
        cursor.close()
        connection.close()
        print("\n✅ 数据库测试完成")
        
    except Error as e:
        print(f"❌ 数据库连接失败: {e}")

if __name__ == "__main__":
    test_database_connection() 
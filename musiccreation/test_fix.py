#!/usr/bin/env python3
"""
测试修复效果的脚本
"""

import mysql.connector
from mysql.connector import Error

def test_fix():
    """测试修复效果"""
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
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📋 数据库中的表:")
        for table in tables:
            print(f"  - {table[list(table.keys())[0]]}")
        
        # 检查各表的记录数
        table_names = ['users', 'news', 'music']
        print(f"\n📊 各表记录数:")
        for table_name in table_names:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                print(f"  {table_name}表: {count}条")
            except Error as e:
                print(f"  {table_name}表: 查询失败 - {e}")
        
        # 测试用户登录
        print(f"\n🔐 用户登录测试:")
        cursor.execute("SELECT username, email, is_admin FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        if admin:
            print(f"  找到管理员用户: {admin['username']} ({admin['email']})")
            print(f"  管理员权限: {admin['is_admin']}")
        else:
            print("  未找到管理员用户")
        
        cursor.close()
        connection.close()
        print("\n✅ 测试完成")
        
    except Error as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_fix() 
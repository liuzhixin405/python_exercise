#!/usr/bin/env python3
"""
MySQL连接测试脚本
用于测试MCP服务器配置的MySQL连接是否正常
"""

import mysql.connector
from mysql.connector import Error
import sys

def test_mysql_connection():
    """测试MySQL连接"""
    # MCP配置文件中的连接参数
    config = {
        'host': '127.0.0.1',
        'port': 3307,
        'user': 'root',
        'password': '123456',
        'database': 'musiccreation'
    }
    
    print("正在测试MySQL连接...")
    print(f"连接参数: {config}")
    
    try:
        # 尝试连接MySQL
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ MySQL连接成功!")
            print(f"MySQL服务器版本: {db_info}")
            
            # 获取数据库信息
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            database = cursor.fetchone()
            print(f"当前数据库: {database[0]}")
            
            # 测试查询
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"数据库中的表: {[table[0] for table in tables]}")
            
            cursor.close()
            connection.close()
            print("✅ 连接测试完成，MySQL服务正常运行")
            return True
            
    except Error as e:
        print(f"❌ MySQL连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接测试出错: {e}")
        return False

def test_mysql_server_status():
    """测试MySQL服务器状态"""
    print("\n=== MySQL服务器状态检查 ===")
    
    # 检查端口是否开放
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 3307))
    sock.close()
    
    if result == 0:
        print("✅ 端口3307已开放")
    else:
        print("❌ 端口3307未开放，MySQL服务可能未启动")
        return False
    
    return True

if __name__ == "__main__":
    print("=== MySQL MCP服务器连接测试 ===")
    
    # 检查MySQL服务器状态
    if not test_mysql_server_status():
        print("\n请确保MySQL服务已启动并监听端口3307")
        sys.exit(1)
    
    # 测试连接
    if test_mysql_connection():
        print("\n🎉 MySQL MCP服务器连接正常!")
    else:
        print("\n💥 MySQL MCP服务器连接失败!")
        print("请检查以下项目:")
        print("1. MySQL服务是否已启动")
        print("2. 端口3307是否正确")
        print("3. 用户名和密码是否正确")
        print("4. 数据库'musiccreation'是否存在")
        sys.exit(1) 
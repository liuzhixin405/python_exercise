#!/usr/bin/env python3
"""
创建music表的Python脚本
"""

import mysql.connector
from mysql.connector import Error
import os

def execute_sql_file(cursor, file_path):
    """执行SQL文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read()
        
        # 分割SQL命令
        commands = sql_commands.split(';')
        
        for command in commands:
            command = command.strip()
            if command and not command.startswith('--'):
                cursor.execute(command)
                print(f"✅ 执行SQL命令: {command[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ 执行SQL文件失败: {e}")
        return False

def create_music_table():
    """创建music表"""
    # 数据库连接配置
    config = {
        'host': '127.0.0.1',
        'port': 3307,
        'user': 'root',
        'password': '123456',
        'database': 'musiccreation'
    }
    
    try:
        # 连接数据库
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("=== 开始创建music表 ===")
        
        # 执行SQL文件
        sql_file = 'create_music_table.sql'
        if os.path.exists(sql_file):
            if execute_sql_file(cursor, sql_file):
                # 提交更改
                connection.commit()
                print("✅ 数据库更改已提交")
                
                # 验证表是否创建成功
                cursor.execute("SHOW TABLES LIKE 'music'")
                if cursor.fetchone():
                    print("✅ music表创建成功！")
                    
                    # 显示表结构
                    cursor.execute("DESCRIBE music")
                    columns = cursor.fetchall()
                    print("\n📋 表结构:")
                    for column in columns:
                        print(f"  {column[0]} - {column[1]} - {column[2]}")
                    
                    # 显示示例数据
                    cursor.execute("SELECT id, title, artist, genre, duration FROM music LIMIT 5")
                    records = cursor.fetchall()
                    print(f"\n📊 示例数据 (共{len(records)}条):")
                    for record in records:
                        print(f"  ID: {record[0]}, 标题: {record[1]}, 艺术家: {record[2]}, 流派: {record[3]}, 时长: {record[4]}秒")
                    
                else:
                    print("❌ music表创建失败")
            else:
                print("❌ SQL文件执行失败")
        else:
            print(f"❌ SQL文件 {sql_file} 不存在")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ 数据库连接或操作失败: {e}")

if __name__ == "__main__":
    create_music_table() 
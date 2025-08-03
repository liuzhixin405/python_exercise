#!/usr/bin/env python3
"""
查询music表的脚本
"""

import mysql.connector
from mysql.connector import Error

def query_music_table():
    """查询music表"""
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
        
        print("=== Music表查询结果 ===")
        
        # 查询所有音乐
        cursor.execute("""
            SELECT id, title, artist, genre, duration, bpm, key_signature, time_signature, status, created_at 
            FROM music 
            ORDER BY id
        """)
        
        records = cursor.fetchall()
        print(f"\n📊 音乐列表 (共{len(records)}条记录):")
        print("-" * 100)
        print(f"{'ID':<3} {'标题':<15} {'艺术家':<12} {'流派':<8} {'时长':<6} {'BPM':<4} {'调号':<8} {'拍号':<6} {'状态':<10} {'创建时间'}")
        print("-" * 100)
        
        for record in records:
            id, title, artist, genre, duration, bpm, key_signature, time_signature, status, created_at = record
            print(f"{id:<3} {title:<15} {artist:<12} {genre:<8} {duration:<6} {bpm:<4} {key_signature:<8} {time_signature:<6} {status:<10} {created_at}")
        
        # 按流派统计
        cursor.execute("SELECT genre, COUNT(*) as count FROM music GROUP BY genre ORDER BY count DESC")
        genre_stats = cursor.fetchall()
        
        print(f"\n📈 流派统计:")
        for genre, count in genre_stats:
            print(f"  {genre}: {count}首")
        
        # 按状态统计
        cursor.execute("SELECT status, COUNT(*) as count FROM music GROUP BY status ORDER BY count DESC")
        status_stats = cursor.fetchall()
        
        print(f"\n📊 状态统计:")
        for status, count in status_stats:
            print(f"  {status}: {count}首")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ 查询失败: {e}")

if __name__ == "__main__":
    query_music_table() 
#!/usr/bin/env python3
"""
简化版music表创建脚本
"""

import mysql.connector
from mysql.connector import Error

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
        print("正在连接数据库...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("✅ 数据库连接成功")
        
        # 删除表（如果存在）
        print("正在删除旧表（如果存在）...")
        cursor.execute("DROP TABLE IF EXISTS music")
        print("✅ 旧表删除完成")
        
        # 创建music表
        print("正在创建music表...")
        create_table_sql = """
        CREATE TABLE music (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL COMMENT '音乐标题',
            artist VARCHAR(255) NOT NULL COMMENT '艺术家/创作者',
            genre VARCHAR(100) COMMENT '音乐流派',
            duration INT COMMENT '时长（秒）',
            bpm INT COMMENT '每分钟节拍数',
            key_signature VARCHAR(20) COMMENT '调号',
            time_signature VARCHAR(20) COMMENT '拍号',
            description TEXT COMMENT '音乐描述',
            file_path VARCHAR(500) COMMENT '音频文件路径',
            cover_image VARCHAR(500) COMMENT '封面图片路径',
            is_public BOOLEAN DEFAULT TRUE COMMENT '是否公开',
            is_featured BOOLEAN DEFAULT FALSE COMMENT '是否推荐',
            play_count INT DEFAULT 0 COMMENT '播放次数',
            like_count INT DEFAULT 0 COMMENT '点赞次数',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            created_by INT COMMENT '创建者ID',
            status ENUM('draft', 'published', 'archived') DEFAULT 'draft' COMMENT '状态'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='音乐表'
        """
        
        cursor.execute(create_table_sql)
        print("✅ music表创建成功")
        
        # 创建索引
        print("正在创建索引...")
        indexes = [
            "CREATE INDEX idx_music_title ON music(title)",
            "CREATE INDEX idx_music_artist ON music(artist)",
            "CREATE INDEX idx_music_genre ON music(genre)",
            "CREATE INDEX idx_music_created_at ON music(created_at)",
            "CREATE INDEX idx_music_status ON music(status)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ 索引创建完成")
        
        # 插入示例数据
        print("正在插入示例数据...")
        sample_data = [
            ('春日序曲', '音乐创作者', '古典', 180, 120, 'C大调', '4/4', '一首充满春天气息的古典音乐作品', True, 'published'),
            ('夜空中最亮的星', '独立音乐人', '流行', 240, 85, 'G大调', '4/4', '温暖治愈的流行歌曲', True, 'published'),
            ('电子舞曲', 'DJ制作人', '电子', 200, 128, 'A小调', '4/4', '动感十足的电子舞曲', True, 'published'),
            ('爵士即兴', '爵士乐手', '爵士', 300, 90, 'F大调', '3/4', '自由即兴的爵士乐作品', True, 'published'),
            ('民谣故事', '民谣歌手', '民谣', 280, 75, 'D大调', '6/8', '讲述生活故事的民谣歌曲', True, 'published')
        ]
        
        insert_sql = """
        INSERT INTO music (title, artist, genre, duration, bpm, key_signature, time_signature, description, is_public, status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_sql, sample_data)
        print("✅ 示例数据插入完成")
        
        # 提交更改
        connection.commit()
        print("✅ 数据库更改已提交")
        
        # 验证表是否创建成功
        cursor.execute("SHOW TABLES LIKE 'music'")
        if cursor.fetchone():
            print("✅ music表验证成功！")
            
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
        
        cursor.close()
        connection.close()
        print("✅ 数据库连接已关闭")
        
    except Error as e:
        print(f"❌ 数据库操作失败: {e}")

if __name__ == "__main__":
    print("=== 开始创建music表 ===")
    create_music_table()
    print("=== music表创建完成 ===") 
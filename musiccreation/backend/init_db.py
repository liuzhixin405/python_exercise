#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_database
from flask import Flask

def main():
    """主函数"""
    print("=== 开始初始化数据库 ===")
    
    # 创建Flask应用上下文
    app = Flask(__name__)
    
    # 配置数据库
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', '127.0.0.1')
    app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3307))
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '123456')
    app.config['MYSQL_DATABASE'] = os.getenv('MYSQL_DATABASE', 'musiccreation')
    
    with app.app_context():
        try:
            # 初始化数据库
            init_database()
            print("✅ 数据库初始化完成")
            
            # 测试连接
            from database import db
            result = db.execute_query("SELECT COUNT(*) as count FROM users")
            print(f"✅ 用户表中有 {result[0]['count']} 条记录")
            
            result = db.execute_query("SELECT COUNT(*) as count FROM news")
            print(f"✅ 新闻表中有 {result[0]['count']} 条记录")
            
            result = db.execute_query("SELECT COUNT(*) as count FROM music")
            print(f"✅ 音乐表中有 {result[0]['count']} 条记录")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main() 
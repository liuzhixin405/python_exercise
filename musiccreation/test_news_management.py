#!/usr/bin/env python3
"""
测试新闻管理功能
"""
import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from admin.models.mysql_data_store import mysql_data_store

def test_news_management():
    """测试新闻管理功能"""
    print("🧪 测试新闻管理功能...")
    
    # 创建Flask应用上下文
    from flask import Flask
    from database import db
    
    app = Flask(__name__)
    app.config['MYSQL_HOST'] = '127.0.0.1'
    app.config['MYSQL_PORT'] = 3307
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '123456'
    app.config['MYSQL_DATABASE'] = 'musiccreation'
    
    db.init_app(app)
    
    with app.app_context():
        # 测试获取新闻列表
        print("\n1. 测试获取新闻列表:")
        result = mysql_data_store.get_news_paginated(page=1, per_page=10)
        print(f"✅ 总新闻数: {result['total']}")
        print(f"✅ 当前页新闻数: {len(result['news'])}")
        print(f"✅ 总页数: {result['pages']}")
        
        for news in result['news']:
            print(f"  - {news['title']} (作者: {news['author']})")
        
        # 测试创建新闻
        print("\n2. 测试创建新闻:")
        test_title = "测试新闻标题"
        test_description = "这是一个测试新闻的描述"
        test_image_url = "https://via.placeholder.com/300x200?text=Test+News"
        test_author = "admin"
        
        new_news = mysql_data_store.create_news(test_title, test_description, test_image_url, test_author)
        if new_news:
            print(f"✅ 创建新闻成功: {new_news['title']}")
        else:
            print("❌ 创建新闻失败")
        
        # 再次获取新闻列表
        print("\n3. 再次获取新闻列表:")
        result = mysql_data_store.get_news_paginated(page=1, per_page=10)
        print(f"✅ 总新闻数: {result['total']}")
        print(f"✅ 当前页新闻数: {len(result['news'])}")
        
        # 测试获取单个新闻
        if result['news']:
            first_news = result['news'][0]
            print(f"\n4. 测试获取单个新闻:")
            news_detail = mysql_data_store.get_news_by_id(first_news['id'])
            if news_detail:
                print(f"✅ 获取新闻成功: {news_detail['title']}")
                print(f"  - 描述: {news_detail['description'][:50]}...")
                print(f"  - 作者: {news_detail['author']}")
                print(f"  - 创建时间: {news_detail['created_at']}")
            else:
                print("❌ 获取新闻失败")
        
        print("\n🎉 新闻管理功能测试完成!")

if __name__ == "__main__":
    test_news_management() 
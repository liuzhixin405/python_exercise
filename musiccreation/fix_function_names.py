#!/usr/bin/env python3
"""
修复backend/app.py中的函数名冲突问题
"""
import re

def fix_function_names():
    """修复函数名冲突"""
    file_path = "backend/app.py"
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复数据库操作函数名
    replacements = [
        # 重命名数据库操作函数
        (r'def create_news\(title, description, content, image_url, author_id, author_name\):', 
         'def create_news_in_db(title, description, content, image_url, author_id, author_name):'),
        
        (r'def update_news\(news_id, title, description, content, image_url\):', 
         'def update_news_in_db(news_id, title, description, content, image_url):'),
        
        (r'def delete_news\(news_id\):', 
         'def delete_news_in_db(news_id):'),
        
        # 修复函数调用
        (r'create_news\(title, description, description, image_url, user_id, user\[\'username\'\]\)', 
         'create_news_in_db(title, description, description, image_url, user_id, user[\'username\'])'),
        
        (r'update_news\(news_id, title, description, description, image_url\)', 
         'update_news_in_db(news_id, title, description, description, image_url)'),
        
        (r'delete_news\(news_id\)', 
         'delete_news_in_db(news_id)'),
    ]
    
    # 应用替换
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 函数名冲突修复完成！")

if __name__ == "__main__":
    fix_function_names() 
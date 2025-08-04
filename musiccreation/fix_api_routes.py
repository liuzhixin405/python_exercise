#!/usr/bin/env python3
"""
恢复API路由函数名，只保留数据库操作函数的重命名
"""
import re

def fix_api_routes():
    """恢复API路由函数名"""
    file_path = "backend/app.py"
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 恢复API路由函数名
    replacements = [
        # 恢复API路由函数名
        (r'def delete_news_in_db\(news_id\):\s*\n\s*"""删除新闻"""', 
         'def delete_news(news_id):\n    """删除新闻"""'),
        
        (r'def admin_delete_news_in_db\(news_id\):\s*\n\s*"""管理员删除新闻"""', 
         'def admin_delete_news(news_id):\n    """管理员删除新闻"""'),
    ]
    
    # 应用替换
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ API路由函数名恢复完成！")

if __name__ == "__main__":
    fix_api_routes() 
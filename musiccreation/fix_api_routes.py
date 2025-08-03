#!/usr/bin/env python3
"""
修复API路由中data_store引用的脚本
"""

def fix_api_routes():
    """修复API路由文件中的data_store引用"""
    file_path = "backend/admin/routes/api.py"
    
    print(f"正在修复文件: {file_path}")
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义替换映射
    replacements = [
        ("data_store.get_user_by_username", "mysql_data_store.get_user_by_username"),
        ("data_store.users.values()", "mysql_data_store.get_all_users()"),
        ("data_store.create_user", "mysql_data_store.create_user"),
        ("data_store.get_stats", "mysql_data_store.get_stats"),
        ("data_store.get_news_paginated", "mysql_data_store.get_news_paginated"),
        ("data_store.create_news", "mysql_data_store.create_news"),
        ("data_store.get_news_by_id", "mysql_data_store.get_news_by_id"),
        ("data_store.update_news", "mysql_data_store.update_news"),
        ("data_store.delete_news", "mysql_data_store.delete_news"),
    ]
    
    # 应用替换
    original_content = content
    for old, new in replacements:
        content = content.replace(old, new)
    
    # 如果内容有变化，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已修复: {file_path}")
        return True
    else:
        print(f"⏭️  无需修复: {file_path}")
        return False

if __name__ == "__main__":
    fix_api_routes() 
#!/usr/bin/env python3
"""
修复模板文件中路由问题的脚本
"""

import os
import re

def fix_routes_in_file(file_path):
    """修复单个文件中的路由问题"""
    print(f"正在修复文件: {file_path}")
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义路由映射
    route_mapping = {
        r"url_for\('admin_login'\)": "url_for('auth.admin_login')",
        r"url_for\('admin_register'\)": "url_for('auth.admin_register')",
        r"url_for\('admin_logout'\)": "url_for('auth.admin_logout')",
        r"url_for\('admin_dashboard'\)": "url_for('dashboard.admin_dashboard')",
        r"url_for\('admin_users'\)": "url_for('users.admin_users')",
        r"url_for\('admin_news'\)": "url_for('news.admin_news')",
        r"url_for\('create_news'\)": "url_for('news.create_news')",
        r"url_for\('edit_news'\)": "url_for('news.edit_news')",
        r"url_for\('delete_news'\)": "url_for('news.delete_news')"
    }
    
    # 应用修复
    original_content = content
    for pattern, replacement in route_mapping.items():
        content = re.sub(pattern, replacement, content)
    
    # 如果内容有变化，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已修复: {file_path}")
        return True
    else:
        print(f"⏭️  无需修复: {file_path}")
        return False

def fix_all_templates():
    """修复所有模板文件"""
    template_dir = "backend/templates/admin"
    
    if not os.path.exists(template_dir):
        print(f"❌ 模板目录不存在: {template_dir}")
        return
    
    # 获取所有HTML文件
    html_files = []
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"找到 {len(html_files)} 个HTML文件")
    
    fixed_count = 0
    for file_path in html_files:
        if fix_routes_in_file(file_path):
            fixed_count += 1
    
    print(f"\n✅ 修复完成！共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    fix_all_templates() 
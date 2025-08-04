#!/usr/bin/env python3
"""
批量修复管理后台模板中的URL引用
"""
import os
import re

def fix_admin_urls():
    """修复管理后台模板中的URL引用"""
    template_dir = "backend/templates/admin"
    
    # URL映射
    url_mapping = {
        r"url_for\('dashboard\.admin_dashboard'\)": "url_for('admin_dashboard_page')",
        r"url_for\('users\.admin_users'\)": "url_for('admin_users_page')",
        r"url_for\('news\.admin_news'\)": "url_for('admin_news_page')",
        r"url_for\('auth\.admin_logout'\)": "url_for('admin_logout_page')",
        r"url_for\('auth\.admin_login'\)": "url_for('admin_login_page')",
        r"url_for\('auth\.admin_register'\)": "url_for('admin_register_page')"
    }
    
    # 获取所有HTML文件
    html_files = []
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"找到 {len(html_files)} 个HTML文件")
    
    fixed_count = 0
    for file_path in html_files:
        print(f"正在处理: {file_path}")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 应用URL映射
        original_content = content
        for pattern, replacement in url_mapping.items():
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已修复: {file_path}")
            fixed_count += 1
        else:
            print(f"⏭️  无需修复: {file_path}")
    
    print(f"\n✅ 修复完成！共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    fix_admin_urls() 
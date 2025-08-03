#!/usr/bin/env python3
"""
测试后台用户功能
"""
import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from admin.models.admin_data_store import admin_data_store
from admin.utils.auth import hash_password, check_password

def test_admin_users():
    """测试后台用户功能"""
    print("🧪 测试后台用户功能...")
    
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
        # 测试获取管理员用户
        print("\n1. 测试获取管理员用户:")
        admin_user = admin_data_store.get_admin_user_by_username('admin')
        if admin_user:
            print(f"✅ 找到管理员用户: {admin_user['username']} ({admin_user['role']})")
        else:
            print("❌ 未找到管理员用户")
    
        # 测试创建新用户
        print("\n2. 测试创建新用户:")
        test_username = 'testuser'
        test_email = 'test@example.com'
        
        # 检查用户是否已存在
        if admin_data_store.check_username_exists(test_username):
            print(f"⏭️  用户 {test_username} 已存在")
        else:
            password_hash = hash_password('test123')
            new_user = admin_data_store.create_admin_user(
                username=test_username,
                email=test_email,
                password_hash=password_hash,
                real_name='测试用户',
                role='editor'
            )
            if new_user:
                print(f"✅ 创建用户成功: {new_user['username']} ({new_user['role']})")
            else:
                print("❌ 创建用户失败")
        
        # 测试获取所有用户
        print("\n3. 测试获取所有用户:")
        result = admin_data_store.get_all_admin_users(page=1, per_page=10)
        print(f"✅ 总用户数: {result['total']}")
        print(f"✅ 当前页用户数: {len(result['users'])}")
        for user in result['users']:
            print(f"  - {user['username']} ({user['role']}) - {'激活' if user['is_active'] else '禁用'}")
        
        # 测试统计信息
        print("\n4. 测试统计信息:")
        stats = admin_data_store.get_admin_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 测试密码验证
        print("\n5. 测试密码验证:")
        if admin_user:
            is_valid = check_password(admin_user['password_hash'], 'admin123')
            print(f"✅ 管理员密码验证: {'成功' if is_valid else '失败'}")
        
        print("\n🎉 后台用户功能测试完成!")

if __name__ == "__main__":
    test_admin_users() 
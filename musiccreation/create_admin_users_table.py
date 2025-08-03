#!/usr/bin/env python3
"""
创建后台用户表的脚本
"""
import mysql.connector
from mysql.connector import Error

def create_admin_users_table():
    """创建后台用户表"""
    config = {
        'host': '127.0.0.1',
        'port': 3307,
        'user': 'root',
        'password': '123456',
        'database': 'musiccreation'
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("✅ 数据库连接成功")
        
        # 创建后台用户表
        create_admin_users_table_sql = """
        CREATE TABLE IF NOT EXISTS admin_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
            email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
            password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
            real_name VARCHAR(100) COMMENT '真实姓名',
            role ENUM('admin', 'editor', 'viewer') DEFAULT 'viewer' COMMENT '角色',
            is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
            last_login TIMESTAMP NULL COMMENT '最后登录时间',
            login_count INT DEFAULT 0 COMMENT '登录次数',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='后台用户表'
        """
        
        cursor.execute(create_admin_users_table_sql)
        print("✅ 后台用户表创建成功")
        
        # 创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username)",
            "CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email)",
            "CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role)",
            "CREATE INDEX IF NOT EXISTS idx_admin_users_is_active ON admin_users(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_admin_users_created_at ON admin_users(created_at)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ 索引创建成功")
            except Error as e:
                if "Duplicate key name" in str(e):
                    print(f"⏭️  索引已存在")
                else:
                    print(f"❌ 索引创建失败: {e}")
        
        # 检查是否已有管理员用户
        cursor.execute("SELECT COUNT(*) FROM admin_users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # 创建默认管理员用户
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
            
            insert_admin_sql = """
            INSERT INTO admin_users (username, email, password_hash, real_name, role, is_active) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_admin_sql, ('admin', 'admin@feedmusic.com', password_hash, '系统管理员', 'admin', True))
            print("✅ 默认管理员用户创建成功: admin / admin123")
        else:
            print(f"⏭️  已有 {admin_count} 个管理员用户")
        
        connection.commit()
        print("✅ 数据库操作完成")
        
        # 显示表结构
        cursor.execute("DESCRIBE admin_users")
        columns = cursor.fetchall()
        print("\n📋 后台用户表结构:")
        for column in columns:
            print(f"  {column[0]}: {column[1]} - {column[8]}")
        
        # 显示用户列表
        cursor.execute("SELECT id, username, email, role, is_active, created_at FROM admin_users")
        users = cursor.fetchall()
        print(f"\n👥 后台用户列表 ({len(users)} 个用户):")
        for user in users:
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}, 状态: {'激活' if user[4] else '禁用'}, 创建时间: {user[5]}")
        
    except Error as e:
        print(f"❌ 数据库操作失败: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ 数据库连接已关闭")

if __name__ == "__main__":
    create_admin_users_table() 
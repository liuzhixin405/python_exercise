#!/usr/bin/env python3
"""
检查数据库结构
"""
import pymysql
from pymysql.cursors import DictCursor

def check_db_structure():
    """检查数据库结构"""
    try:
        # 连接参数
        host = '127.0.0.1'
        port = 3307
        user = 'root'
        password = '123456'
        database = 'musiccreation'
        
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        
        with connection.cursor() as cursor:
            # 检查users表结构
            cursor.execute("DESCRIBE users")
            users_columns = cursor.fetchall()
            print("Users表结构:")
            for col in users_columns:
                print(f"  {col['Field']}: {col['Type']} {col['Null']} {col['Key']} {col['Default']}")
            
            print("\n" + "="*50 + "\n")
            
            # 检查news表结构
            cursor.execute("DESCRIBE news")
            news_columns = cursor.fetchall()
            print("News表结构:")
            for col in news_columns:
                print(f"  {col['Field']}: {col['Type']} {col['Null']} {col['Key']} {col['Default']}")
            
            print("\n" + "="*50 + "\n")
            
            # 检查现有数据
            cursor.execute("SELECT COUNT(*) as count FROM users")
            users_count = cursor.fetchone()['count']
            print(f"Users表记录数: {users_count}")
            
            cursor.execute("SELECT COUNT(*) as count FROM news")
            news_count = cursor.fetchone()['count']
            print(f"News表记录数: {news_count}")
            
            if users_count > 0:
                cursor.execute("SELECT * FROM users LIMIT 3")
                users = cursor.fetchall()
                print("\nUsers表前3条记录:")
                for user in users:
                    print(f"  ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ 检查数据库结构失败: {e}")

if __name__ == "__main__":
    check_db_structure() 
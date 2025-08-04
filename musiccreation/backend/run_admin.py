"""
后台管理应用启动文件
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ['MYSQL_HOST'] = '127.0.0.1'
os.environ['MYSQL_PORT'] = '3307'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = '123456'
os.environ['MYSQL_DATABASE'] = 'musiccreation'

from app import app

if __name__ == '__main__':
    print("🚀 启动后台管理应用...")
    print("📊 后台管理地址: http://localhost:5001/admin/login")
    print("🔑 默认管理员账号: admin / admin123")
    print("🔗 数据库连接: 127.0.0.1:3307")
    app.run(debug=True, host='0.0.0.0', port=5001) 
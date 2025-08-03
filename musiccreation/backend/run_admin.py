"""
后台管理应用启动文件
"""
from admin import create_app, init_data_store

app = create_app('development')

if __name__ == '__main__':
    # 在应用上下文中初始化数据存储
    with app.app_context():
        init_data_store()
    
    print("🚀 启动后台管理应用...")
    print("📊 后台管理地址: http://localhost:5001/admin/login")
    print("🔑 默认管理员账号: admin / admin123")
    app.run(debug=True, host='0.0.0.0', port=5001) 
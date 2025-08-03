#!/usr/bin/env python3
"""
启动包含后台管理的应用
"""
import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from admin import create_app

if __name__ == "__main__":
    app = create_app()
    
    print("🚀 启动后台管理应用...")
    print("📊 后台管理地址: http://localhost:5000/admin/login")
    print("🔑 默认管理员账号: admin / admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
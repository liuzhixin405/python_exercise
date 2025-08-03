"""
认证工具函数
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def require_admin(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password: str) -> str:
    """加密密码"""
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(password_hash: str, password: str) -> bool:
    """验证密码"""
    return bcrypt.check_password_hash(password_hash, password)

def login_user(user_data: dict):
    """用户登录"""
    session['admin_logged_in'] = True
    session['admin_user'] = {
        'id': user_data['id'],
        'username': user_data['username'],
        'email': user_data['email'],
        'is_admin': user_data.get('is_admin', False)
    }

def logout_user():
    """用户登出"""
    session.clear()

def get_current_user():
    """获取当前登录用户"""
    if 'admin_logged_in' in session:
        return session.get('admin_user')
    return None 
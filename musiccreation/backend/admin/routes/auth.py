"""
认证路由 - 处理登录、注册、登出
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from admin.models.admin_data_store import admin_data_store
from admin.utils.auth import hash_password, check_password, login_user, logout_user, require_admin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def root():
    """根路径，直接跳转到登录页面"""
    return redirect(url_for('auth.admin_login'))

@auth_bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # 验证输入
        if not username or len(username) < 3 or len(username) > 20:
            flash('用户名长度必须在3-20字符之间！', 'error')
            return render_template('admin/register.html')
        
        if not email or '@' not in email:
            flash('请输入有效的邮箱地址！', 'error')
            return render_template('admin/register.html')
        
        if not password or len(password) < 6:
            flash('密码长度不能少于6位！', 'error')
            return render_template('admin/register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致！', 'error')
            return render_template('admin/register.html')
        
        # 检查用户名是否已存在
        if admin_data_store.check_username_exists(username):
            flash('用户名已存在！', 'error')
            return render_template('admin/register.html')
        
        # 检查邮箱是否已存在
        if admin_data_store.check_email_exists(email):
            flash('邮箱已被注册！', 'error')
            return render_template('admin/register.html')
        
        # 创建新后台用户
        password_hash = hash_password(password)
        admin_data_store.create_admin_user(username, email, password_hash, real_name=username, role='viewer')
        
        flash('注册成功！请登录。', 'success')
        return redirect(url_for('auth.admin_login'))
    
    return render_template('admin/register.html')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = admin_data_store.get_admin_user_by_username(username)
        
        if user and check_password(user['password_hash'], password):
            # 更新登录信息
            admin_data_store.update_login_info(user['id'])
            login_user(user)
            flash('登录成功！', 'success')
            return redirect(url_for('dashboard.admin_dashboard'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('admin/simple_login.html')

@auth_bp.route('/admin/logout')
def admin_logout():
    """管理员登出"""
    logout_user()
    flash('已退出登录！', 'success')
    return redirect(url_for('auth.admin_login')) 
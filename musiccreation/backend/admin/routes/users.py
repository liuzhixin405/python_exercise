"""
用户管理路由 - 处理用户管理页面
"""
from flask import Blueprint, render_template, request
from admin.utils.auth import require_admin
from admin.models.admin_data_store import admin_data_store

users_bp = Blueprint('users', __name__)

@users_bp.route('/admin/users')
@require_admin
def admin_users():
    """用户管理"""
    page = request.args.get('page', 1, type=int)
    result = admin_data_store.get_all_admin_users(page=page, per_page=20)
    return render_template('admin/simple_users.html', users=result['users'], pagination=result) 
"""
仪表板路由 - 处理仪表板页面
"""
from flask import Blueprint, render_template
from admin.utils.auth import require_admin
from admin.models.admin_data_store import admin_data_store

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/admin')
@require_admin
def admin_dashboard():
    """管理后台首页"""
    # 统计数据
    stats = admin_data_store.get_admin_stats()
    
    return render_template('admin/simple_dashboard.html', stats=stats) 
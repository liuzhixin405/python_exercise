"""
API路由 - 处理RESTful API接口
"""
from flask import Blueprint, request, jsonify, send_from_directory
from admin.models.mysql_data_store import mysql_data_store
from admin.models.admin_data_store import admin_data_store
from admin.utils.auth import hash_password, check_password, login_user, logout_user, get_current_user
from admin.utils.file_upload import save_uploaded_file, allowed_file

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/admin/register', methods=['POST'])
def api_admin_register():
    """API: 管理员注册"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # 验证输入
        if not username or len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': '用户名长度必须在3-20字符之间！'}), 400
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'message': '请输入有效的邮箱地址！'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'success': False, 'message': '密码长度不能少于6位！'}), 400
        
        # 检查用户名是否已存在
        if admin_data_store.check_username_exists(username):
            return jsonify({'success': False, 'message': '用户名已存在！'}), 400
        
        # 检查邮箱是否已存在
        if admin_data_store.check_email_exists(email):
            return jsonify({'success': False, 'message': '邮箱已被注册！'}), 400
        
        # 创建新用户
        password_hash = hash_password(password)
        admin_data_store.create_admin_user(username, email, password_hash, role='viewer')
        
        return jsonify({'success': True, 'message': '注册成功！'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败：{str(e)}'}), 500

@api_bp.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    """API: 管理员登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = admin_data_store.get_admin_user_by_username(username)
        
        if user and check_password(user['password_hash'], password):
            # 更新登录信息
            admin_data_store.update_login_info(user['id'])
            login_user(user)
            return jsonify({
                'success': True, 
                'message': '登录成功！',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user.get('role', 'viewer')
                }
            })
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误！'}), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败：{str(e)}'}), 500

@api_bp.route('/api/admin/logout', methods=['POST'])
def api_admin_logout():
    """API: 管理员登出"""
    logout_user()
    return jsonify({'success': True, 'message': '已退出登录！'})

@api_bp.route('/api/admin/stats')
def api_admin_stats():
    """API: 获取统计数据"""
    if not get_current_user():
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        stats = admin_data_store.get_admin_stats()
        return jsonify({'success': True, 'stats': stats})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取统计数据失败：{str(e)}'}), 500

@api_bp.route('/api/admin/users')
def api_admin_users():
    """API: 获取用户列表"""
    if not get_current_user():
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        result = admin_data_store.get_all_admin_users(page=page, per_page=per_page)
        return jsonify({
            'success': True, 
            'users': result['users'],
            'pagination': {
                'current_page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'total_pages': result['pages']
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户列表失败：{str(e)}'}), 500

@api_bp.route('/api/admin/news', methods=['GET'])
def api_admin_news_list():
    """API: 获取新闻列表（分页）"""
    if not get_current_user():
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        result = mysql_data_store.get_news_paginated(page, per_page)
        return jsonify({
            'success': True, 
            'news': result['news'],
            'pagination': {
                'current_page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'total_pages': result['pages']
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取新闻列表失败：{str(e)}'}), 500

@api_bp.route('/api/admin/news', methods=['POST'])
def api_admin_news_create():
    """API: 创建新闻"""
    if not get_current_user():
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        image_url = data.get('image_url', '').strip()
        
        # 验证输入
        if not title:
            return jsonify({'success': False, 'message': '标题不能为空！'}), 400
        
        if not description:
            return jsonify({'success': False, 'message': '描述不能为空！'}), 400
        
        # 获取当前用户
        current_user = get_current_user()
        author = current_user['username']
        
        # 创建新闻
        new_news = mysql_data_store.create_news(title, description, image_url, author)
        
        return jsonify({
            'success': True, 
            'message': '新闻创建成功！',
            'news': new_news
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建新闻失败：{str(e)}'}), 500

@api_bp.route('/api/admin/news/<int:news_id>', methods=['GET'])
def api_admin_news_detail(news_id):
    """API: 获取新闻详情"""
    if not get_current_user():
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        news = mysql_data_store.get_news_by_id(news_id)
        if not news:
            return jsonify({'success': False, 'message': '新闻不存在！'}), 404
        
        return jsonify({'success': True, 'news': news})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取新闻详情失败：{str(e)}'}), 500

@api_bp.route('/api/admin/news/<int:news_id>', methods=['PUT'])
def api_admin_news_update(news_id):
    """API: 更新新闻"""
    if not get_current_user():
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        image_url = data.get('image_url', '').strip()
        
        # 验证输入
        if not title:
            return jsonify({'success': False, 'message': '标题不能为空！'}), 400
        
        if not description:
            return jsonify({'success': False, 'message': '描述不能为空！'}), 400
        
        # 更新新闻
        updated_news = mysql_data_store.update_news(news_id, title, description, image_url)
        if not updated_news:
            return jsonify({'success': False, 'message': '新闻不存在！'}), 404
        
        return jsonify({
            'success': True, 
            'message': '新闻更新成功！',
            'news': updated_news
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新新闻失败：{str(e)}'}), 500

@api_bp.route('/api/admin/news/<int:news_id>', methods=['DELETE'])
def api_admin_news_delete(news_id):
    """API: 删除新闻"""
    if not get_current_user():
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        success = mysql_data_store.delete_news(news_id)
        if not success:
            return jsonify({'success': False, 'message': '新闻不存在！'}), 404
        
        return jsonify({'success': True, 'message': '新闻删除成功！'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除新闻失败：{str(e)}'}), 500

@api_bp.route('/api/admin/upload', methods=['POST'])
def api_admin_upload():
    """API: 文件上传"""
    if not get_current_user():
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件！'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件！'}), 400
        
        if file and allowed_file(file.filename):
            filename = save_uploaded_file(file)
            return jsonify({
                'success': True, 
                'message': '文件上传成功！',
                'filename': filename,
                'url': f'/uploads/{filename}'
            })
        else:
            return jsonify({'success': False, 'message': '不支持的文件类型！'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'文件上传失败：{str(e)}'}), 500

@api_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    import os
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
    return send_from_directory(upload_folder, filename)

@api_bp.route('/test')
def test_api():
    """API测试页面"""
    return send_from_directory('.', 'test_api.html') 
 
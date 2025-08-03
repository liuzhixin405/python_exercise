from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
import json

# 导入主应用的数据
from app import users, news_data, bcrypt, get_user_by_username, get_news_by_id, user_id_counter, news_id_counter

admin_app = Flask(__name__)
admin_app.secret_key = 'admin-secret-key'

# 启用CORS
CORS(admin_app)

# 配置
admin_app.config['UPLOAD_FOLDER'] = 'uploads'
admin_app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(admin_app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_admin(f):
    """管理员权限装饰器"""
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ==================== API 接口 ====================

@admin_app.route('/api/admin/register', methods=['POST'])
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
        if get_user_by_username(username):
            return jsonify({'success': False, 'message': '用户名已存在！'}), 400
        
        # 检查邮箱是否已存在
        for user in users.values():
            if user['email'] == email:
                return jsonify({'success': False, 'message': '邮箱已被注册！'}), 400
        
        # 创建新用户
        global user_id_counter
        user_id_counter += 1
        
        new_user = {
            'id': user_id_counter,
            'username': username,
            'email': email,
            'password_hash': bcrypt.generate_password_hash(password).decode('utf-8'),
            'is_admin': False,  # 默认不是管理员
            'created_at': datetime.utcnow().isoformat()
        }
        
        users[user_id_counter] = new_user
        
        return jsonify({'success': True, 'message': '注册成功！'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败：{str(e)}'}), 500

@admin_app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    """API: 管理员登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = get_user_by_username(username)
        
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['admin_logged_in'] = True
            session['admin_user'] = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user.get('is_admin', False)
            }
            return jsonify({
                'success': True, 
                'message': '登录成功！',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user.get('is_admin', False)
                }
            })
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误！'}), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败：{str(e)}'}), 500

@admin_app.route('/api/admin/logout', methods=['POST'])
def api_admin_logout():
    """API: 管理员登出"""
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录！'})

@admin_app.route('/api/admin/stats')
def api_admin_stats():
    """API: 获取统计数据"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        stats = {
            'total_users': len(users),
            'total_news': len(news_data),
            'admin_users': len([u for u in users.values() if u.get('is_admin', False)]),
            'recent_news': len([n for n in news_data if datetime.fromisoformat(n['created_at']) > datetime.utcnow() - timedelta(days=7)])
        }
        return jsonify({'success': True, 'stats': stats})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取统计数据失败：{str(e)}'}), 500

@admin_app.route('/api/admin/users')
def api_admin_users():
    """API: 获取用户列表"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        user_list = []
        for user in users.values():
            user_list.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user.get('is_admin', False),
                'created_at': user['created_at']
            })
        
        return jsonify({'success': True, 'users': user_list})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户列表失败：{str(e)}'}), 500

@admin_app.route('/api/admin/news')
def api_admin_news():
    """API: 获取新闻列表（分页）"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start = (page - 1) * per_page
        end = start + per_page
        
        # 按创建时间倒序排列
        sorted_news = sorted(news_data, key=lambda x: x['created_at'], reverse=True)
        paginated_news = sorted_news[start:end]
        
        total_pages = (len(news_data) + per_page - 1) // per_page
        
        return jsonify({
            'success': True, 
            'news': paginated_news,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': len(news_data),
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取新闻列表失败：{str(e)}'}), 500

@admin_app.route('/api/admin/news', methods=['POST'])
def api_create_news():
    """API: 创建新闻"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        image_url = data.get('image_url', '').strip()
        
        # 验证输入
        if not title or len(title) > 100:
            return jsonify({'success': False, 'message': '标题不能为空且长度不能超过100字符！'}), 400
        
        if not description or len(description) > 500:
            return jsonify({'success': False, 'message': '描述不能为空且长度不能超过500字符！'}), 400
        
        if not image_url:
            return jsonify({'success': False, 'message': '请提供图片URL！'}), 400
        
        # 创建新闻
        global news_id_counter
        news_id_counter += 1
        
        new_news = {
            'id': news_id_counter,
            'title': title,
            'description': description,
            'image_url': image_url,
            'author': session['admin_user']['username'],
            'author_id': session['admin_user']['id'],  # 添加作者ID
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        news_data.append(new_news)
        return jsonify({'success': True, 'message': '新闻创建成功！', 'news': new_news})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建新闻失败：{str(e)}'}), 500

@admin_app.route('/api/admin/news/<int:news_id>', methods=['PUT'])
def api_update_news(news_id):
    """API: 更新新闻"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        news = get_news_by_id(news_id)
        if not news:
            return jsonify({'success': False, 'message': '新闻不存在！'}), 404
        
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        image_url = data.get('image_url', '').strip()
        
        # 验证输入
        if not title or len(title) > 100:
            return jsonify({'success': False, 'message': '标题不能为空且长度不能超过100字符！'}), 400
        
        if not description or len(description) > 500:
            return jsonify({'success': False, 'message': '描述不能为空且长度不能超过500字符！'}), 400
        
        # 更新新闻
        news['title'] = title
        news['description'] = description
        if image_url:
            news['image_url'] = image_url
        news['updated_at'] = datetime.utcnow().isoformat()
        
        return jsonify({'success': True, 'message': '新闻更新成功！', 'news': news})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新新闻失败：{str(e)}'}), 500

@admin_app.route('/api/admin/news/<int:news_id>', methods=['DELETE'])
def api_delete_news(news_id):
    """API: 删除新闻"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        news = get_news_by_id(news_id)
        if not news:
            return jsonify({'success': False, 'message': '新闻不存在！'}), 404
        
        # 从列表中删除
        news_data[:] = [n for n in news_data if n['id'] != news_id]
        
        return jsonify({'success': True, 'message': '新闻删除成功！'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除新闻失败：{str(e)}'}), 500

@admin_app.route('/api/admin/upload', methods=['POST'])
def api_upload_image():
    """API: 上传图片"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': '未登录！'}), 401
    
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件！'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件！'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 添加时间戳避免文件名冲突
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(admin_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            image_url = f"/uploads/{filename}"
            return jsonify({
                'success': True, 
                'message': '图片上传成功！',
                'image_url': image_url,
                'filename': filename
            })
        else:
            return jsonify({'success': False, 'message': '不支持的文件格式！'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'图片上传失败：{str(e)}'}), 500

# ==================== 现有的HTML模板路由 ====================

@admin_app.route('/admin/register', methods=['GET', 'POST'])
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
        if get_user_by_username(username):
            flash('用户名已存在！', 'error')
            return render_template('admin/register.html')
        
        # 检查邮箱是否已存在
        for user in users.values():
            if user['email'] == email:
                flash('邮箱已被注册！', 'error')
                return render_template('admin/register.html')
        
        # 创建新用户
        global user_id_counter
        user_id_counter += 1
        
        new_user = {
            'id': user_id_counter,
            'username': username,
            'email': email,
            'password_hash': bcrypt.generate_password_hash(password).decode('utf-8'),
            'is_admin': False,  # 默认不是管理员
            'created_at': datetime.utcnow().isoformat()
        }
        
        users[user_id_counter] = new_user
        
        flash('注册成功！请登录。', 'success')
        return redirect(url_for('admin_login'))
    
    return render_template('admin/register.html')

@admin_app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user_by_username(username)
        
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['admin_logged_in'] = True
            session['admin_user'] = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user.get('is_admin', False)
            }
            flash('登录成功！', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('admin/simple_login.html')

@admin_app.route('/admin/logout')
def admin_logout():
    """管理员登出"""
    session.clear()
    flash('已退出登录！', 'success')
    return redirect(url_for('admin_login'))

@admin_app.route('/admin')
@require_admin
def admin_dashboard():
    """管理后台首页"""
    # 统计数据
    stats = {
        'total_users': len(users),
        'total_news': len(news_data),
        'admin_users': len([u for u in users.values() if u.get('is_admin', False)]),
        'recent_news': len([n for n in news_data if datetime.fromisoformat(n['created_at']) > datetime.utcnow() - timedelta(days=7)])
    }
    
    return render_template('admin/simple_dashboard.html', stats=stats)

@admin_app.route('/admin/users')
@require_admin
def admin_users():
    """用户管理"""
    user_list = []
    for user in users.values():
        user_list.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'is_admin': user.get('is_admin', False),
            'created_at': user['created_at']
        })
    
    return render_template('admin/simple_users.html', users=user_list)

@admin_app.route('/admin/news')
@require_admin
def admin_news():
    """新闻管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    
    # 按创建时间倒序排列
    sorted_news = sorted(news_data, key=lambda x: x['created_at'], reverse=True)
    paginated_news = sorted_news[start:end]
    
    total_pages = (len(news_data) + per_page - 1) // per_page
    
    return render_template('admin/simple_news.html', 
                         news=paginated_news, 
                         current_page=page, 
                         total_pages=total_pages)

@admin_app.route('/admin/news/create', methods=['GET', 'POST'])
@require_admin
def create_news():
    """创建新闻"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        # 验证输入
        if not title or len(title) > 100:
            flash('标题不能为空且长度不能超过100字符！', 'error')
            return render_template('admin/create_news.html')
        
        if not description or len(description) > 500:
            flash('描述不能为空且长度不能超过500字符！', 'error')
            return render_template('admin/create_news.html')
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 添加时间戳避免文件名冲突
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(admin_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f"/uploads/{filename}"
        
        if not image_url:
            flash('请提供图片URL或上传图片！', 'error')
            return render_template('admin/create_news.html')
        
        # 创建新闻
        global news_id_counter
        news_id_counter += 1
        
        new_news = {
            'id': news_id_counter,
            'title': title,
            'description': description,
            'image_url': image_url,
            'author': session['admin_user']['username'],
            'author_id': session['admin_user']['id'],  # 添加作者ID
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        news_data.append(new_news)
        flash('新闻创建成功！', 'success')
        return redirect(url_for('admin_news'))
    
    return render_template('admin/create_news.html')

@admin_app.route('/admin/news/edit/<int:news_id>', methods=['GET', 'POST'])
@require_admin
def edit_news(news_id):
    """编辑新闻"""
    news = get_news_by_id(news_id)
    if not news:
        flash('新闻不存在！', 'error')
        return redirect(url_for('admin_news'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        # 验证输入
        if not title or len(title) > 100:
            flash('标题不能为空且长度不能超过100字符！', 'error')
            return render_template('admin/edit_news.html', news=news)
        
        if not description or len(description) > 500:
            flash('描述不能为空且长度不能超过500字符！', 'error')
            return render_template('admin/edit_news.html', news=news)
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 添加时间戳避免文件名冲突
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(admin_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f"/uploads/{filename}"
        
        # 更新新闻
        news['title'] = title
        news['description'] = description
        if image_url:
            news['image_url'] = image_url
        news['updated_at'] = datetime.utcnow().isoformat()
        
        flash('新闻更新成功！', 'success')
        return redirect(url_for('admin_news'))
    
    return render_template('admin/edit_news.html', news=news)

@admin_app.route('/admin/news/delete/<int:news_id>', methods=['POST'])
@require_admin
def delete_news(news_id):
    """删除新闻"""
    news = get_news_by_id(news_id)
    if not news:
        flash('新闻不存在！', 'error')
        return redirect(url_for('admin_news'))
    
    # 从列表中删除
    news_data[:] = [n for n in news_data if n['id'] != news_id]
    
    flash('新闻删除成功！', 'success')
    return redirect(url_for('admin_news'))

@admin_app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(admin_app.config['UPLOAD_FOLDER'], filename)

@admin_app.route('/')
def root():
    """根路径，直接跳转到登录页面"""
    return redirect(url_for('admin_login'))

@admin_app.route('/test')
def test_api():
    """API测试页面"""
    return send_from_directory('.', 'test_api.html')

@admin_app.route('/api/admin/debug/news')
def api_debug_news():
    """调试API: 查看所有新闻数据"""
    try:
        print("Debug: All news_data in admin system:")
        for i, news in enumerate(news_data):
            print(f"  {i+1}. ID: {news.get('id')}, Title: {news.get('title')}, Author: {news.get('author')}, Author_ID: {news.get('author_id')}")
        
        return jsonify({
            'success': True,
            'total_news': len(news_data),
            'news_data': news_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'调试失败：{str(e)}'}), 500

if __name__ == '__main__':
    admin_app.run(debug=True, host='0.0.0.0', port=5001) 
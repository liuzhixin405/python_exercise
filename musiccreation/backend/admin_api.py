from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

# 导入主应用的数据
from app import users, news_data, bcrypt, get_user_by_username, get_news_by_id, user_id_counter, news_id_counter

admin_api = Flask(__name__)
admin_api.secret_key = 'admin-api-secret-key'

# 配置
admin_api.config['JWT_SECRET_KEY'] = 'admin-jwt-secret-key'
admin_api.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
admin_api.config['UPLOAD_FOLDER'] = 'uploads'
admin_api.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(admin_api.config['UPLOAD_FOLDER'], exist_ok=True)

jwt = JWTManager(admin_api)
CORS(admin_api)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_admin(f):
    """管理员权限装饰器"""
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            user = users.get(user_id)
            if not user or not user.get('is_admin', False):
                return jsonify({'error': '需要管理员权限'}), 403
            return f(*args, **kwargs)
        except:
            return jsonify({'error': '需要管理员权限'}), 403
    decorated_function.__name__ = f.__name__
    return decorated_function

# 管理员注册
@admin_api.route('/api/admin/register', methods=['POST'])
def admin_register():
    """管理员注册"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # 验证输入
        if not username or len(username) < 3 or len(username) > 20:
            return jsonify({'error': '用户名长度必须在3-20字符之间'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': '请输入有效的邮箱地址'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'error': '密码长度不能少于6位'}), 400
        
        # 检查用户名是否已存在
        if get_user_by_username(username):
            return jsonify({'error': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        for user in users.values():
            if user['email'] == email:
                return jsonify({'error': '邮箱已被注册'}), 400
        
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
        
        return jsonify({
            'message': '注册成功',
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'email': new_user['email'],
                'is_admin': new_user['is_admin']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

# 管理员登录
@admin_api.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        user = get_user_by_username(username)
        
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            # 创建JWT token
            access_token = create_access_token(identity=user['id'])
            
            return jsonify({
                'message': '登录成功',
                'access_token': access_token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user.get('is_admin', False)
                }
            }), 200
        else:
            return jsonify({'error': '用户名或密码错误'}), 401
            
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

# 获取管理后台统计信息
@admin_api.route('/api/admin/stats', methods=['GET'])
@jwt_required()
@require_admin
def get_admin_stats():
    """获取管理后台统计信息"""
    try:
        stats = {
            'total_users': len(users),
            'total_news': len(news_data),
            'admin_users': len([u for u in users.values() if u.get('is_admin', False)]),
            'recent_news': len([n for n in news_data if datetime.fromisoformat(n['created_at']) > datetime.utcnow() - timedelta(days=7)])
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500

# 获取所有用户
@admin_api.route('/api/admin/users', methods=['GET'])
@jwt_required()
@require_admin
def get_all_users():
    """获取所有用户"""
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
        
        return jsonify({'users': user_list}), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户列表失败: {str(e)}'}), 500

# 获取所有新闻（分页）
@admin_api.route('/api/admin/news', methods=['GET'])
@jwt_required()
@require_admin
def get_all_news():
    """获取所有新闻（分页）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 分页计算
        start = (page - 1) * per_page
        end = start + per_page
        
        # 按创建时间倒序排列
        sorted_news = sorted(news_data, key=lambda x: x['created_at'], reverse=True)
        paginated_news = sorted_news[start:end]
        
        total_pages = (len(news_data) + per_page - 1) // per_page
        
        return jsonify({
            'news': paginated_news,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_items': len(news_data)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取新闻列表失败: {str(e)}'}), 500

# 创建新闻
@admin_api.route('/api/admin/news', methods=['POST'])
@jwt_required()
@require_admin
def create_news():
    """创建新闻"""
    try:
        user_id = get_jwt_identity()
        user = users.get(user_id)
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        image_url = data.get('image_url', '').strip()
        
        # 验证输入
        if not title or len(title) > 100:
            return jsonify({'error': '标题不能为空且长度不能超过100字符'}), 400
        
        if not description or len(description) > 500:
            return jsonify({'error': '描述不能为空且长度不能超过500字符'}), 400
        
        if not image_url:
            return jsonify({'error': '请提供图片URL'}), 400
        
        # 创建新闻
        global news_id_counter
        news_id_counter += 1
        
        new_news = {
            'id': news_id_counter,
            'title': title,
            'description': description,
            'image_url': image_url,
            'author': user['username'],
            'author_id': user['id'],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        news_data.append(new_news)
        
        return jsonify({
            'message': '新闻创建成功',
            'news': new_news
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'创建新闻失败: {str(e)}'}), 500

# 更新新闻
@admin_api.route('/api/admin/news/<int:news_id>', methods=['PUT'])
@jwt_required()
@require_admin
def update_news(news_id):
    """更新新闻"""
    try:
        news = get_news_by_id(news_id)
        
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        image_url = data.get('image_url', '').strip()
        
        # 验证输入
        if not title or len(title) > 100:
            return jsonify({'error': '标题不能为空且长度不能超过100字符'}), 400
        
        if not description or len(description) > 500:
            return jsonify({'error': '描述不能为空且长度不能超过500字符'}), 400
        
        # 更新新闻
        news['title'] = title
        news['description'] = description
        if image_url:
            news['image_url'] = image_url
        news['updated_at'] = datetime.utcnow().isoformat()
        
        return jsonify({
            'message': '新闻更新成功',
            'news': news
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'更新新闻失败: {str(e)}'}), 500

# 删除新闻
@admin_api.route('/api/admin/news/<int:news_id>', methods=['DELETE'])
@jwt_required()
@require_admin
def delete_news(news_id):
    """删除新闻"""
    try:
        news = get_news_by_id(news_id)
        
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        # 从列表中删除
        news_data[:] = [n for n in news_data if n['id'] != news_id]
        
        return jsonify({'message': '新闻删除成功'}), 200
        
    except Exception as e:
        return jsonify({'error': f'删除新闻失败: {str(e)}'}), 500

# 图片上传
@admin_api.route('/api/admin/upload', methods=['POST'])
@jwt_required()
@require_admin
def upload_image():
    """上传图片"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 添加时间戳避免文件名冲突
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(admin_api.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                'message': '图片上传成功',
                'image_url': f"/uploads/{filename}"
            }), 200
        else:
            return jsonify({'error': '不支持的文件格式'}), 400
            
    except Exception as e:
        return jsonify({'error': f'图片上传失败: {str(e)}'}), 500

if __name__ == '__main__':
    admin_api.run(debug=True, host='0.0.0.0', port=5001) 
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Debug: Invalid token error: {error}")
    print(f"Debug: Error type: {type(error)}")
    print(f"Debug: Error message: {str(error)}")
    return jsonify({'error': f'无效的token: {str(error)}'}), 422

@jwt.unauthorized_loader
def unauthorized_callback(error):
    print(f"Debug: Unauthorized error: {error}")
    print(f"Debug: Error type: {type(error)}")
    print(f"Debug: Error message: {str(error)}")
    return jsonify({'error': f'缺少token: {str(error)}'}), 401

# 本地数据存储
users = {
    1: {
        'id': 1,
        'username': 'admin',
        'email': 'admin@feedmusic.com',
        'password_hash': bcrypt.generate_password_hash('admin123').decode('utf-8'),
        'created_at': '2024-01-01T00:00:00',
        'is_admin': True
    }
}

news_data = [
    {
        'id': 1,
        'title': 'Taylor Swift 发布新专辑《Midnights》',
        'description': '流行天后 Taylor Swift 发布了她的第十张录音室专辑《Midnights》，这张专辑融合了流行、电子和另类音乐元素，展现了她在音乐创作上的新突破。专辑中的每首歌都代表了午夜时分的不同情绪和思考。',
        'image_url': 'https://picsum.photos/400/300?random=1',
        'created_at': '2024-01-15T10:30:00',
        'updated_at': '2024-01-15T10:30:00',
        'author': 'admin',
        'author_id': 1
    },
    {
        'id': 2,
        'title': 'BTS 成员开始个人活动',
        'description': '韩国男团 BTS 的成员们开始各自的个人音乐活动，每位成员都展现了独特的音乐风格和个人魅力。从 RM 的深度思考到 Jungkook 的青春活力，粉丝们对此表示热烈支持。',
        'image_url': 'https://picsum.photos/400/300?random=2',
        'created_at': '2024-01-14T15:20:00',
        'updated_at': '2024-01-14T15:20:00',
        'author': 'admin',
        'author_id': 1
    },
    {
        'id': 3,
        'title': 'Billie Eilish 获得格莱美大奖',
        'description': 'Billie Eilish 在今年的格莱美颁奖典礼上获得了多个重要奖项，包括年度专辑和年度歌曲。她的音乐才华和独特风格得到了业界的广泛认可。',
        'image_url': 'https://picsum.photos/400/300?random=3',
        'created_at': '2024-01-13T20:15:00',
        'updated_at': '2024-01-13T20:15:00',
        'author': 'admin',
        'author_id': 1
    },
    {
        'id': 4,
        'title': 'Ed Sheeran 世界巡回演唱会启动',
        'description': '英国创作歌手 Ed Sheeran 宣布启动他的世界巡回演唱会，将在全球多个城市进行演出，为歌迷带来精彩的音乐盛宴。巡演将包括新专辑中的热门歌曲。',
        'image_url': 'https://picsum.photos/400/300?random=4',
        'created_at': '2024-01-12T14:45:00',
        'updated_at': '2024-01-12T14:45:00',
        'author': 'admin',
        'author_id': 1
    },
    {
        'id': 5,
        'title': 'Drake 新单曲打破流媒体记录',
        'description': '说唱歌手 Drake 的最新单曲在各大流媒体平台上创造了新的播放记录，再次证明了他作为音乐巨星的强大影响力。新歌融合了多种音乐风格。',
        'image_url': 'https://picsum.photos/400/300?random=5',
        'created_at': '2024-01-11T11:30:00',
        'updated_at': '2024-01-11T11:30:00',
        'author': 'admin',
        'author_id': 1
    },
    {
        'id': 6,
        'title': 'Adele 回归音乐舞台',
        'description': '英国歌手 Adele 在长时间的休息后正式回归音乐舞台，她的新作品展现了更加成熟和深情的音乐风格。新专辑将包含更多个人化的歌曲。',
        'image_url': 'https://picsum.photos/400/300?random=6',
        'created_at': '2024-01-10T16:20:00',
        'updated_at': '2024-01-10T16:20:00',
        'author': 'admin',
        'author_id': 1
    }
]

# 计数器
user_id_counter = 1
news_id_counter = 6

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_by_username(username):
    """根据用户名获取用户"""
    for user in users.values():
        if user['username'] == username:
            return user
    return None

def get_user_by_id(user_id):
    """根据用户ID获取用户"""
    return users.get(user_id)

def get_news_by_id(news_id):
    """根据新闻ID获取新闻"""
    for news in news_data:
        if news['id'] == news_id:
            return news
    return None

@app.route('/')
def index():
    """API状态检查"""
    return jsonify({
        'message': 'FeedMusic API is running',
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/test-token', methods=['GET'])
@jwt_required()
def test_token():
    """测试token是否有效"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        return jsonify({
            'message': 'Token is valid',
            'user_id': user_id,
            'username': user['username'] if user else None
        }), 200
    except Exception as e:
        return jsonify({'error': f'Token test failed: {str(e)}'}), 500

# 用户注册
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
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

# 用户登录
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
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
            access_token = create_access_token(identity=str(user['id']))  # 将用户ID转换为字符串
            
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

# 用户登出
@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    return jsonify({'message': '登出成功'}), 200

# 获取用户资料
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户资料"""
    try:
        user_id = int(get_jwt_identity())  # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user.get('is_admin', False),
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户资料失败: {str(e)}'}), 500

# 更新用户资料
@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户资料"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 更新邮箱
        if 'email' in data:
            new_email = data['email'].strip()
            if new_email and '@' in new_email:
                # 检查邮箱是否已被其他用户使用
                for other_user in users.values():
                    if other_user['id'] != user_id and other_user['email'] == new_email:
                        return jsonify({'error': '邮箱已被其他用户使用'}), 400
                user['email'] = new_email
        
        # 更新密码
        if 'password' in data:
            new_password = data['password'].strip()
            if new_password and len(new_password) >= 6:
                user['password_hash'] = bcrypt.generate_password_hash(new_password).decode('utf-8')
            elif new_password:
                return jsonify({'error': '密码长度不能少于6位'}), 400
        
        return jsonify({
            'message': '资料更新成功',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user.get('is_admin', False)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'更新资料失败: {str(e)}'}), 500

# 获取新闻列表
@app.route('/api/news', methods=['GET'])
def get_news():
    """获取新闻列表（公开 - 显示所有新闻）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
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
        return jsonify({'error': f'获取新闻失败: {str(e)}'}), 500

@app.route('/api/user/news', methods=['GET'])
@jwt_required()
def get_user_news():
    """获取当前用户的新闻列表"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        print(f"Debug: user_id from token = {user_id}")
        user = get_user_by_id(user_id)
        print(f"Debug: user found = {user is not None}")
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        # 过滤出当前用户的新闻
        user_news = [news for news in news_data if news['author_id'] == user_id]
        
        # 分页计算
        start = (page - 1) * per_page
        end = start + per_page
        
        # 按创建时间倒序排列
        sorted_news = sorted(user_news, key=lambda x: x['created_at'], reverse=True)
        paginated_news = sorted_news[start:end]
        
        total_pages = (len(user_news) + per_page - 1) // per_page
        
        return jsonify({
            'news': paginated_news,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_items': len(user_news)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户新闻失败: {str(e)}'}), 500

# 获取新闻详情
@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    """获取新闻详情"""
    try:
        news = get_news_by_id(news_id)
        
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        return jsonify({'news': news}), 200
        
    except Exception as e:
        return jsonify({'error': f'获取新闻详情失败: {str(e)}'}), 500

# 创建新闻
@app.route('/api/news', methods=['POST'])
@jwt_required()
def create_news():
    """创建新闻"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
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
@app.route('/api/news/<int:news_id>', methods=['PUT'])
@jwt_required()
def update_news(news_id):
    """更新新闻"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        news = get_news_by_id(news_id)
        
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        # 检查权限（只有作者或管理员可以编辑）
        if news['author_id'] != user['id'] and not user.get('is_admin', False):
            return jsonify({'error': '没有权限编辑此新闻'}), 403
        
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
@app.route('/api/news/<int:news_id>', methods=['DELETE'])
@jwt_required()
def delete_news(news_id):
    """删除新闻"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        news = get_news_by_id(news_id)
        
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        # 检查权限（只有作者或管理员可以删除）
        if news['author_id'] != user['id'] and not user.get('is_admin', False):
            return jsonify({'error': '没有权限删除此新闻'}), 403
        
        # 从列表中删除
        news_data[:] = [n for n in news_data if n['id'] != news_id]
        
        return jsonify({'message': '新闻删除成功'}), 200
        
    except Exception as e:
        return jsonify({'error': f'删除新闻失败: {str(e)}'}), 500

# 图片上传
@app.route('/api/upload', methods=['POST'])
@jwt_required()
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
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                'message': '图片上传成功',
                'image_url': f"/uploads/{filename}"
            }), 200
        else:
            return jsonify({'error': '不支持的文件格式'}), 400
            
    except Exception as e:
        return jsonify({'error': f'图片上传失败: {str(e)}'}), 500

# 提供上传的文件
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==================== 后台管理API ====================

# 获取所有用户（管理员专用）
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """获取所有用户（管理员专用）"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user or not user.get('is_admin', False):
            return jsonify({'error': '需要管理员权限'}), 403
        
        user_list = []
        for u in users.values():
            user_list.append({
                'id': u['id'],
                'username': u['username'],
                'email': u['email'],
                'is_admin': u.get('is_admin', False),
                'created_at': u['created_at']
            })
        
        return jsonify({'users': user_list}), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户列表失败: {str(e)}'}), 500

# 获取所有新闻（管理员专用）
@app.route('/api/admin/news', methods=['GET'])
@jwt_required()
def get_all_news_admin():
    """获取所有新闻（管理员专用）"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user or not user.get('is_admin', False):
            return jsonify({'error': '需要管理员权限'}), 403
        
        return jsonify({'news': news_data}), 200
        
    except Exception as e:
        return jsonify({'error': f'获取新闻列表失败: {str(e)}'}), 500

# 获取管理后台统计信息
@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """获取管理后台统计信息"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user or not user.get('is_admin', False):
            return jsonify({'error': '需要管理员权限'}), 403
        
        stats = {
            'total_users': len(users),
            'total_news': len(news_data),
            'admin_users': len([u for u in users.values() if u.get('is_admin', False)]),
            'recent_news': len([n for n in news_data if datetime.fromisoformat(n['created_at']) > datetime.utcnow() - timedelta(days=7)])
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500

# 管理员创建新闻
@app.route('/api/admin/news', methods=['POST'])
@jwt_required()
def admin_create_news():
    """管理员创建新闻"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user or not user.get('is_admin', False):
            return jsonify({'error': '需要管理员权限'}), 403
        
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

# 管理员更新新闻
@app.route('/api/admin/news/<int:news_id>', methods=['PUT'])
@jwt_required()
def admin_update_news(news_id):
    """管理员更新新闻"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user or not user.get('is_admin', False):
            return jsonify({'error': '需要管理员权限'}), 403
        
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

# 管理员删除新闻
@app.route('/api/admin/news/<int:news_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_news(news_id):
    """管理员删除新闻"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user or not user.get('is_admin', False):
            return jsonify({'error': '需要管理员权限'}), 403
        
        news = get_news_by_id(news_id)
        
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        # 从列表中删除
        news_data[:] = [n for n in news_data if n['id'] != news_id]
        
        return jsonify({'message': '新闻删除成功'}), 200
        
    except Exception as e:
        return jsonify({'error': f'删除新闻失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import uuid

# 导入数据库相关模块
from database import db, init_database
from models import User, News, Music

# 导入后台管理模块
from admin import create_app as create_admin_app

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

# 初始化数据库
db.init_app(app)

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Debug: Invalid token error: {error}")
    return jsonify({'error': f'无效的token: {str(error)}'}), 422

@jwt.unauthorized_loader
def unauthorized_callback(error):
    print(f"Debug: Unauthorized error: {error}")
    return jsonify({'error': f'缺少token: {str(error)}'}), 401

def allowed_file(filename):
    """检查文件类型是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': 'FeedMusic API with MySQL',
        'version': '2.0',
        'database': 'MySQL',
        'status': 'running',
        'admin_url': 'http://localhost:5000/admin/login'
    })

@app.route('/api/test-token', methods=['GET'])
@jwt_required()
def test_token():
    """测试token有效性"""
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'message': 'Token有效',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'is_admin': user['is_admin']
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': '用户名、邮箱和密码都是必需的'}), 400
        
        # 检查用户名是否已存在
        existing_user = User.get_by_username(username)
        if existing_user:
            return jsonify({'error': '用户名已存在'}), 409
        
        # 创建新用户
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = User.create(username, email, password_hash)
        
        # 获取创建的用户
        user = User.get_by_id(user_id)
        
        # 生成JWT token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'message': '注册成功',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user['is_admin']
            },
            'access_token': access_token
        }), 201
        
    except Exception as e:
        print(f"注册错误: {e}")
        return jsonify({'error': '注册失败'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': '用户名和密码都是必需的'}), 400
        
        # 查找用户
        user = User.get_by_username(username)
        if not user:
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 验证密码
        if not bcrypt.check_password_hash(user['password_hash'], password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 生成JWT token
        access_token = create_access_token(identity=user['id'])
        
        return jsonify({
            'message': '登录成功',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user['is_admin']
            },
            'access_token': access_token
        })
        
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({'error': '登录失败'}), 500

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    return jsonify({'message': '登出成功'})

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户资料"""
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'is_admin': user['is_admin'],
            'created_at': user['created_at']
        }
    })

@app.route('/api/news', methods=['GET'])
def get_news():
    """获取新闻列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取新闻数据
        result = News.get_all(page=page, per_page=per_page)
        
        return jsonify({
            'news': result['news'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
        
    except Exception as e:
        print(f"获取新闻错误: {e}")
        return jsonify({'error': '获取新闻失败'}), 500

@app.route('/api/user/news', methods=['GET'])
@jwt_required()
def get_user_news():
    """获取当前用户的新闻"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取用户的新闻数据
        result = News.get_all(page=page, per_page=per_page, author_id=current_user_id)
        
        return jsonify({
            'news': result['news'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
        
    except Exception as e:
        print(f"获取用户新闻错误: {e}")
        return jsonify({'error': '获取用户新闻失败'}), 500

@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    """获取新闻详情"""
    try:
        news = News.get_by_id(news_id)
        
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        return jsonify({'news': news})
        
    except Exception as e:
        print(f"获取新闻详情错误: {e}")
        return jsonify({'error': '获取新闻详情失败'}), 500

@app.route('/api/news', methods=['POST'])
@jwt_required()
def create_news():
    """创建新闻"""
    try:
        current_user_id = get_jwt_identity()
        user = User.get_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        title = data.get('title')
        description = data.get('description')
        image_url = data.get('image_url', '')
        
        if not title or not description:
            return jsonify({'error': '标题和描述都是必需的'}), 400
        
        # 创建新闻
        news_id = News.create(title, description, image_url, user['username'], current_user_id)
        
        # 获取创建的新闻
        news = News.get_by_id(news_id)
        
        return jsonify({
            'message': '新闻创建成功',
            'news': news
        }), 201
        
    except Exception as e:
        print(f"创建新闻错误: {e}")
        return jsonify({'error': '创建新闻失败'}), 500

@app.route('/api/news/<int:news_id>', methods=['PUT'])
@jwt_required()
def update_news(news_id):
    """更新新闻"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查新闻是否存在
        news = News.get_by_id(news_id)
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        # 检查权限（只有作者或管理员可以编辑）
        if news['author_id'] != current_user_id:
            user = User.get_by_id(current_user_id)
            if not user or not user['is_admin']:
                return jsonify({'error': '没有权限编辑此新闻'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 更新新闻
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'image_url' in data:
            update_data['image_url'] = data['image_url']
        
        if not update_data:
            return jsonify({'error': '没有提供更新数据'}), 400
        
        success = News.update(news_id, **update_data)
        
        if not success:
            return jsonify({'error': '更新失败'}), 500
        
        # 获取更新后的新闻
        updated_news = News.get_by_id(news_id)
        
        return jsonify({
            'message': '新闻更新成功',
            'news': updated_news
        })
        
    except Exception as e:
        print(f"更新新闻错误: {e}")
        return jsonify({'error': '更新新闻失败'}), 500

@app.route('/api/news/<int:news_id>', methods=['DELETE'])
@jwt_required()
def delete_news(news_id):
    """删除新闻"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查新闻是否存在
        news = News.get_by_id(news_id)
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        # 检查权限（只有作者或管理员可以删除）
        if news['author_id'] != current_user_id:
            user = User.get_by_id(current_user_id)
            if not user or not user['is_admin']:
                return jsonify({'error': '没有权限删除此新闻'}), 403
        
        # 删除新闻
        success = News.delete(news_id)
        
        if not success:
            return jsonify({'error': '删除失败'}), 500
        
        return jsonify({'message': '新闻删除成功'})
        
    except Exception as e:
        print(f"删除新闻错误: {e}")
        return jsonify({'error': '删除新闻失败'}), 500

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """上传图片"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # 保存文件
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # 返回文件URL
            file_url = f"/uploads/{unique_filename}"
            
            return jsonify({
                'message': '文件上传成功',
                'filename': unique_filename,
                'url': file_url
            })
        
        return jsonify({'error': '不支持的文件类型'}), 400
        
    except Exception as e:
        print(f"文件上传错误: {e}")
        return jsonify({'error': '文件上传失败'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 音乐相关API
@app.route('/api/music', methods=['GET'])
def get_music():
    """获取音乐列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        genre = request.args.get('genre')
        status = request.args.get('status')
        
        # 获取音乐数据
        result = Music.get_all(page=page, per_page=per_page, genre=genre, status=status)
        
        return jsonify({
            'music': result['music'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
        
    except Exception as e:
        print(f"获取音乐错误: {e}")
        return jsonify({'error': '获取音乐失败'}), 500

@app.route('/api/music/<int:music_id>', methods=['GET'])
def get_music_detail(music_id):
    """获取音乐详情"""
    try:
        music = Music.get_by_id(music_id)
        
        if not music:
            return jsonify({'error': '音乐不存在'}), 404
        
        return jsonify({'music': music})
        
    except Exception as e:
        print(f"获取音乐详情错误: {e}")
        return jsonify({'error': '获取音乐详情失败'}), 500

@app.route('/api/music', methods=['POST'])
@jwt_required()
def create_music():
    """创建音乐"""
    try:
        current_user_id = get_jwt_identity()
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        title = data.get('title')
        artist = data.get('artist')
        
        if not title or not artist:
            return jsonify({'error': '标题和艺术家都是必需的'}), 400
        
        # 创建音乐
        music_id = Music.create(
            title=title,
            artist=artist,
            genre=data.get('genre'),
            duration=data.get('duration'),
            bpm=data.get('bpm'),
            key_signature=data.get('key_signature'),
            time_signature=data.get('time_signature'),
            description=data.get('description'),
            file_path=data.get('file_path'),
            cover_image=data.get('cover_image'),
            is_public=data.get('is_public', True),
            created_by=current_user_id
        )
        
        # 获取创建的音乐
        music = Music.get_by_id(music_id)
        
        return jsonify({
            'message': '音乐创建成功',
            'music': music
        }), 201
        
    except Exception as e:
        print(f"创建音乐错误: {e}")
        return jsonify({'error': '创建音乐失败'}), 500

# 注册后台管理蓝图
admin_app = create_admin_app()
app.register_blueprint(admin_app, url_prefix='/admin')

if __name__ == '__main__':
    # 初始化数据库
    with app.app_context():
        try:
            init_database()
            print("✅ 数据库初始化成功")
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            # 继续运行，因为表可能已经存在
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
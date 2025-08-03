from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import timedelta

# 导入数据库相关模块
from database import db, init_database
from models import User, News, Music

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# 初始化扩展
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

# 初始化数据库
db.init_app(app)

@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': 'FeedMusic API with MySQL',
        'version': '2.0',
        'database': 'MySQL',
        'status': 'running'
    })

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
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
        
        # 生成JWT token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'message': '注册成功',
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
            'access_token': access_token
        })
        
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({'error': '登录失败'}), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    """获取新闻列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
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

@app.route('/api/music', methods=['GET'])
def get_music():
    """获取音乐列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        result = Music.get_all(page=page, per_page=per_page)
        
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
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import uuid
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# MySQL数据库配置
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3307))
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '123456')
app.config['MYSQL_DATABASE'] = os.environ.get('MYSQL_DATABASE', 'musiccreation')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE'],
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def init_database():
    """初始化数据库表"""
    # 首先连接到MySQL服务器（不指定数据库）
    try:
        connection = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        
        with connection.cursor() as cursor:
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DATABASE']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        connection.close()
    except Exception as e:
        print(f"创建数据库失败: {e}")
        return False
    
    # 然后连接到指定的数据库
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    real_name VARCHAR(100),
                    role ENUM('user', 'admin', 'viewer') DEFAULT 'user',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    INDEX idx_username (username),
                    INDEX idx_email (email),
                    INDEX idx_role (role)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 创建新闻表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    content LONGTEXT,
                    image_url VARCHAR(500),
                    author_id INT,
                    author_name VARCHAR(100),
                    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
                    view_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    published_at TIMESTAMP NULL,
                    INDEX idx_author_id (author_id),
                    INDEX idx_status (status),
                    INDEX idx_created_at (created_at),
                    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 检查是否已有管理员用户
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
            admin_count = cursor.fetchone()['count']
            
            if admin_count == 0:
                # 创建默认管理员用户
                admin_password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, real_name, role) 
                    VALUES (%s, %s, %s, %s, %s)
                """, ('admin', 'admin@feedmusic.com', admin_password_hash, '系统管理员', 'admin'))
                
                # 插入示例新闻数据
                cursor.execute("SELECT id FROM users WHERE username = 'admin'")
                admin_id = cursor.fetchone()['id']
                
                sample_news = [
                    ('Taylor Swift 发布新专辑《Midnights》', '流行天后 Taylor Swift 发布了她的第十张录音室专辑《Midnights》，这张专辑融合了流行、电子和另类音乐元素，展现了她在音乐创作上的新突破。专辑中的每首歌都代表了午夜时分的不同情绪和思考。', 'https://picsum.photos/400/300?random=1', admin_id, 'admin'),
                    ('BTS 成员开始个人活动', '韩国男团 BTS 的成员们开始各自的个人音乐活动，每位成员都展现了独特的音乐风格和个人魅力。从 RM 的深度思考到 Jungkook 的青春活力，粉丝们对此表示热烈支持。', 'https://picsum.photos/400/300?random=2', admin_id, 'admin'),
                    ('Billie Eilish 获得格莱美大奖', 'Billie Eilish 在今年的格莱美颁奖典礼上获得了多个重要奖项，包括年度专辑和年度歌曲。她的音乐才华和独特风格得到了业界的广泛认可。', 'https://picsum.photos/400/300?random=3', admin_id, 'admin'),
                    ('Ed Sheeran 世界巡回演唱会启动', '英国创作歌手 Ed Sheeran 宣布启动他的世界巡回演唱会，将在全球多个城市进行演出，为歌迷带来精彩的音乐盛宴。巡演将包括新专辑中的热门歌曲。', 'https://picsum.photos/400/300?random=4', admin_id, 'admin'),
                    ('Drake 新单曲打破流媒体记录', '说唱歌手 Drake 的最新单曲在各大流媒体平台上创造了新的播放记录，再次证明了他作为音乐巨星的强大影响力。新歌融合了多种音乐风格。', 'https://picsum.photos/400/300?random=5', admin_id, 'admin')
                ]
                
                for title, description, image_url, author_id, author_name in sample_news:
                    cursor.execute("""
                        INSERT INTO news (title, description, content, image_url, author_id, author_name, status, published_at) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (title, description, description, image_url, author_id, author_name, 'published', datetime.utcnow()))
            
            connection.commit()
            return True
            
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

# 初始化数据库
init_database()

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
    return jsonify({'error': f'缺少token: {str(error)}'}), 422

# 数据库操作函数
def get_user_by_username(username):
    """根据用户名获取用户"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND is_active = TRUE", (username,))
            return cursor.fetchone()
    except Exception as e:
        print(f"获取用户失败: {e}")
        return None
    finally:
        connection.close()

def get_user_by_id(user_id):
    """根据ID获取用户"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s AND is_active = TRUE", (user_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"获取用户失败: {e}")
        return None
    finally:
        connection.close()

def create_user(username, email, password_hash, real_name=None, role='user'):
    """创建新用户"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, real_name, role) 
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email, password_hash, real_name or username, role))
            connection.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"创建用户失败: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()

def check_username_exists(username):
    """检查用户名是否存在"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = %s", (username,))
            return cursor.fetchone()['count'] > 0
    except Exception as e:
        print(f"检查用户名失败: {e}")
        return False
    finally:
        connection.close()

def check_email_exists(email):
    """检查邮箱是否存在"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE email = %s", (email,))
            return cursor.fetchone()['count'] > 0
    except Exception as e:
        print(f"检查邮箱失败: {e}")
        return False
    finally:
        connection.close()

def update_user_login_time(user_id):
    """更新用户最后登录时间"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user_id,))
            connection.commit()
            return True
    except Exception as e:
        print(f"更新登录时间失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def get_all_users():
    """获取所有用户"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email, real_name, role, created_at, last_login FROM users WHERE is_active = TRUE ORDER BY created_at DESC")
            return cursor.fetchall()
    except Exception as e:
        print(f"获取用户列表失败: {e}")
        return []
    finally:
        connection.close()

def get_news_list(page=1, per_page=10, status='published'):
    """获取新闻列表"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT n.*, u.username as author_username 
                FROM news n 
                LEFT JOIN users u ON n.author_id = u.id 
                WHERE n.status = %s 
                ORDER BY n.created_at DESC 
                LIMIT %s OFFSET %s
            """, (status, per_page, offset))
            return cursor.fetchall()
    except Exception as e:
        print(f"获取新闻列表失败: {e}")
        return []
    finally:
        connection.close()

def get_news_by_id(news_id):
    """根据ID获取新闻"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT n.*, u.username as author_username 
                FROM news n 
                LEFT JOIN users u ON n.author_id = u.id 
                WHERE n.id = %s
            """, (news_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"获取新闻失败: {e}")
        return None
    finally:
        connection.close()

def create_news_in_db(title, description, content, image_url, author_id, author_name):
    """创建新闻"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO news (title, description, content, image_url, author_id, author_name, status, published_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, description, content, image_url, author_id, author_name, 'published', datetime.utcnow()))
            connection.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"创建新闻失败: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()

def update_news_in_db(news_id, title, description, content, image_url):
    """更新新闻"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE news 
                SET title = %s, description = %s, content = %s, image_url = %s, updated_at = NOW() 
                WHERE id = %s
            """, (title, description, content, image_url, news_id))
            connection.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"更新新闻失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def delete_news(news_id):
    """删除新闻"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM news WHERE id = %s", (news_id,))
            connection.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"删除新闻失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def get_news_count(status='published'):
    """获取新闻总数"""
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM news WHERE status = %s", (status,))
            return cursor.fetchone()['count']
    except Exception as e:
        print(f"获取新闻数量失败: {e}")
        return 0
    finally:
        connection.close()

def allowed_file(filename):
    """检查文件类型是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """API状态检查"""
    return jsonify({
        'message': 'FeedMusic API is running',
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat()
    })

# 管理后台页面路由
@app.route('/admin')
def admin_redirect():
    """管理后台重定向"""
    return redirect('/admin/login')

@app.route('/admin/login')
def admin_login_page():
    """管理后台登录页面"""
    return render_template('admin/simple_login.html')

@app.route('/admin/register')
def admin_register_page():
    """管理后台注册页面"""
    return render_template('admin/register.html')

@app.route('/admin/dashboard')
def admin_dashboard_page():
    """管理后台首页"""
    return render_template('admin/simple_dashboard.html')

@app.route('/admin/users')
def admin_users_page():
    """用户管理页面"""
    return render_template('admin/simple_users.html')

@app.route('/admin/news')
def admin_news_page():
    """新闻管理页面"""
    return render_template('admin/simple_news.html')

@app.route('/admin/news/create')
def admin_create_news_page():
    """创建新闻页面"""
    return render_template('admin/create_news.html')

@app.route('/admin/news/edit/<int:news_id>')
def admin_edit_news_page(news_id):
    """编辑新闻页面"""
    return render_template('admin/edit_news.html')

@app.route('/admin/logout')
def admin_logout_page():
    """管理后台登出页面"""
    return render_template('admin/logout.html')

# 管理后台登录API
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理后台登录"""
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
            # 检查是否是管理员
            if user['role'] != 'admin':
                return jsonify({'error': '只有管理员才能登录后台'}), 403
            
            # 创建JWT token
            access_token = create_access_token(identity=str(user['id']))
            
            # 更新最后登录时间
            update_user_login_time(user['id'])
            
            return jsonify({
                'message': '登录成功',
                'access_token': access_token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
            }), 200
        else:
            return jsonify({'error': '用户名或密码错误'}), 401
            
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

# 管理后台注册API
@app.route('/api/admin/register', methods=['POST'])
def admin_register():
    """管理后台注册"""
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
        if check_username_exists(username):
            return jsonify({'error': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if check_email_exists(email):
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 创建新管理员用户
        user_id = create_user(username, email, bcrypt.generate_password_hash(password).decode('utf-8'), role='admin')
        
        if not user_id:
            return jsonify({'error': '注册失败'}), 500
        
        new_user = get_user_by_id(user_id)
        
        return jsonify({
            'message': '注册成功',
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'email': new_user['email'],
                'role': new_user['role']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

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
        if check_username_exists(username):
            return jsonify({'error': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if check_email_exists(email):
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 创建新用户
        user_id = create_user(username, email, bcrypt.generate_password_hash(password).decode('utf-8'))
        
        if not user_id:
            return jsonify({'error': '注册失败'}), 500
        
        new_user = get_user_by_id(user_id)
        
        return jsonify({
            'message': '注册成功',
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'email': new_user['email'],
                'is_admin': new_user['role'] == 'admin'
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
            
            # 更新最后登录时间
            update_user_login_time(user['id'])
            
            return jsonify({
                'message': '登录成功',
                'access_token': access_token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user['role'] == 'admin'
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
                'is_admin': user['role'] == 'admin',
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
                if check_email_exists(new_email) and new_email != user['email']:
                    return jsonify({'error': '邮箱已被其他用户使用'}), 400
                user['email'] = new_email
        
        # 更新密码
        if 'password' in data:
            new_password = data['password'].strip()
            if new_password and len(new_password) >= 6:
                user['password_hash'] = bcrypt.generate_password_hash(new_password).decode('utf-8')
            elif new_password:
                return jsonify({'error': '密码长度不能少于6位'}), 400
        
        # 更新其他字段
        if 'real_name' in data:
            user['real_name'] = data['real_name'].strip()
        
        # 更新数据库
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET email = %s, password_hash = %s, real_name = %s, updated_at = NOW() 
                    WHERE id = %s
                """, (user['email'], user['password_hash'], user['real_name'], user_id))
                connection.commit()
            return jsonify({
                'message': '资料更新成功',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user['role'] == 'admin'
                }
            }), 200
        except Exception as e:
            print(f"更新用户资料失败: {e}")
            connection.rollback()
            return jsonify({'error': f'更新资料失败: {str(e)}'}), 500
        finally:
            connection.close()
        
    except Exception as e:
        return jsonify({'error': f'更新资料失败: {str(e)}'}), 500

# 获取新闻列表
@app.route('/api/news', methods=['GET'])
def get_news():
    """获取新闻列表（公开 - 显示所有新闻）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        # 获取新闻列表
        news_list = get_news_list(page, per_page, 'published')
        total_count = get_news_count('published')
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return jsonify({
            'news': news_list,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_items': total_count
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
        
        # 获取当前用户的新闻
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': '数据库连接失败'}), 500
        
        try:
            with connection.cursor() as cursor:
                offset = (page - 1) * per_page
                cursor.execute("""
                    SELECT n.*, u.username as author_username 
                    FROM news n 
                    LEFT JOIN users u ON n.author_id = u.id 
                    WHERE n.author_id = %s 
                    ORDER BY n.created_at DESC 
                    LIMIT %s OFFSET %s
                """, (user_id, per_page, offset))
                user_news = cursor.fetchall()
                
                # 获取总数
                cursor.execute("SELECT COUNT(*) as count FROM news WHERE author_id = %s", (user_id,))
                total_count = cursor.fetchone()['count']
                
                total_pages = (total_count + per_page - 1) // per_page
                
                return jsonify({
                    'news': user_news,
                    'pagination': {
                        'current_page': page,
                        'per_page': per_page,
                        'total_pages': total_pages,
                        'total_items': total_count
                    }
                }), 200
        finally:
            connection.close()
        
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
        news_id = create_news_in_db(title, description, description, image_url, user_id, user['username'])
        
        if not news_id:
            return jsonify({'error': '创建新闻失败'}), 500
        
        new_news = get_news_by_id(news_id)
        
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
        if news['author_id'] != user['id'] and user['role'] != 'admin':
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
        updated = update_news_in_db(news_id, title, description, description, image_url)
        
        if not updated:
            return jsonify({'error': '更新新闻失败'}), 500
        
        updated_news = get_news_by_id(news_id)
        
        return jsonify({
            'message': '新闻更新成功',
            'news': updated_news
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
        if news['author_id'] != user['id'] and user['role'] != 'admin':
            return jsonify({'error': '没有权限删除此新闻'}), 403
        
        # 从列表中删除
        deleted = delete_news_in_db(news_id)
        
        if not deleted:
            return jsonify({'error': '删除新闻失败'}), 500
        
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
def get_all_users_admin():
    """获取所有用户（管理员专用）"""
    try:
        user_id = int(get_jwt_identity()) # 将字符串ID转换为整数
        user = get_user_by_id(user_id)
        
        if not user or user['role'] != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        
        user_list = []
        for u in get_all_users():
            user_list.append({
                'id': u['id'],
                'username': u['username'],
                'email': u['email'],
                'is_admin': u['role'] == 'admin',
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
        
        if not user or user['role'] != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取新闻列表和总数
        news_list = get_news_list(page, per_page, 'published')
        total_count = get_news_count('published')
        
        # 计算分页信息
        total_pages = (total_count + per_page - 1) // per_page
        
        return jsonify({
            'news': news_list,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_count': total_count
            }
        }), 200
        
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
        
        if not user or user['role'] != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        
        stats = {
            'total_users': len(get_all_users()),
            'total_news': get_news_count(),
            'admin_users': len([u for u in get_all_users() if u['role'] == 'admin']),
            'recent_news': get_news_count()  # 简化统计，实际应该查询最近7天的新闻
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
        
        if not user or user['role'] != 'admin':
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
        news_id = create_news_in_db(title, description, description, image_url, user_id, user['username'])
        
        if not news_id:
            return jsonify({'error': '创建新闻失败'}), 500
        
        new_news = get_news_by_id(news_id)
        
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
        
        if not user or user['role'] != 'admin':
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
        updated = update_news_in_db(news_id, title, description, description, image_url)
        
        if not updated:
            return jsonify({'error': '更新新闻失败'}), 500
        
        updated_news = get_news_by_id(news_id)
        
        return jsonify({
            'message': '新闻更新成功',
            'news': updated_news
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
        
        if not user or user['role'] != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        
        news = get_news_by_id(news_id)
        
        if not news:
            return jsonify({'error': '新闻不存在'}), 404
        
        # 从列表中删除
        deleted = delete_news_in_db(news_id)
        
        if not deleted:
            return jsonify({'error': '删除新闻失败'}), 500
        
        return jsonify({'message': '新闻删除成功'}), 200
        
    except Exception as e:
        return jsonify({'error': f'删除新闻失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 

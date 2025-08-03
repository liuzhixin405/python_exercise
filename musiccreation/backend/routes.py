from flask import request, jsonify, send_from_directory
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
from app import app, db, User, News

bcrypt = Bcrypt(app)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=password_hash
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '缺少用户名或密码'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    else:
        return jsonify({'error': '用户名或密码错误'}), 401

@app.route('/api/news', methods=['GET'])
def get_news():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    
    news = News.query.order_by(News.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    news_list = []
    for item in news.items:
        news_list.append({
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'image_url': item.image_url,
            'created_at': item.created_at.isoformat(),
            'author': item.author.username
        })
    
    return jsonify({
        'news': news_list,
        'total': news.total,
        'pages': news.pages,
        'current_page': page
    }), 200

@app.route('/api/news', methods=['POST'])
@jwt_required()
def create_news():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('description'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    new_news = News(
        title=data['title'],
        description=data['description'],
        image_url=data.get('image_url', ''),
        author_id=user.id
    )
    
    db.session.add(new_news)
    db.session.commit()
    
    return jsonify({
        'message': '新闻创建成功',
        'news': {
            'id': new_news.id,
            'title': new_news.title,
            'description': new_news.description,
            'image_url': new_news.image_url,
            'created_at': new_news.created_at.isoformat(),
            'author': user.username
        }
    }), 201

@app.route('/api/news/<int:news_id>', methods=['PUT'])
@jwt_required()
def update_news(news_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    news = News.query.get_or_404(news_id)
    
    if news.author_id != user.id:
        return jsonify({'error': '无权限编辑此新闻'}), 403
    
    data = request.get_json()
    
    if data.get('title'):
        news.title = data['title']
    if data.get('description'):
        news.description = data['description']
    if data.get('image_url'):
        news.image_url = data['image_url']
    
    news.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '新闻更新成功'}), 200

@app.route('/api/news/<int:news_id>', methods=['DELETE'])
@jwt_required()
def delete_news(news_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    news = News.query.get_or_404(news_id)
    
    if news.author_id != user.id:
        return jsonify({'error': '无权限删除此新闻'}), 403
    
    db.session.delete(news)
    db.session.commit()
    
    return jsonify({'message': '新闻删除成功'}), 200

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        file_url = f"/uploads/{unique_filename}"
        return jsonify({'image_url': file_url}), 200
    
    return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    }), 200 
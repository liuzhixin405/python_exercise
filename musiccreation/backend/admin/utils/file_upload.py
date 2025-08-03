"""
文件上传工具函数
"""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, folder: str = None) -> str:
    """保存上传的文件"""
    if folder is None:
        folder = current_app.config['UPLOAD_FOLDER']
    
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 添加时间戳避免文件名冲突
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # 确保目录存在
        os.makedirs(folder, exist_ok=True)
        
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        
        return f"/uploads/{filename}"
    
    return None

def delete_file(filename: str) -> bool:
    """删除文件"""
    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception:
        pass
    return False 
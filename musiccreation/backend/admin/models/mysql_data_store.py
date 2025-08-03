"""
MySQL数据存储模型 - 完全基于数据库的数据存储
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from database import db

class MySQLDataStore:
    """MySQL数据存储类"""
    
    def __init__(self):
        # 基础URL配置
        self.base_url = "http://localhost:5000"
    
    def _normalize_image_url(self, image_url: str) -> str:
        """标准化图片URL，添加域名前缀"""
        if not image_url:
            return ""
        
        # 如果已经是完整的URL（包含http或https），直接返回
        if image_url.startswith(('http://', 'https://')):
            return image_url
        
        # 如果是相对路径，添加域名前缀
        if image_url.startswith('/'):
            return f"{self.base_url}{image_url}"
        
        # 如果只是文件名，添加完整路径
        return f"{self.base_url}/uploads/{image_url}"
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        query = "SELECT * FROM users WHERE username = %s"
        result = db.execute_query(query, (username,))
        return result[0] if result else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        query = "SELECT * FROM users WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def create_user(self, username: str, email: str, password_hash: str, is_admin: bool = False) -> Dict[str, Any]:
        """创建新用户"""
        query = """
        INSERT INTO users (username, email, password_hash, is_admin) 
        VALUES (%s, %s, %s, %s)
        """
        user_id = db.execute_insert(query, (username, email, password_hash, is_admin))
        
        # 返回创建的用户
        return self.get_user_by_id(user_id)
    
    def get_news_by_id(self, news_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取新闻"""
        query = """
        SELECT n.*, u.username as author_name 
        FROM news n 
        LEFT JOIN users u ON n.author_id = u.id 
        WHERE n.id = %s
        """
        result = db.execute_query(query, (news_id,))
        if result:
            news = result[0]
            # 标准化图片URL
            news['image_url'] = self._normalize_image_url(news['image_url'])
            return news
        return None
    
    def create_news(self, title: str, description: str, image_url: str, author: str) -> Dict[str, Any]:
        """创建新闻"""
        # 对于后台用户，我们直接使用作者名，不关联前台用户ID
        query = """
        INSERT INTO news (title, description, image_url, author) 
        VALUES (%s, %s, %s, %s)
        """
        news_id = db.execute_insert(query, (title, description, image_url, author))
        
        # 返回创建的新闻
        return self.get_news_by_id(news_id)
    
    def update_news(self, news_id: int, title: str, description: str, image_url: str = None) -> Optional[Dict[str, Any]]:
        """更新新闻"""
        # 构建更新字段
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        
        if image_url is not None:
            update_fields.append("image_url = %s")
            params.append(image_url)
        
        if not update_fields:
            return self.get_news_by_id(news_id)
        
        # 添加更新时间
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(news_id)
        
        query = f"UPDATE news SET {', '.join(update_fields)} WHERE id = %s"
        db.execute_update(query, params)
        
        return self.get_news_by_id(news_id)
    
    def delete_news(self, news_id: int) -> bool:
        """删除新闻"""
        query = "DELETE FROM news WHERE id = %s"
        return db.execute_update(query, (news_id,)) > 0
    
    def get_news_paginated(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """获取分页新闻"""
        offset = (page - 1) * per_page
        
        # 获取总数
        count_query = "SELECT COUNT(*) as total FROM news"
        total_result = db.execute_query(count_query)
        total = total_result[0]['total']
        
        # 获取新闻列表
        query = """
        SELECT n.*, u.username as author_name 
        FROM news n 
        LEFT JOIN users u ON n.author_id = u.id 
        ORDER BY n.created_at DESC 
        LIMIT %s OFFSET %s
        """
        news_list = db.execute_query(query, (per_page, offset))
        
        # 标准化图片URL
        for news in news_list:
            news['image_url'] = self._normalize_image_url(news['image_url'])
        
        return {
            'news': news_list,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        queries = {
            'total_users': "SELECT COUNT(*) as count FROM users",
            'total_news': "SELECT COUNT(*) as count FROM news",
            'admin_users': "SELECT COUNT(*) as count FROM users WHERE is_admin = TRUE"
        }
        
        stats = {}
        for key, query in queries.items():
            result = db.execute_query(query)
            stats[key] = result[0]['count']
        
        return stats
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        query = "SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC"
        return db.execute_query(query)
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        query = "DELETE FROM users WHERE id = %s"
        return db.execute_update(query, (user_id,)) > 0
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """更新用户信息"""
        if not kwargs:
            return False
        
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE users SET {set_clause} WHERE id = %s"
        params = list(kwargs.values()) + [user_id]
        
        return db.execute_update(query, params) > 0

# 创建全局实例
mysql_data_store = MySQLDataStore() 
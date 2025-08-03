"""
数据模型类 - 用于操作MySQL数据库
"""

from database import db
from typing import List, Dict, Optional, Any

class User:
    """用户模型"""
    
    @staticmethod
    def get_by_username(username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        query = "SELECT * FROM users WHERE username = %s"
        result = db.execute_query(query, (username,))
        return result[0] if result else None
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        query = "SELECT * FROM users WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def create(username: str, email: str, password_hash: str, is_admin: bool = False) -> int:
        """创建新用户"""
        query = """
        INSERT INTO users (username, email, password_hash, is_admin) 
        VALUES (%s, %s, %s, %s)
        """
        return db.execute_insert(query, (username, email, password_hash, is_admin))
    
    @staticmethod
    def get_all(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """获取所有用户（分页）"""
        offset = (page - 1) * per_page
        
        # 获取总数
        count_query = "SELECT COUNT(*) as total FROM users"
        total_result = db.execute_query(count_query)
        total = total_result[0]['total']
        
        # 获取用户列表
        query = "SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s"
        users = db.execute_query(query, (per_page, offset))
        
        return {
            'users': users,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }

class News:
    """新闻模型"""
    
    @staticmethod
    def get_by_id(news_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取新闻"""
        query = """
        SELECT n.*, u.username as author_name 
        FROM news n 
        LEFT JOIN users u ON n.author_id = u.id 
        WHERE n.id = %s
        """
        result = db.execute_query(query, (news_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_all(page: int = 1, per_page: int = 10, author_id: int = None) -> Dict[str, Any]:
        """获取所有新闻（分页）"""
        offset = (page - 1) * per_page
        
        # 构建查询条件
        where_clause = ""
        params = []
        
        if author_id:
            where_clause = "WHERE n.author_id = %s"
            params.append(author_id)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM news n {where_clause}"
        total_result = db.execute_query(count_query, params)
        total = total_result[0]['total']
        
        # 获取新闻列表
        query = f"""
        SELECT n.*, u.username as author_name 
        FROM news n 
        LEFT JOIN users u ON n.author_id = u.id 
        {where_clause}
        ORDER BY n.created_at DESC 
        LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        news_list = db.execute_query(query, params)
        
        return {
            'news': news_list,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def create(title: str, description: str, image_url: str, author: str, author_id: int) -> int:
        """创建新闻"""
        query = """
        INSERT INTO news (title, description, image_url, author, author_id) 
        VALUES (%s, %s, %s, %s, %s)
        """
        return db.execute_insert(query, (title, description, image_url, author, author_id))
    
    @staticmethod
    def update(news_id: int, **kwargs) -> bool:
        """更新新闻"""
        if not kwargs:
            return False
        
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE news SET {set_clause} WHERE id = %s"
        params = list(kwargs.values()) + [news_id]
        
        return db.execute_update(query, params) > 0
    
    @staticmethod
    def delete(news_id: int) -> bool:
        """删除新闻"""
        query = "DELETE FROM news WHERE id = %s"
        return db.execute_update(query, (news_id,)) > 0
    
    @staticmethod
    def get_stats() -> Dict[str, int]:
        """获取新闻统计信息"""
        queries = {
            'total_news': "SELECT COUNT(*) as count FROM news",
            'total_users': "SELECT COUNT(*) as count FROM users",
            'admin_users': "SELECT COUNT(*) as count FROM users WHERE is_admin = TRUE"
        }
        
        stats = {}
        for key, query in queries.items():
            result = db.execute_query(query)
            stats[key] = result[0]['count']
        
        return stats

class Music:
    """音乐模型"""
    
    @staticmethod
    def get_by_id(music_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取音乐"""
        query = "SELECT * FROM music WHERE id = %s"
        result = db.execute_query(query, (music_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_all(page: int = 1, per_page: int = 10, genre: str = None, status: str = None) -> Dict[str, Any]:
        """获取所有音乐（分页）"""
        offset = (page - 1) * per_page
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if genre:
            where_conditions.append("genre = %s")
            params.append(genre)
        
        if status:
            where_conditions.append("status = %s")
            params.append(status)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM music {where_clause}"
        total_result = db.execute_query(count_query, params)
        total = total_result[0]['total']
        
        # 获取音乐列表
        query = f"""
        SELECT * FROM music 
        {where_clause}
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        music_list = db.execute_query(query, params)
        
        return {
            'music': music_list,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def create(title: str, artist: str, genre: str = None, duration: int = None, 
               bpm: int = None, key_signature: str = None, time_signature: str = None,
               description: str = None, file_path: str = None, cover_image: str = None,
               is_public: bool = True, created_by: int = None) -> int:
        """创建音乐"""
        query = """
        INSERT INTO music (title, artist, genre, duration, bpm, key_signature, time_signature, 
                          description, file_path, cover_image, is_public, created_by) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return db.execute_insert(query, (title, artist, genre, duration, bpm, key_signature, 
                                        time_signature, description, file_path, cover_image, 
                                        is_public, created_by))
    
    @staticmethod
    def update(music_id: int, **kwargs) -> bool:
        """更新音乐"""
        if not kwargs:
            return False
        
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE music SET {set_clause} WHERE id = %s"
        params = list(kwargs.values()) + [music_id]
        
        return db.execute_update(query, params) > 0
    
    @staticmethod
    def delete(music_id: int) -> bool:
        """删除音乐"""
        query = "DELETE FROM music WHERE id = %s"
        return db.execute_update(query, (music_id,)) > 0 
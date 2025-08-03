"""
数据存储模型 - 管理内存中的数据
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

class DataStore:
    """内存数据存储类"""
    
    def __init__(self):
        # 基础URL配置
        self.base_url = "http://localhost:5001"
        
        # 用户数据
        self.users: Dict[int, Dict[str, Any]] = {
            1: {
                'id': 1,
                'username': 'admin',
                'email': 'admin@feedmusic.com',
                'password_hash': None,  # 将在初始化时设置
                'created_at': '2024-01-01T00:00:00',
                'is_admin': True
            }
        }
        
        # 新闻数据
        self.news_data: List[Dict[str, Any]] = [
            {
                'id': 1,
                'title': '音乐新闻管理系统上线',
                'description': '欢迎使用音乐新闻管理系统，这是一个功能完整的管理平台。',
                'image_url': 'https://via.placeholder.com/300x200?text=Music+News',
                'author': 'admin',
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00'
            },
            {
                'id': 2,
                'title': '系统功能介绍',
                'description': '本系统支持用户管理、新闻管理、图片上传等功能。',
                'image_url': 'https://via.placeholder.com/300x200?text=Features',
                'author': 'admin',
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00'
            }
        ]
        
        # ID计数器
        self.user_id_counter = 1
        self.news_id_counter = 2
    
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
        for user in self.users.values():
            if user['username'] == username:
                return user
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        return self.users.get(user_id)
    
    def create_user(self, username: str, email: str, password_hash: str, is_admin: bool = False) -> Dict[str, Any]:
        """创建新用户"""
        self.user_id_counter += 1
        new_user = {
            'id': self.user_id_counter,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'is_admin': is_admin,
            'created_at': datetime.utcnow().isoformat()
        }
        self.users[self.user_id_counter] = new_user
        return new_user
    
    def get_news_by_id(self, news_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取新闻"""
        for news in self.news_data:
            if news['id'] == news_id:
                # 返回时标准化图片URL
                news_copy = news.copy()
                news_copy['image_url'] = self._normalize_image_url(news['image_url'])
                return news_copy
        return None
    
    def create_news(self, title: str, description: str, image_url: str, author: str) -> Dict[str, Any]:
        """创建新闻"""
        self.news_id_counter += 1
        
        # 标准化图片URL
        normalized_image_url = self._normalize_image_url(image_url)
        
        new_news = {
            'id': self.news_id_counter,
            'title': title,
            'description': description,
            'image_url': normalized_image_url,
            'author': author,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        self.news_data.append(new_news)
        return new_news
    
    def update_news(self, news_id: int, title: str, description: str, image_url: str = None) -> Optional[Dict[str, Any]]:
        """更新新闻"""
        news = None
        for n in self.news_data:
            if n['id'] == news_id:
                news = n
                break
        
        if news:
            news['title'] = title
            news['description'] = description
            if image_url:
                news['image_url'] = self._normalize_image_url(image_url)
            news['updated_at'] = datetime.utcnow().isoformat()
            
            # 返回时标准化图片URL
            news_copy = news.copy()
            news_copy['image_url'] = self._normalize_image_url(news['image_url'])
            return news_copy
        return None
    
    def delete_news(self, news_id: int) -> bool:
        """删除新闻"""
        for i, news in enumerate(self.news_data):
            if news['id'] == news_id:
                del self.news_data[i]
                return True
        return False
    
    def get_news_paginated(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """获取分页新闻列表"""
        start = (page - 1) * per_page
        end = start + per_page
        
        # 按创建时间倒序排列
        sorted_news = sorted(self.news_data, key=lambda x: x['created_at'], reverse=True)
        paginated_news = sorted_news[start:end]
        
        # 标准化所有新闻的图片URL
        normalized_news = []
        for news in paginated_news:
            news_copy = news.copy()
            news_copy['image_url'] = self._normalize_image_url(news['image_url'])
            normalized_news.append(news_copy)
        
        total_pages = (len(self.news_data) + per_page - 1) // per_page
        
        return {
            'news': normalized_news,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': len(self.news_data),
                'per_page': per_page
            }
        }
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计数据"""
        from datetime import timedelta
        
        recent_news = len([
            n for n in self.news_data 
            if datetime.fromisoformat(n['created_at']) > datetime.utcnow() - timedelta(days=7)
        ])
        
        return {
            'total_users': len(self.users),
            'total_news': len(self.news_data),
            'admin_users': len([u for u in self.users.values() if u.get('is_admin', False)]),
            'recent_news': recent_news
        }

# 全局数据存储实例
data_store = DataStore() 
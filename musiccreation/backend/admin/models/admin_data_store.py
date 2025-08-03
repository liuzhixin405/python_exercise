"""
后台用户数据存储模型 - 专门管理后台用户
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from database import db

class AdminDataStore:
    """后台用户数据存储类"""
    
    def __init__(self):
        pass
    
    def get_admin_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取后台用户"""
        query = "SELECT * FROM admin_users WHERE username = %s AND is_active = TRUE"
        result = db.execute_query(query, (username,))
        return result[0] if result else None
    
    def get_admin_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取后台用户"""
        query = "SELECT * FROM admin_users WHERE id = %s AND is_active = TRUE"
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_admin_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取后台用户"""
        query = "SELECT * FROM admin_users WHERE email = %s AND is_active = TRUE"
        result = db.execute_query(query, (email,))
        return result[0] if result else None
    
    def create_admin_user(self, username: str, email: str, password_hash: str, 
                         real_name: str = None, role: str = 'viewer') -> Dict[str, Any]:
        """创建后台用户"""
        query = """
        INSERT INTO admin_users (username, email, password_hash, real_name, role) 
        VALUES (%s, %s, %s, %s, %s)
        """
        user_id = db.execute_insert(query, (username, email, password_hash, real_name, role))
        
        # 返回创建的用户
        return self.get_admin_user_by_id(user_id)
    
    def update_admin_user(self, user_id: int, **kwargs) -> bool:
        """更新后台用户信息"""
        if not kwargs:
            return False
        
        # 构建更新字段
        update_fields = []
        params = []
        
        allowed_fields = ['username', 'email', 'password_hash', 'real_name', 'role', 'is_active']
        for key, value in kwargs.items():
            if key in allowed_fields:
                update_fields.append(f"{key} = %s")
                params.append(value)
        
        if not update_fields:
            return False
        
        # 添加更新时间
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        query = f"UPDATE admin_users SET {', '.join(update_fields)} WHERE id = %s"
        return db.execute_update(query, params) > 0
    
    def update_login_info(self, user_id: int) -> bool:
        """更新登录信息"""
        query = """
        UPDATE admin_users 
        SET last_login = CURRENT_TIMESTAMP, login_count = login_count + 1 
        WHERE id = %s
        """
        return db.execute_update(query, (user_id,)) > 0
    
    def delete_admin_user(self, user_id: int) -> bool:
        """删除后台用户（软删除）"""
        query = "UPDATE admin_users SET is_active = FALSE WHERE id = %s"
        return db.execute_update(query, (user_id,)) > 0
    
    def get_all_admin_users(self, page: int = 1, per_page: int = 20, 
                           role: Optional[str] = None, is_active: Optional[bool] = None) -> Dict[str, Any]:
        """获取所有后台用户（分页）"""
        offset = (page - 1) * per_page
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if role:
            where_conditions.append("role = %s")
            params.append(role)
        
        if is_active is not None:
            where_conditions.append("is_active = %s")
            params.append(is_active)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM admin_users {where_clause}"
        total_result = db.execute_query(count_query, params)
        total = total_result[0]['total']
        
        # 获取用户列表
        query = f"""
        SELECT id, username, email, real_name, role, is_active, last_login, login_count, created_at, updated_at
        FROM admin_users 
        {where_clause}
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        user_list = db.execute_query(query, params + [per_page, offset])
        
        return {
            'users': user_list,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def get_admin_stats(self) -> Dict[str, int]:
        """获取后台用户统计信息"""
        queries = {
            'total_users': "SELECT COUNT(*) as count FROM admin_users WHERE is_active = TRUE",
            'admin_users': "SELECT COUNT(*) as count FROM admin_users WHERE role = 'admin' AND is_active = TRUE",
            'editor_users': "SELECT COUNT(*) as count FROM admin_users WHERE role = 'editor' AND is_active = TRUE",
            'viewer_users': "SELECT COUNT(*) as count FROM admin_users WHERE role = 'viewer' AND is_active = TRUE",
            'active_users': "SELECT COUNT(*) as count FROM admin_users WHERE is_active = TRUE",
            'inactive_users': "SELECT COUNT(*) as count FROM admin_users WHERE is_active = FALSE"
        }
        
        stats = {}
        for key, query in queries.items():
            result = db.execute_query(query)
            stats[key] = result[0]['count']
        
        return stats
    
    def check_username_exists(self, username: str, exclude_id: int = None) -> bool:
        """检查用户名是否已存在"""
        if exclude_id:
            query = "SELECT COUNT(*) as count FROM admin_users WHERE username = %s AND id != %s"
            result = db.execute_query(query, (username, exclude_id))
        else:
            query = "SELECT COUNT(*) as count FROM admin_users WHERE username = %s"
            result = db.execute_query(query, (username,))
        
        return result[0]['count'] > 0
    
    def check_email_exists(self, email: str, exclude_id: int = None) -> bool:
        """检查邮箱是否已存在"""
        if exclude_id:
            query = "SELECT COUNT(*) as count FROM admin_users WHERE email = %s AND id != %s"
            result = db.execute_query(query, (email, exclude_id))
        else:
            query = "SELECT COUNT(*) as count FROM admin_users WHERE email = %s"
            result = db.execute_query(query, (email,))
        
        return result[0]['count'] > 0

# 创建全局实例
admin_data_store = AdminDataStore() 
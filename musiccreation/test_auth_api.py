#!/usr/bin/env python3
"""
测试用户认证API的脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:5000"

def test_register():
    """测试用户注册"""
    print("=== 测试用户注册 ===")
    
    # 测试数据
    test_users = [
        {
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "password123"
        },
        {
            "username": "testuser2", 
            "email": "test2@example.com",
            "password": "password456"
        }
    ]
    
    for user_data in test_users:
        try:
            response = requests.post(f"{BASE_URL}/api/register", json=user_data)
            print(f"注册用户 {user_data['username']}:")
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.json()}")
            print()
        except Exception as e:
            print(f"注册失败: {e}")
            print()

def test_login():
    """测试用户登录"""
    print("=== 测试用户登录 ===")
    
    # 测试登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"管理员登录:")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            return token
        print()
    except Exception as e:
        print(f"登录失败: {e}")
        print()
    
    return None

def test_news_api(token=None):
    """测试新闻API"""
    print("=== 测试新闻API ===")
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(f"{BASE_URL}/api/news", headers=headers)
        print(f"获取新闻列表:")
        print(f"  状态码: {response.status_code}")
        data = response.json()
        print(f"  新闻数量: {len(data.get('news', []))}")
        print(f"  分页信息: {data.get('pagination', {})}")
        print()
    except Exception as e:
        print(f"获取新闻失败: {e}")
        print()

def test_music_api(token=None):
    """测试音乐API"""
    print("=== 测试音乐API ===")
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(f"{BASE_URL}/api/music", headers=headers)
        print(f"获取音乐列表:")
        print(f"  状态码: {response.status_code}")
        data = response.json()
        print(f"  音乐数量: {len(data.get('music', []))}")
        print(f"  分页信息: {data.get('pagination', {})}")
        print()
    except Exception as e:
        print(f"获取音乐失败: {e}")
        print()

def test_api_status():
    """测试API状态"""
    print("=== 测试API状态 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"API状态:")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
        print()
    except Exception as e:
        print(f"API状态检查失败: {e}")
        print()

def main():
    """主函数"""
    print("开始测试用户认证API...")
    print()
    
    # 测试API状态
    test_api_status()
    
    # 测试注册
    test_register()
    
    # 测试登录
    token = test_login()
    
    # 测试新闻API
    test_news_api(token)
    
    # 测试音乐API
    test_music_api(token)
    
    print("测试完成！")

if __name__ == "__main__":
    main() 
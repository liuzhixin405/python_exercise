#!/usr/bin/env python3
"""
测试后台管理访问
"""
import urllib.request
import urllib.error

def test_admin_access():
    """测试后台管理页面访问"""
    urls = [
        "http://localhost:5001/admin/login",
        "http://localhost:5001/admin/register",
        "http://localhost:5001/",
        "http://localhost:5001/api/admin/news?page=1",
    ]
    
    for url in urls:
        try:
            print(f"测试访问: {url}")
            response = urllib.request.urlopen(url, timeout=5)
            print(f"✅ 状态码: {response.getcode()}")
            content = response.read()
            print(f"✅ 内容长度: {len(content)} 字节")
            if "api/admin/news" in url:
                print(f"✅ 内容预览: {content[:200].decode('utf-8')}...")
            print("-" * 50)
        except urllib.error.URLError as e:
            print(f"❌ 访问失败: {e}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            print("-" * 50)

if __name__ == "__main__":
    test_admin_access() 
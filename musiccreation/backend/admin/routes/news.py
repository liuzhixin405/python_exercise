"""
新闻管理路由 - 处理新闻管理页面
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from admin.utils.auth import require_admin, get_current_user
from admin.models.mysql_data_store import mysql_data_store
from admin.utils.file_upload import save_uploaded_file

news_bp = Blueprint('news', __name__)

@news_bp.route('/admin/news')
@require_admin
def admin_news():
    """新闻管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 获取分页新闻数据
    result = mysql_data_store.get_news_paginated(page=page, per_page=per_page)
    
    return render_template('admin/simple_news.html', 
                         news=result['news'], 
                         current_page=page, 
                         total_pages=result['pages'])

@news_bp.route('/admin/news/create', methods=['GET', 'POST'])
@require_admin
def create_news():
    """创建新闻"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        # 验证输入
        if not title or len(title) > 100:
            flash('标题不能为空且长度不能超过100字符！', 'error')
            return render_template('admin/create_news.html')
        
        if not description or len(description) > 500:
            flash('描述不能为空且长度不能超过500字符！', 'error')
            return render_template('admin/create_news.html')
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            uploaded_url = save_uploaded_file(file)
            if uploaded_url:
                image_url = uploaded_url
        
        if not image_url:
            flash('请提供图片URL或上传图片！', 'error')
            return render_template('admin/create_news.html')
        
        # 创建新闻
        current_user = get_current_user()
        # 使用后台用户名作为作者
        author_name = current_user.get('real_name') or current_user.get('username')
        mysql_data_store.create_news(title, description, image_url, author_name)
        
        flash('新闻创建成功！', 'success')
        return redirect(url_for('news.admin_news'))
    
    return render_template('admin/create_news.html')

@news_bp.route('/admin/news/edit/<int:news_id>', methods=['GET', 'POST'])
@require_admin
def edit_news(news_id):
    """编辑新闻"""
    news = mysql_data_store.get_news_by_id(news_id)
    if not news:
        flash('新闻不存在！', 'error')
        return redirect(url_for('news.admin_news'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        # 验证输入
        if not title or len(title) > 100:
            flash('标题不能为空且长度不能超过100字符！', 'error')
            return render_template('admin/edit_news.html', news=news)
        
        if not description or len(description) > 500:
            flash('描述不能为空且长度不能超过500字符！', 'error')
            return render_template('admin/edit_news.html', news=news)
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            uploaded_url = save_uploaded_file(file)
            if uploaded_url:
                image_url = uploaded_url
        
        # 更新新闻
        mysql_data_store.update_news(news_id, title, description, image_url)
        
        flash('新闻更新成功！', 'success')
        return redirect(url_for('news.admin_news'))
    
    return render_template('admin/edit_news.html', news=news)

@news_bp.route('/admin/news/delete/<int:news_id>', methods=['POST'])
@require_admin
def delete_news(news_id):
    """删除新闻"""
    if mysql_data_store.delete_news(news_id):
        flash('新闻删除成功！', 'success')
    else:
        flash('新闻不存在！', 'error')
    
    return redirect(url_for('news.admin_news')) 
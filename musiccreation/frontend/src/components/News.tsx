import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Loader2, Image as ImageIcon, Trash2 } from 'lucide-react';
import Toast from './Toast';

interface NewsItem {
  id: number;
  title: string;
  description: string;
  image_url: string;
  author: string;
  author_id: number;
  created_at: string;
}

interface NewsProps {
  isLoggedIn: boolean;
  currentUser: string | null;
}

const News: React.FC<NewsProps> = ({ isLoggedIn, currentUser }) => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    description: '',
    image_url: ''
  });
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'warning' | 'info'; isVisible: boolean }>({
    message: '',
    type: 'info',
    isVisible: false
  });

  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    setToast({ message, type, isVisible: true });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  const fetchNews = async () => {
    try {
      setLoading(true);
      
      // 所有用户都获取公开新闻列表（包括管理员创建的 + 用户创建的）
      const url = 'http://localhost:5000/api/news';
      const response = await fetch(url);
      
      console.log('Debug: Response status:', response.status);
      if (!response.ok) {
        const errorText = await response.text();
        console.log('Debug: Error response:', errorText);
        throw new Error(`Failed to fetch news: ${response.status} ${errorText}`);
      }
      const data = await response.json();
      console.log('Debug: News data received:', data);
      setNews(data.news || []);
      setHasMore(data.news && data.news.length > 6);
    } catch (err) {
      console.error('Error fetching news:', err);
      setError('获取新闻数据失败');
      // 使用假数据作为后备
      setNews([
        {
          id: 1,
          title: 'Taylor Swift 发布新专辑《Midnights》',
          description: '流行天后 Taylor Swift 发布了她的第十张录音室专辑《Midnights》。',
          image_url: 'https://picsum.photos/400/300?random=1',
          author: 'admin',
          author_id: 1,
          created_at: '2024-01-15T10:30:00'
        }
      ]);
      setHasMore(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, [isLoggedIn]); // eslint-disable-line react-hooks/exhaustive-deps

  // 无限滚动监听器
  useEffect(() => {
    const handleScroll = () => {
      if (isLoadingMore || !hasMore) return;
      
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      // 当滚动到距离底部100px时加载更多
      if (scrollTop + windowHeight >= documentHeight - 100) {
        loadMoreNews();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isLoadingMore, hasMore, currentPage, news.length]);

  const loadMoreNews = async () => {
    if (isLoadingMore || !hasMore) return;
    
    setIsLoadingMore(true);
    try {
      const nextPage = currentPage + 1;
      const response = await fetch(`http://localhost:5000/api/news?page=${nextPage}&per_page=6`);
      
      if (response.ok) {
        const data = await response.json();
        const newNews = data.news || [];
        
        if (newNews.length > 0) {
          setNews(prev => [...prev, ...newNews]);
          setCurrentPage(nextPage);
        } else {
          setHasMore(false);
        }
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error loading more news:', error);
      setHasMore(false);
    } finally {
      setIsLoadingMore(false);
    }
  };

  const handleCreateNews = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createForm.title || !createForm.description || !createForm.image_url) {
      showToast('请填写所有字段', 'error');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      console.log('Debug: Token for creating news:', token ? token.substring(0, 20) + '...' : 'No token');
      
      if (!token) {
        showToast('请先登录', 'error');
        return;
      }
      
      const response = await fetch('http://localhost:5000/api/news', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(createForm)
      });

      console.log('Debug: Create news response status:', response.status);
      
      if (response.ok) {
        setShowCreateModal(false);
        setCreateForm({ title: '', description: '', image_url: '' });
        fetchNews();
        showToast('新闻创建成功！', 'success');
      } else {
        const data = await response.json();
        console.log('Debug: Create news error response:', data);
        showToast(data.error || '创建失败', 'error');
      }
    } catch (error) {
      console.error('Error creating news:', error);
      showToast('创建失败，请检查网络连接', 'error');
    }
  };

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteNewsId, setDeleteNewsId] = useState<number | null>(null);

  const handleDeleteClick = (newsId: number) => {
    setDeleteNewsId(newsId);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteNewsId) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/news/${deleteNewsId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        fetchNews();
        showToast('新闻删除成功！', 'success');
      } else {
        const data = await response.json();
        showToast(data.error || '删除失败', 'error');
      }
    } catch (error) {
      console.error('Error deleting news:', error);
      showToast('删除失败，请检查网络连接', 'error');
    } finally {
      setShowDeleteConfirm(false);
      setDeleteNewsId(null);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false);
    setDeleteNewsId(null);
  };

  const handleDeleteNews = async (newsId: number) => {
    // 这个方法现在被 handleDeleteClick 替代
    handleDeleteClick(newsId);
  };





  const ImageWithFallback: React.FC<{ src: string; alt: string; className?: string }> = ({ src, alt, className }) => {
    const [imgSrc, setImgSrc] = useState(src);
    const [hasError, setHasError] = useState(false);

    const handleError = () => {
      if (!hasError) {
        setHasError(true);
        setImgSrc('');
      }
    };

    if (hasError || !imgSrc) {
      return (
        <div className={`${className} bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center`}>
          <div className="text-center text-white">
            <ImageIcon size={48} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm opacity-75">{alt}</p>
          </div>
        </div>
      );
    }

    return (
      <img
        src={imgSrc}
        alt={alt}
        className={className}
        onError={handleError}
        loading="lazy"
      />
    );
  };

  if (loading) {
    return (
      <section className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-64">
            <div className="flex items-center space-x-2">
              <Loader2 className="animate-spin h-8 w-8 text-blue-600" />
              <span className="text-lg text-gray-600">加载中...</span>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <>
      {/* 确认删除对话框 */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">确认删除</h3>
            <p className="text-gray-600 mb-6">确定要删除这条新闻吗？此操作无法撤销。</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={handleDeleteCancel}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                取消
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                确定删除
              </button>
            </div>
          </div>
        </div>
      )}

    <section className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            最新音乐资讯
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            发现最新音乐动态，了解音乐界的热门话题和趋势
            {isLoggedIn && '，你也可以发布自己的音乐故事'}
          </p>
          {error && (
            <div className="mt-4 p-3 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded-lg">
              {error}
            </div>
          )}
        </motion.div>

        {isLoggedIn && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8 space-x-4"
          >
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-medium py-3 px-8 rounded-xl transition-all duration-200 inline-flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              <Plus size={20} />
              <span>发布新闻</span>
            </button>
            <button
              onClick={async () => {
                const token = localStorage.getItem('token');
                console.log('Debug: Current token:', token ? token.substring(0, 20) + '...' : 'No token');
                if (token) {
                  try {
                    const response = await fetch('http://localhost:5000/api/test-token', {
                      headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await response.json();
                    console.log('Debug: Token test result:', data);
                    showToast(response.ok ? 'Token有效' : 'Token无效', response.ok ? 'success' : 'error');
                  } catch (error) {
                    console.error('Token test error:', error);
                    showToast('Token测试失败', 'error');
                  }
                } else {
                  showToast('没有token', 'error');
                }
              }}
              className="bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700 text-white font-medium py-3 px-8 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              测试Token
            </button>
          </motion.div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {news.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="group bg-white rounded-2xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-2xl hover:scale-105"
            >
              <div className="relative h-48 md:h-56 overflow-hidden">
                <ImageWithFallback
                  src={item.image_url}
                  alt={item.title}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                {/* 只有新闻作者才能看到删除按钮 */}
                {isLoggedIn && currentUser && item.author === currentUser && (
                  <div className="absolute top-2 right-2 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <button
                      onClick={() => handleDeleteClick(item.id)}
                      className="bg-red-500 hover:bg-red-600 text-white p-2 rounded-lg transition-colors"
                      title="删除"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                )}
              </div>

              <div className="p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2 group-hover:text-blue-600 transition-colors duration-200">
                  {item.title}
                </h3>
                <p className="text-gray-600 mb-4 line-clamp-2 leading-relaxed">
                  {item.description}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-blue-600">
                    By: {item.author}
                  </span>
                  <span className="text-sm text-gray-500">
                    {new Date(item.created_at).toLocaleDateString('zh-CN', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {isLoadingMore && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-8"
          >
            <div className="flex items-center justify-center space-x-2">
              <Loader2 className="animate-spin h-6 w-6 text-blue-600" />
              <span className="text-gray-600">加载更多...</span>
            </div>
          </motion.div>
        )}

        {!hasMore && news.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-8"
          >
            <p className="text-gray-500 text-lg">
              已显示全部内容
            </p>
          </motion.div>
        )}

        {news.length === 0 && !loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16"
          >
            <div className="text-6xl mb-4">🎵</div>
            <h3 className="text-2xl font-semibold text-gray-900 mb-2">
              暂无新闻
            </h3>
            <p className="text-gray-600">
              {isLoggedIn 
                ? '你还没有发布任何音乐新闻，点击上方按钮开始发布吧！'
                : '暂时没有音乐新闻，请稍后再来查看'
              }
            </p>
          </motion.div>
        )}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-lg font-semibold mb-4">发布新闻</h3>
            <form onSubmit={handleCreateNews} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  标题
                </label>
                <input
                  type="text"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  描述
                </label>
                <textarea
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  图片URL
                </label>
                <input
                  type="url"
                  value={createForm.image_url}
                  onChange={(e) => setCreateForm({ ...createForm, image_url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://example.com/image.jpg"
                  required
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
                >
                  发布
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-md transition-colors"
                >
                  取消
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />
    </section>
    </>
  );
};

export default News; 
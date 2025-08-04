import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Menu, X, Settings, User, LogOut } from 'lucide-react';
import Toast from './Toast';

interface NavbarProps {
  currentSection: string;
  onSectionChange: (section: string) => void;
  onAdminClick: () => void;
  scrollProgress: number;
  isLoggedIn: boolean;
  currentUser: string | null;
  onLogin: (username: string) => void;
  onLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ 
  currentSection, 
  onSectionChange, 
  onAdminClick,
  scrollProgress,
  isLoggedIn,
  currentUser,
  onLogin,
  onLogout
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'warning' | 'info'; isVisible: boolean }>({
    message: '',
    type: 'info',
    isVisible: false
  });

  const sections = [
    { id: 'introduction', name: 'Introduction' },
    { id: 'news', name: 'News' }
  ];

  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    setToast({ message, type, isVisible: true });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loginForm.username && loginForm.password) {
      try {
        const response = await fetch('http://localhost:5000/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: loginForm.username,
            password: loginForm.password,
          }),
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
          onLogin(loginForm.username);
          setShowLoginModal(false);
          setLoginForm({ username: '', password: '' });
          showToast('登录成功！', 'success');
          localStorage.setItem('token', data.access_token);
        } else {
          showToast(data.error || data.message || '登录失败', 'error');
        }
      } catch (error) {
        console.error('Login error:', error);
        showToast('登录失败，请检查网络连接', 'error');
      }
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (registerForm.password !== registerForm.confirmPassword) {
      showToast('两次输入的密码不一致', 'error');
      return;
    }
    
    if (registerForm.username && registerForm.email && registerForm.password) {
      try {
        const response = await fetch('http://localhost:5000/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: registerForm.username,
            email: registerForm.email,
            password: registerForm.password,
          }),
        });

        const data = await response.json();

        if (response.ok || response.status === 201) {
          showToast('注册成功！请登录', 'success');
          setShowRegisterModal(false);
          setShowLoginModal(true);
          setRegisterForm({ username: '', email: '', password: '', confirmPassword: '' });
        } else {
          showToast(data.error || data.message || '注册失败', 'error');
        }
      } catch (error) {
        console.error('Register error:', error);
        showToast('注册失败，请检查网络连接', 'error');
      }
    }
  };

  const handleAdminClick = () => {
    window.open('http://localhost:5001/admin/login', '_blank');
  };

  const handleLogout = () => {
    onLogout();
    localStorage.removeItem('token');
    showToast('已退出登录', 'info');
  };

  return (
    <>
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 right-0 z-50 h-1 bg-gray-200">
        <motion.div
          className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
          style={{ width: `${scrollProgress}%` }}
          transition={{ duration: 0.1 }}
        />
      </div>

      {/* Desktop Navigation */}
      <nav className="fixed top-1 left-0 right-0 z-40 bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">FeedMusic</h1>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-8">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => onSectionChange(section.id)}
                  className={`text-sm font-medium transition-colors relative ${
                    currentSection === section.id
                      ? 'text-blue-600'
                      : 'text-gray-700 hover:text-blue-600'
                  }`}
                >
                  {section.name}
                  {currentSection === section.id && (
                    <motion.div
                      className="absolute -bottom-1 left-0 right-0 h-0.5 bg-blue-600"
                      layoutId="activeSection"
                    />
                  )}
                </button>
              ))}
            </div>

            {/* Right side buttons */}
            <div className="hidden md:flex items-center space-x-4">
              {/* Admin Panel Link */}
              <button
                onClick={handleAdminClick}
                className="flex items-center space-x-1 text-sm text-gray-600 hover:text-blue-600 transition-colors"
              >
                <Settings size={16} />
                <span>管理后台</span>
              </button>

              {/* Login/User Info */}
              {isLoggedIn ? (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-700">
                    <User size={16} className="inline mr-1" />
                    {currentUser}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-1 text-sm text-red-600 hover:text-red-700 transition-colors"
                  >
                    <LogOut size={16} />
                    <span>退出</span>
                  </button>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowLoginModal(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    登录
                  </button>
                  <button
                    onClick={() => setShowRegisterModal(true)}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    注册
                  </button>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-700 hover:text-gray-900"
              >
                {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="md:hidden fixed top-17 left-0 right-0 z-30 bg-white border-b border-gray-200 shadow-lg"
        >
          <div className="px-4 py-2 space-y-1">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => {
                  onSectionChange(section.id);
                  setIsMenuOpen(false);
                }}
                className={`block w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentSection === section.id
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                }`}
              >
                {section.name}
              </button>
            ))}
            
            <button
              onClick={() => {
                handleAdminClick();
                setIsMenuOpen(false);
              }}
              className="flex items-center space-x-1 px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-md"
            >
              <Settings size={16} />
              <span>管理后台</span>
            </button>

            {isLoggedIn ? (
              <div className="px-3 py-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">
                    <User size={16} className="inline mr-1" />
                    {currentUser}
                  </span>
                  <button
                    onClick={() => {
                      handleLogout();
                      setIsMenuOpen(false);
                    }}
                    className="text-sm text-red-600 hover:text-red-700"
                  >
                    退出
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-1">
                <button
                  onClick={() => {
                    setShowLoginModal(true);
                    setIsMenuOpen(false);
                  }}
                  className="w-full text-left px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-md"
                >
                  登录
                </button>
                <button
                  onClick={() => {
                    setShowRegisterModal(true);
                    setIsMenuOpen(false);
                  }}
                  className="w-full text-left px-3 py-2 text-gray-600 hover:bg-gray-50 rounded-md"
                >
                  注册
                </button>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Login Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-lg font-semibold mb-4">登录</h3>
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户名
                </label>
                <input
                  type="text"
                  value={loginForm.username}
                  onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  密码
                </label>
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
                >
                  登录
                </button>
                <button
                  type="button"
                  onClick={() => setShowLoginModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-md transition-colors"
                >
                  取消
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}

      {/* Register Modal */}
      {showRegisterModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-lg font-semibold mb-4">注册</h3>
            <form onSubmit={handleRegisterSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户名
                </label>
                <input
                  type="text"
                  value={registerForm.username}
                  onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  邮箱
                </label>
                <input
                  type="email"
                  value={registerForm.email}
                  onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  密码
                </label>
                <input
                  type="password"
                  value={registerForm.password}
                  onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  确认密码
                </label>
                <input
                  type="password"
                  value={registerForm.confirmPassword}
                  onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
                >
                  注册
                </button>
                <button
                  type="button"
                  onClick={() => setShowRegisterModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-md transition-colors"
                >
                  取消
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}

      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />
    </>
  );
};

export default Navbar; 
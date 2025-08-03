import axios from 'axios';
import { AuthResponse, NewsResponse, LoginForm, RegisterForm, CreateNewsForm } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理token过期
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data: RegisterForm) => api.post('/register', data),
  login: (data: LoginForm) => api.post<AuthResponse>('/login', data),
  getProfile: () => api.get('/profile'),
};

export const newsAPI = {
  getNews: (page = 1, perPage = 6) => 
    api.get<NewsResponse>(`/news?page=${page}&per_page=${perPage}`),
  createNews: (data: CreateNewsForm) => api.post('/news', data),
  updateNews: (id: number, data: Partial<CreateNewsForm>) => 
    api.put(`/news/${id}`, data),
  deleteNews: (id: number) => api.delete(`/news/${id}`),
  uploadImage: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default api; 
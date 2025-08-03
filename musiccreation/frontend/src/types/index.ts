export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface News {
  id: number;
  title: string;
  description: string;
  image_url: string;
  created_at: string;
  author: string;
}

export interface AuthResponse {
  message: string;
  access_token: string;
  user: User;
}

export interface NewsResponse {
  news: News[];
  total: number;
  pages: number;
  current_page: number;
}

export interface LoginForm {
  username: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
}

export interface CreateNewsForm {
  title: string;
  description: string;
  image_url: string;
} 
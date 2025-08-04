-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS musiccreation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE musiccreation;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100),
    role ENUM('user', 'admin', 'viewer') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建新闻表
CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    content LONGTEXT,
    image_url VARCHAR(500),
    author_id INT,
    author_name VARCHAR(100),
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    view_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL,
    INDEX idx_author_id (author_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建音乐表
CREATE TABLE IF NOT EXISTS music (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    artist VARCHAR(200),
    album VARCHAR(200),
    genre VARCHAR(100),
    duration INT, -- 秒数
    file_path VARCHAR(500),
    file_size BIGINT,
    uploader_id INT,
    uploader_name VARCHAR(100),
    play_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_artist (artist),
    INDEX idx_genre (genre),
    INDEX idx_uploader_id (uploader_id),
    INDEX idx_status (status),
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建管理员用户表
CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100),
    role ENUM('admin', 'editor', 'viewer') DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入默认管理员用户
INSERT IGNORE INTO admin_users (username, email, password_hash, real_name, role) VALUES
('admin', 'admin@feedmusic.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uOeG', '系统管理员', 'admin');

-- 插入默认系统配置
INSERT IGNORE INTO system_config (config_key, config_value, description) VALUES
('site_name', 'FeedMusic', '网站名称'),
('site_description', '音乐创作与分享平台', '网站描述'),
('max_upload_size', '16777216', '最大上传文件大小（字节）'),
('allowed_file_types', 'jpg,jpeg,png,gif,mp3,wav,flac', '允许上传的文件类型'),
('maintenance_mode', 'false', '维护模式开关');

-- 插入示例新闻数据
INSERT IGNORE INTO news (title, description, content, image_url, author_name, status, published_at) VALUES
('Taylor Swift 发布新专辑《Midnights》', '流行天后 Taylor Swift 发布了她的第十张录音室专辑《Midnights》，这张专辑融合了流行、电子和另类音乐元素，展现了她在音乐创作上的新突破。', '流行天后 Taylor Swift 发布了她的第十张录音室专辑《Midnights》，这张专辑融合了流行、电子和另类音乐元素，展现了她在音乐创作上的新突破。专辑中的每首歌都代表了午夜时分的不同情绪和思考。', 'https://picsum.photos/400/300?random=1', 'admin', 'published', NOW()),
('BTS 成员开始个人活动', '韩国男团 BTS 的成员们开始各自的个人音乐活动，每位成员都展现了独特的音乐风格和个人魅力。', '韩国男团 BTS 的成员们开始各自的个人音乐活动，每位成员都展现了独特的音乐风格和个人魅力。从 RM 的深度思考到 Jungkook 的青春活力，粉丝们对此表示热烈支持。', 'https://picsum.photos/400/300?random=2', 'admin', 'published', NOW()),
('Billie Eilish 获得格莱美大奖', 'Billie Eilish 在今年的格莱美颁奖典礼上获得了多个重要奖项，包括年度专辑和年度歌曲。', 'Billie Eilish 在今年的格莱美颁奖典礼上获得了多个重要奖项，包括年度专辑和年度歌曲。她的音乐才华和独特风格得到了业界的广泛认可。', 'https://picsum.photos/400/300?random=3', 'admin', 'published', NOW()); 
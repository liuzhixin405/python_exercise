-- 创建music表的SQL脚本
-- 用于音乐创作项目的音乐数据存储

USE musiccreation;

-- 删除表（如果存在）
DROP TABLE IF EXISTS music;

-- 创建music表
CREATE TABLE music (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '音乐标题',
    artist VARCHAR(255) NOT NULL COMMENT '艺术家/创作者',
    genre VARCHAR(100) COMMENT '音乐流派',
    duration INT COMMENT '时长（秒）',
    bpm INT COMMENT '每分钟节拍数',
    key_signature VARCHAR(20) COMMENT '调号',
    time_signature VARCHAR(20) COMMENT '拍号',
    description TEXT COMMENT '音乐描述',
    file_path VARCHAR(500) COMMENT '音频文件路径',
    cover_image VARCHAR(500) COMMENT '封面图片路径',
    tags JSON COMMENT '标签（JSON格式）',
    is_public BOOLEAN DEFAULT TRUE COMMENT '是否公开',
    is_featured BOOLEAN DEFAULT FALSE COMMENT '是否推荐',
    play_count INT DEFAULT 0 COMMENT '播放次数',
    like_count INT DEFAULT 0 COMMENT '点赞次数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by INT COMMENT '创建者ID',
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft' COMMENT '状态'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='音乐表';

-- 创建索引
CREATE INDEX idx_music_title ON music(title);
CREATE INDEX idx_music_artist ON music(artist);
CREATE INDEX idx_music_genre ON music(genre);
CREATE INDEX idx_music_created_at ON music(created_at);
CREATE INDEX idx_music_status ON music(status);
CREATE INDEX idx_music_is_public ON music(is_public);
CREATE INDEX idx_music_is_featured ON music(is_featured);

-- 插入示例数据
INSERT INTO music (title, artist, genre, duration, bpm, key_signature, time_signature, description, is_public, status) VALUES
('春日序曲', '音乐创作者', '古典', 180, 120, 'C大调', '4/4', '一首充满春天气息的古典音乐作品', TRUE, 'published'),
('夜空中最亮的星', '独立音乐人', '流行', 240, 85, 'G大调', '4/4', '温暖治愈的流行歌曲', TRUE, 'published'),
('电子舞曲', 'DJ制作人', '电子', 200, 128, 'A小调', '4/4', '动感十足的电子舞曲', TRUE, 'published'),
('爵士即兴', '爵士乐手', '爵士', 300, 90, 'F大调', '3/4', '自由即兴的爵士乐作品', TRUE, 'published'),
('民谣故事', '民谣歌手', '民谣', 280, 75, 'D大调', '6/8', '讲述生活故事的民谣歌曲', TRUE, 'published');

-- 显示创建结果
SELECT 'Music表创建成功！' AS message;
SELECT COUNT(*) AS total_records FROM music; 
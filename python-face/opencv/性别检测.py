import numpy as np
import json

def load_face_features_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        face_points = np.array(data[0])  # 处理实际数据层级
        return calculate_features(face_points)

def calculate_features(face_points):
    def distance(p1, p2):
        return np.sqrt(np.sum((p1 - p2) ** 2))

    # 特征点选择（需要根据具体数据调整索引）
    eye_left = face_points[36]
    eye_right = face_points[45]
    mouth_left = face_points[48]
    mouth_right = face_points[54]
    nose = face_points[30]
    chin = face_points[8]

    face_width = distance(face_points[0], face_points[16])
    face_height = distance(face_points[8], face_points[27])

    # 计算特征比例
    eye_ratio = distance(eye_left, eye_right) / face_width
    mouth_ratio = distance(mouth_left, mouth_right) / face_width
    nose_ratio = distance(nose, chin) / face_height
    face_ratio = face_width / face_height

    return {
        'eye_ratio': eye_ratio,
        'mouth_ratio': mouth_ratio,
        'nose_ratio': nose_ratio,
        'face_ratio': face_ratio
    }

def guess_gender(features):
    # 基于简单规则推测性别
    if features['face_ratio'] < 0.7 and features['nose_ratio'] < 0.2:
        return 'male'
    elif features['face_ratio'] >= 0.7 and features['nose_ratio'] >= 0.2:
        return 'female'
    else:
        return 'unknown'

def main():
    file_path = 'landmarks_data.json'
    features = load_face_features_from_json(file_path)
    
    gender = guess_gender(features)
    
    print(f"推测性别: {gender}")

if __name__ == "__main__":
    main()

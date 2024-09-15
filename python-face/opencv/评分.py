import json
import numpy as np

class FaceFeatures:
    def __init__(self, eye_ratio, mouth_ratio, nose_ratio, face_ratio):
        self.eye_ratio = eye_ratio
        self.mouth_ratio = mouth_ratio
        self.nose_ratio = nose_ratio
        self.face_ratio = face_ratio

class AppearanceRating:
    def __init__(self, female_rating):
        self.female_rating = female_rating

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

    return FaceFeatures(eye_ratio, mouth_ratio, nose_ratio, face_ratio)

def get_aesthetic_score(feature, feature_type):
    # 调整的评分逻辑
    if feature_type == 'eye_ratio':
        if feature > 0.35:
            return 9.0
        elif feature > 0.3:
            return 8.0
        elif feature > 0.25:
            return 6.0
        else:
            return 4.0
    elif feature_type == 'mouth_ratio':
        if feature > 0.8:
            return 9.0
        elif feature > 0.7:
            return 8.0
        elif feature > 0.6:
            return 6.0
        else:
            return 4.0
    elif feature_type == 'nose_ratio':
        if feature < 0.15:
            return 9.0
        elif feature < 0.2:
            return 8.0
        elif feature < 0.25:
            return 6.0
        else:
            return 4.0
    elif feature_type == 'face_ratio':
        if feature > 0.75:
            return 9.0
        elif feature > 0.7:
            return 8.0
        elif feature > 0.65:
            return 6.0
        else:
            return 4.0

def calculate_total_score(features):
    eye_score = get_aesthetic_score(features.eye_ratio, 'eye_ratio')
    mouth_score = get_aesthetic_score(features.mouth_ratio, 'mouth_ratio')
    nose_score = get_aesthetic_score(features.nose_ratio, 'nose_ratio')
    face_score = get_aesthetic_score(features.face_ratio, 'face_ratio')

    return (eye_score * 0.3) + (mouth_score * 0.2) + (nose_score * 0.2) + (face_score * 0.3)

def get_appearance_rating(total_score):
    if total_score >= 27:
        return AppearanceRating("美丽、优雅")
    elif total_score >= 20:
        return AppearanceRating("普通、亲切")
    elif total_score >= 15:
        return AppearanceRating("普通偏丑")
    else:
        return AppearanceRating("丑")

def main():
    file_path = 'landmarks_data.json'
    features = load_face_features_from_json(file_path)
    
    total_score = calculate_total_score(features)
    rating = get_appearance_rating(total_score)
    
    print(f"总分: {total_score:.2f}")
    print(f"女性评价: {rating.female_rating}")

if __name__ == "__main__":
    main()
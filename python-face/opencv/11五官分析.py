import cv2
import dlib
import json
import math

# 读取图片和灰度转换
def load_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to load image at {image_path}")
        return None, None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img, gray

# 提取特征点并保存为列表
def extract_landmarks(landmarks):
    points = []
    for n in range(68):
        x = landmarks.part(n).x
        y = landmarks.part(n).y
        points.append((x, y))
    return points

# 将特征点保存为JSON文件
def save_landmarks_to_json(landmarks_list, output_path):
    with open(output_path, 'w') as f:
        json.dump(landmarks_list, f)
    print(f"Landmarks saved to {output_path}")

# 从JSON文件中加载特征点
def load_landmarks_from_json(json_path):
    with open(json_path, 'r') as f:
        landmarks_list = json.load(f)
    return landmarks_list

# 计算两个点之间的欧几里得距离
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# 分析眼睛的宽高比
def analyze_eye_shape(landmarks):
    # 左眼6个点：36-41，右眼6个点：42-47
    left_eye = landmarks[36:42]
    right_eye = landmarks[42:48]

    # 计算眼睛宽度和高度
    def eye_ratio(eye_points):
        eye_width = calculate_distance(eye_points[0], eye_points[3])
        eye_height = (calculate_distance(eye_points[1], eye_points[5]) + calculate_distance(eye_points[2], eye_points[4])) / 2
        return eye_width / eye_height

    left_eye_ratio = eye_ratio(left_eye)
    right_eye_ratio = eye_ratio(right_eye)

    print(f"Left Eye Ratio: {left_eye_ratio:.2f}")
    print(f"Right Eye Ratio: {right_eye_ratio:.2f}")

    # 判断眼睛类型
    if left_eye_ratio > 3.0 or right_eye_ratio > 3.0:
        print("Eye Shape: 丹凤眼 (Almond-shaped eyes)")
    elif left_eye_ratio < 2.0 or right_eye_ratio < 2.0:
        print("Eye Shape: 桃花眼 (Peach blossom eyes)")
    else:
        print("Eye Shape: 普通眼型 (Normal eye shape)")

# 分析嘴巴形状
def analyze_mouth_shape(landmarks):
    # 嘴巴点：48-67
    mouth = landmarks[48:68]

    # 计算嘴巴的宽度和高度
    mouth_width = calculate_distance(mouth[0], mouth[6])
    mouth_height = (calculate_distance(mouth[3], mouth[9]) + calculate_distance(mouth[2], mouth[10])) / 2
    mouth_ratio = mouth_width / mouth_height

    print(f"Mouth Ratio: {mouth_ratio:.2f}")

    # 判断嘴巴类型
    if mouth_ratio > 2.0:
        print("Mouth Shape: 大嘴巴 (Wide mouth)")
    elif mouth_ratio < 1.5:
        print("Mouth Shape: 小嘴巴 (Small mouth)")
    else:
        print("Mouth Shape: 普通嘴型 (Normal mouth shape)")

# 分析鼻子形状
def analyze_nose_shape(landmarks):
    # 鼻子点：27-35
    nose = landmarks[27:36]

    # 计算鼻子的宽度和长度
    nose_width = calculate_distance(nose[0], nose[4])
    nose_height = calculate_distance(nose[0], nose[6])
    nose_ratio = nose_height / nose_width

    print(f"Nose Ratio: {nose_ratio:.2f}")

    # 判断鼻子类型
    if nose_ratio > 1.5:
        print("Nose Shape: 高鼻梁 (High nose bridge)")
    else:
        print("Nose Shape: 平鼻梁 (Flat nose bridge)")

# 分析脸型
def analyze_face_shape(landmarks):
    # 轮廓点：0-16
    jaw = landmarks[0:17]

    # 计算下巴的宽度和脸的高度
    jaw_width = calculate_distance(jaw[0], jaw[16])
    face_height = calculate_distance(jaw[8], jaw[0])  # 0号点为下巴最下面，8号点为最上面的点
    face_ratio = face_height / jaw_width

    print(f"Face Ratio: {face_ratio:.2f}")

    # 判断脸型
    if face_ratio > 1.5:
        print("Face Shape: 瓜子脸 (Oval face)")
    elif face_ratio < 1.2:
        print("Face Shape: 方脸 (Square face)")
    else:
        print("Face Shape: 圆脸 (Round face)")

# 主函数
def analyze_landmarks(json_path):
    # 加载特征点数据
    landmarks_list = load_landmarks_from_json(json_path)

    # 遍历每张人脸并分析五官形状
    for i, landmarks in enumerate(landmarks_list):
        print(f"Analyzing face {i+1}:")
        analyze_eye_shape(landmarks)
        analyze_mouth_shape(landmarks)
        analyze_nose_shape(landmarks)
        analyze_face_shape(landmarks)
        print("")

if __name__ == "__main__":
    json_path = 'landmarks_data.json'
    analyze_landmarks(json_path)

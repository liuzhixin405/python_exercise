import cv2
import dlib
import json
import os

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

# 主函数
def main(image_path, output_json_path):
    # 加载图片和灰度图像
    img, gray = load_image(image_path)
    if img is None:
        return
    
    # 人脸检测
    face_detector = dlib.get_frontal_face_detector()
    faces = face_detector(gray, 1)
    
    if len(faces) == 0:
        print("No face detected.")
        return

    # 加载人脸关键点预测模型
    predictor = dlib.shape_predictor('lib/shape_predictor_68_face_landmarks.dat')

    # 提取并保存每张人脸的特征点
    all_landmarks = []
    for face in faces:
        landmarks = predictor(gray, face)
        points = extract_landmarks(landmarks)
        all_landmarks.append(points)

    # 将所有人脸的特征点保存为JSON文件
    save_landmarks_to_json(all_landmarks, output_json_path)

if __name__ == "__main__":
    image_path = 'lena_resized.jpg'
    output_json_path = 'landmarks_data.json'
    main(image_path, output_json_path)

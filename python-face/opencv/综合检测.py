import cv2
import dlib
from deepface import DeepFace
import numpy as np

# 加载Dlib的面部检测模型
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r'lib\shape_predictor_68_face_landmarks.dat')  # 需要下载68个点的模型

# 读取人脸图片
image_path = 'lena_resized.jpg'
img = cv2.imread(image_path)

# 转为灰度图
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 检测人脸
faces = detector(gray)

# 如果检测到人脸
if len(faces) > 0:
    for face in faces:
        # 提取面部特征点
        landmarks = predictor(gray, face)
        for n in range(0, 68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            cv2.circle(img, (x, y), 1, (255, 0, 0), -1)  # 标记特征点

    # 显示带有标记的图片
    cv2.imshow('Face landmarks', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 使用deepface进行分析，预测年龄、性别、种族等
    analysis = DeepFace.analyze(img_path=image_path, actions=['age', 'gender', 'race', 'emotion'])

    # 输出分析结果
    print(f"年龄: {analysis[0]['age']}")
    print(f"性别: {analysis[0]['gender']}")
    print(f"种族: {analysis[0]['dominant_race']}")
    print(f"情绪: {analysis[0]['dominant_emotion']}")

    # 对相貌或性格进行简单评分 (举例，根据情绪和年龄评分)
    age = analysis[0]['age']
    dominant_emotion = analysis[0]['dominant_emotion']

    # 假设根据年龄和情绪做一个简单评分
    score = 100 - abs(30 - age)  # 年龄30为满分，离30越远分数越低

    if dominant_emotion == "happy":
        score += 10  # 如果情绪是开心的，增加额外分数

    print(f"面部评分: {score}/100")

else:
    print("未检测到人脸！")


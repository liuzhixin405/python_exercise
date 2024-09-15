import cv2
import dlib

# 读取图片和灰度转换
img = cv2.imread('lena_resized.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#人脸检测
face_detector = dlib.get_frontal_face_detector()
faces = face_detector(gray, 1)

# 人脸识别

preditor = dlib.shape_predictor('lib\shape_predictor_68_face_landmarks.dat')
for face in faces:
    shap = preditor(gray, face)
    # 绘制68个特征点
    for n in range(68):
        x = shap.part(n).x
        y = shap.part(n).y
        cv2.circle(img, (x, y), 1, (0, 255, 0), 2)

    #显示68个特征点
    cv2.imshow('face',img)
    cv2.waitKey(0)        
    cv2.destroyAllWindows()
import cv2 as cv
import os

from PIL import Image
import numpy as np

def getImagesAndLabels(path):
    # 定义一个空列表，用来存放图像数据和标签
    faceSamples = []
    # 定义一个空列表，用来存放标签
    ids = []
    #存储图片信息
    imagePaths=[os.path.join(path, f) for f in os.listdir(path)]
    #加载分类器
    face_detector = cv.CascadeClassifier('G:/Downloads/opencv/sources/data/haarcascades/haarcascade_frontalface_alt2.xml')
    # 遍历文件夹下的每一个人名
    for imagePath in imagePaths:
        # 读取图片,灰度化PIL有九种不同模式,  这里选择L模式 
        PIL_img = Image.open(imagePath).convert('L')
        # 将图片转换为numpy数组
        img_numpy = np.array(PIL_img, 'uint8')
        # 人脸检测
        faces = face_detector.detectMultiScale(img_numpy)
        #获取每张图片的id和姓名
        id = int(os.path.split(imagePath)[1].split(".")[0])
        # 如果检测到人脸
        for (x, y, w, h) in faces:
            # 将人脸图像保存到列表
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            # 将人名保存到列表
            ids.append(id)


    #打印脸部特征和id
    print('id:',id)
    print('fs:',faceSamples)
    return faceSamples, ids

if __name__ == '__main__':
        #图片路径
    path='data/jm/'
    #获取特征        
    faces,ids = getImagesAndLabels(path)
    #加载识别器
    recognizer = cv.face.LBPHFaceRecognizer_create()
    #训练识别器
    recognizer.train(faces, np.array(ids))
    #保存训练好的识别器
    recognizer.write('trainner/trainner_girl.yml')
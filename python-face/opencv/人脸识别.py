import cv2
import os
import urllib
import urllib.request

#加载训练数据文件
recognizer = cv2.face.LBPHFaceRecognizer_create()
#加载数据
recognizer.read('trainner/trainner_girl.yml')
#名称
names=[]
#报警全局变量
warningtime=0
#md5加密
def md5(str):
    import hashlib
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()
#短信反馈
def send_sms(msg):
  print('短信已发送')
#报警模块
def warning():
    print('有人偷偷的进来了,请注意')


#准备识别的图片
def detect_face(img):
    #转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #加载人脸识别分类器
    face_detector = cv2.CascadeClassifier('G:/Downloads/opencv/sources/data/haarcascades/haarcascade_frontalface_alt2.xml')
    #人脸检测   
   #face = face_detector.detectMultiScale(gray,1.1,5,cv2.CASCADE_SCALE_IMAGE,(100,100),(300,300))
    face=face_detector.detectMultiScale(gray,1.1,5,cv2.CASCADE_SCALE_IMAGE,(100,100),(300,300))

   #gary, 1.1,5,0,(10,10),(100,100)
    for (x,y,w,h) in face: 
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        cv2.circle(img,center=(x+w//2,y+h//2),radius=w//2,color=(0,255,0),thickness=1)
        #人脸识别
        try:
            id, conf = recognizer.predict(gray[y:y + h, x:x + w])
        except Exception as e:
            print(f"人脸识别失败: {e}")
            continue
        if conf > 80 :
            global warningtime
            warningtime+=1
            if warningtime>100:
                warning()
                warningtime=0
            cv2.putText(img,'unkonw',(1+10,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,255,0),1)
        else:
            cv2.putText(img,str(names[id-1]),(x+10,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,255,0),1)
            print('识别的id:',id)
    cv2.imshow('result',img)


def name():
    path='data/jm'
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    for imagePath in imagePaths:
        name=str(os.path.split(imagePath)[1].split('.',2)[1])
        names.append(name)


cap = cv2.VideoCapture(0)
name()
while True:
    flag,frame = cap.read()
    if not flag:
        break
    detect_face(frame)
    if ord(' ') == cv2.waitKey(10):
        break
cv2.destroyAllWindows()
cap.release()
print(names)


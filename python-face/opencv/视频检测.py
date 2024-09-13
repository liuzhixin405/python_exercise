# 导入图片
import cv2 as cv

# 定义人脸检测函数
def face_detect_demo(img):
    gary = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    face_detect = cv.CascadeClassifier('G:/Downloads/opencv/sources/data/haarcascades/haarcascade_frontalface_default.xml')
    #face = face_detect.detectMultiScale(gary, 1.1,5,0,(10,10),(100,100))
    face = face_detect.detectMultiScale(gary)
    for x,y,w,h in face:
        cv.rectangle(img, (x,y), (x+w,y+h), color=(0,0,255), thickness=2)
    cv.imshow('result', img)

#读取摄像头
cap=cv.VideoCapture(0)
cap.read()
#等待
while True:
    flag,frame=cap.read()
    if not flag:
        break
    face_detect_demo(frame)
    if cv.waitKey(0) & 0xFF == ord('q'):
        break
cv.waitKey(0)

#释放摄像头
cap.release()
#释放内存
cv.destroyAllWindows()

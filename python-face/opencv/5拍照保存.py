# 导入图片
import cv2 as cv

cap=cv.VideoCapture(0)

falg = 1
num = 1

while(cap.isOpened()):
    ret_flag,Vshow = cap.read()
    cv.imshow("Capture_Test",Vshow)
    k = cv.waitKey(1) & 0xFF
    if k == ord('s'):
        cv.imwrite(str(num) + ".name"+".jpg",Vshow)
        print("success to save "+str(num)+" .jpg")
        num +=1
    elif k == ord(' '):
        break

#释放摄像头
cap.release()
#释放内存
cv.destroyAllWindows()

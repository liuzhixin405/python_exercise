# 导入图片
import cv2 as cv
# 显示图片
img = cv.imread('g:\code\python-face\opencv\lena_resized.jpg')
#坐标
x,y,w,h=100,100,100,100
#绘制矩形
cv.rectangle(img,(x,y),(x+w,y+h),(0,0,255),thickness=1)
#绘制圆形
cv.circle(img,center=(x+w,y+h),radius=100,color=(255,0,0),thickness=2)
#显示
cv.imshow('re_image',img)
#等待
while True:
    if cv.waitKey(0) & 0xFF == ord('q'):
        break
cv.waitKey(0)
#释放内存
cv.destroyAllWindows()
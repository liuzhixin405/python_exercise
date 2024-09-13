# 导入图片
import cv2 as cv
# 显示图片
img = cv.imread('g:\code\python-face\opencv\lena.jpg')
# 灰度转换
gray_img=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
cv.imshow('gray', gray_img)
#保存灰度图片
cv.imwrite('gray_face1.jpg',gray_img)
#等待
cv.waitKey(0)
#释放内存
cv.destroyAllWindows()
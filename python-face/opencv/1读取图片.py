# 导入图片
import cv2 as cv
# 显示图片
img = cv.imread('g:\code\python-face\opencv\lena.jpg')
cv.imshow('read_image', img)
#等待
cv.waitKey(0)
#释放内存
cv.destroyAllWindows()
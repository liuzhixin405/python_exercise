# 导入图片
import cv2 as cv
# 显示图片
img = cv.imread('g:\code\python-face\opencv\lena.jpg')
#修改尺寸
resized_img = cv.resize(img, (200, 200))
#显示原图
cv.imshow('Original Image', img)
#显示修改后图片
cv.imshow('Resized Image', resized_img)
#打印原图片尺寸
print('Original Image Size:', img.shape)
#打印修改后的尺寸
print('Resized Image Size:', resized_img.shape)
#等待
while True:
    if cv.waitKey(0) & 0xFF == ord('q'):
        break
cv.waitKey(0)
#释放内存
cv.destroyAllWindows()
import cv2
import numpy as np
#mediapipe人工智能处理库
import mediapipe as mp
#tqdm进度条库
from tqdm import tqdm
#时间库
import time
#导入绘图
import matplotlib.pyplot as plt

def look_img(img):
    '''opencv读入图像格式为BGR,matplotlib可视化格式为RGB,因此需要转换RGB'''
    img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img_RGB)
    plt.show()
#处理帧函数
def process_frame(img):
    #记录该帧开始时间
    start_time = time.time()
    #导入三维人脸关键点检测模型
    mp_face_mesh = mp.solutions.face_mesh
    model=mp_face_mesh.FaceMesh(static_image_mode=True,refine_landmarks=True,max_num_faces=5,min_detection_confidence=0.5,min_tracking_confidence=0.5)

    #获取图片宽高
    h,w=img.shape[0],img.shape[1]
    #BGR格式转RGB格式
    img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #将RGB图像输入模型,获取预测结果
    results = model.process(img_RGB)
    #文字大小
    scaler=1
    radius=20
    lw=3
    #如果检测到人脸
    if results.multi_face_landmarks:
       #获取相关关键点坐标
       #脸轮廓最左点
       FL=results.multi_face_landmarks[0].landmark[234];FL_X,FL_Y=int(FL.x*w),int(FL.y*h);FL_Color=(0,0,255)
       img=cv2.circle(img,(FL_X,FL_Y),20,FL_Color,-1)
       #脸上边缘
       FT=results.multi_face_landmarks[0].landmark[10];FT_X,FT_Y=int(FT.x*w),int(FT.y*h);FT_Color=(31,41,81)
       img=cv2.circle(img,(FT_X,FT_Y),20,FT_Color,-1)

       #脸下边缘
       FB=results.multi_face_landmarks[0].landmark[152];FB_X,FB_Y=int(FB.x*w),int(FB.y*h);FB_Color=(31,41,81) 
       img=cv2.circle(img,(FB_X,FB_Y),20,FB_Color,-1)

       #脸轮廓最右点
       FR=results.multi_face_landmarks[0].landmark[454];FR_X,FR_Y=int(FR.x*w),int(FR.y*h);FR_Color=(0,255,0)
       img=cv2.circle(img,(FR_X,FR_Y),20,FR_Color,-1)
       #五眼
       #左边眼睛左眼角
       ELL=results.multi_face_landmarks[0].landmark[33];ELL_X,ELL_Y=int(ELL.x*w),int(ELL.y*h);ELL_Color=(255,0,0)
       img=cv2.circle(img,(ELL_X,ELL_Y),20,ELL_Color,-1)
  
       #左边眼睛右眼角
       ELR=results.multi_face_landmarks[0].landmark[133];ELR_X,ELR_Y=int(ELR.x*w),int(ELR.y*h);ELR_Color=(0,255,0)
       img=cv2.circle(img,(ELR_X,ELR_Y),20,ELR_Color,-1)
     
       #右边眼睛左眼角
       ERL=results.multi_face_landmarks[0].landmark[362];ERL_X,ERL_Y=int(ERL.x*w),int(ERL.y*h);ERL_Color=(223,150,0)
       img=cv2.circle(img,(ERL_X,ERL_Y),20,ERL_Color,-1)
     
       #右边眼睛右眼角
       ERR=results.multi_face_landmarks[0].landmark[263];ERR_X,ERR_Y=int(ERR.x*w),int(ERR.y*h);ERR_Color=(151,57,0)
       img=cv2.circle(img,(ERR_X,ERR_Y),5,ERR_Color,-1)
       #眉心
       MX=results.multi_face_landmarks[0].landmark[9];MX_X,MX_Y=int(MX.x*w),int(MX.y*h);MX_Color=(29,123,243)
       img=cv2.circle(img,(MX_X,MX_Y),radius,MX_Color,-1)
       #鼻翼下缘
       NB=results.multi_face_landmarks[0].landmark[2];NB_X,NB_Y=int(NB.x*w),int(NB.y*h);NB_Color=(180,187,28)
       img=cv2.circle(img,(NB_X,NB_Y),radius,NB_Color,-1)
       #嘴唇中心
       LC=results.multi_face_landmarks[0].landmark[13];LC_X,LC_Y=int(LC.x*w),int(LC.y*h);LC_Color=(0,0,255)
       img=cv2.circle(img,(LC_X,LC_Y),radius,LC_Color,-1)
       #嘴唇下缘
       LB=results.multi_face_landmarks[0].landmark[17];LB_X,LB_Y=int(LB.x*w),int(LB.y*h);LB_Color=(139,0,0)
       img=cv2.circle(img,(LB_X,LB_Y),radius,LB_Color,-1)
       #达芬奇
       #嘴唇左角
       LL=results.multi_face_landmarks[0].landmark[61];LL_X,LL_Y=int(LL.x*w),int(LL.y*h);LL_Color=(255,255,255)
       img=cv2.circle(img,(LL_X,LL_Y),radius,LL_Color,-1)
       #嘴唇右角
       LR=results.multi_face_landmarks[0].landmark[291];LR_X,LR_Y=int(LR.x*w),int(LR.y*h);LR_Color=(255,255,255)
       img=cv2.circle(img,(LR_X,LR_Y),radius,LR_Color,-1)
       #鼻子左缘
       NL=results.multi_face_landmarks[0].landmark[129];NL_X,NL_Y=int(NL.x*w),int(NL.y*h);NL_Color=(255,255,255)
       img=cv2.circle(img,(NL_X,NL_Y),radius,NL_Color,-1)       
       #鼻子右缘
       NR=results.multi_face_landmarks[0].landmark[358];NR_X,NR_Y=int(NR.x*w),int(NR.y*h);NR_Color=(255,255,255)
       img=cv2.circle(img,(NR_X,NR_Y),radius,NR_Color,-1)

       #眉毛
       #左眉毛左眉角
       EBLL=results.multi_face_landmarks[0].landmark[46];EBLL_X,EBLL_Y=int(EBLL.x*w),int(EBLL.y*h);EBLL_Color=(0,255,0)
       img=cv2.circle(img,(EBLL_X,EBLL_Y),radius,EBLL_Color,-1)
       #左眉毛左眉峰
       EBLT=results.multi_face_landmarks[0].landmark[105];EBLT_X,EBLT_Y=int(EBLT.x*w),int(EBLT.y*h);EBLT_Color=(0,255,0)
       img=cv2.circle(img,(EBLT_X,EBLT_Y),radius,EBLT_Color,-1)
       #左眉毛右角
       EBLR=results.multi_face_landmarks[0].landmark[107];EBLR_X,EBLR_Y=int(EBLR.x*w),int(EBLR.y*h);EBLR_Color=(0,255,0)
       img=cv2.circle(img,(EBLR_X,EBLR_Y),radius,EBLR_Color,-1)
       #右眉毛左角
       EBRL=results.multi_face_landmarks[0].landmark[336];EBRL_X,EBRL_Y=int(EBRL.x*w),int(EBRL.y*h);EBRL_Color=(0,255,0)
       img=cv2.circle(img,(EBRL_X,EBRL_Y),radius,EBRL_Color,-1)
       #右眉毛眉峰
       EBRT=results.multi_face_landmarks[0].landmark[334];EBRT_X,EBRT_Y=int(EBRT.x*w),int(EBRT.y*h);EBRT_Color=(0,255,0)
       img=cv2.circle(img,(EBRT_X,EBRT_Y),radius,EBRT_Color,-1)
       #右眉毛右眉角
       EBRR=results.multi_face_landmarks[0].landmark[276];EBRR_X,EBRR_Y=int(EBRR.x*w),int(EBRR.y*h);EBRR_Color=(0,255,0)
       img=cv2.circle(img,(EBRR_X,EBRR_Y),radius,EBRR_Color,-1)
       #左内眼角上点
       ELRT=results.multi_face_landmarks[0].landmark[157];ELRT_X,ELRT_Y=int(ELRT.x*w),int(ELRT.y*h);ELRT_Color=(0,255,0)
       img=cv2.circle(img,(ELRT_X,ELRT_Y),radius,ELRT_Color,-1)
       #左内眼角下点
       ELRB=results.multi_face_landmarks[0].landmark[154];ELRB_X,ELRB_Y=int(ELRB.x*w),int(ELRB.y*h);ELRB_Color=(0,255,0)
       img=cv2.circle(img,(ELRB_X,ELRB_Y),radius,ELRB_Color,-1)
       #右内眼角上点
       ERLT=results.multi_face_landmarks[0].landmark[384];ERLT_X,ERLT_Y=int(ERLT.x*w),int(ERLT.y*h);ERLT_Color=(0,255,0)
       img=cv2.circle(img,(ERLT_X,ERLT_Y),radius,ERLT_Color,-1)
       #右内眼角下点
       ERRB=results.multi_face_landmarks[0].landmark[381];ERRB_X,ERRB_Y=int(ERRB.x*w),int(ERRB.y*h);ERRB_Color=(0,255,0)
       img=cv2.circle(img,(ERRB_X,ERRB_Y),radius,ERRB_Color,-1)
       #嘴角
       #从左往右六个点的横坐标
       Six_X=np.array([FL_X,ELL_X,ELR_X,ERL_X,ERR_X,FR_X])
       #从左到右得距离
       Left_Right=FR_X-FL_X
       #从左往右六个点间隔得五个距离，并归一化
       Five_Distance=100*np.diff(Six_X)/Left_Right
       #两眼宽度的平均值
       Eye_Witdth_Mean=np.mean([Five_Distance[1],Five_Distance[3]])
       #五官距离分别与两眼宽度均值的差
       Five_Eye_Diff=Five_Distance-Eye_Witdth_Mean
       #求L2范数,作为颜值的五眼评价标准
       Five_Eye_Metrics=np.linalg.norm(Five_Eye_Diff)


       #计算三庭  达芬奇指标 内眦角度 三点连线
       Six_Y=np.array([FT_Y,MX_Y,NB_Y,LC_Y,LB_Y,FB_Y])
       #从最上到最下距离
       Top_Down=FB_Y-FT_Y
       #从上到下六个点间隔的五个距离，归并一化
       Three_Section_Distance=100 *np.diff(Six_Y)/Top_Down
       #三庭的后两是否接近，越小越好
       Three_Section_Metric_A=np.abs(Three_Section_Distance[1]-sum(Three_Section_Distance[2:]))
       #鼻下到唇心距离 占 第三庭的三分之一
       Three_Section_Metric_B=np.abs(Three_Section_Distance[2]-sum(Three_Section_Distance[2:])/3)
       #唇心到下吧尖距离占第三庭的二分之一
       Three_Section_Metric_C=np.abs(sum(Three_Section_Distance[3:])-sum(Three_Section_Distance[2:])/2)

       #嘴宽为鼻宽的1.5倍-1.6倍
       Da_Vinci=(LR.x-LL.x)/(NR.x-NL.x)
       #内侧眉头在内眦(内测眼角)正上方-左侧
       #越接近0越好
       EB_Metric_A=(EBLR_X-ELR_X)/Left_Right
       #内侧眉头在内眦(内测眼角)正上方-右侧
       #越接近0越好
       EB_Metric_B=(EBRL_X-ERL_X)/Left_Right
       #眉峰在外眦(外侧眼角)正上方-左侧
       #越接近0越好
       MB_Metric_C=(EBLT_X-ELL_X)/Left_Right
       #眉峰在外眦(外侧眼角)正上方-右侧
       #越接近0越好
       MB_Metric_D=(EBRT_X-ERR_X)/Left_Right
       #外侧眉峰、外侧眼角、鼻翼应处于同一条直线上-左侧
       #计算这三点构成的三角形面积，越小越好
       MB_Metric_E=0.5*np.linalg.det([[EBLL_X,EBLL_Y,1],[ELL_X,ELL_Y,1],[NL_X,NL_Y,1]])/(Left_Right)**2
       #外侧眉峰、外侧眼角、鼻翼应处于同一条直线上-右侧
       #计算这三点构成的三角形面积，越小越好
       MB_Metric_F=0.5*np.linalg.det([[EBRR_X,EBRR_Y,1],[ERR_X,ERR_Y,1],[NR_X,NR_Y,1]])/(Left_Right)**2

       #内眼角开合度数-左侧
       #48-50度为宜
       vector_a=np.array([ELRT_X-ELR_X,ELRT_Y-ELR_Y])
       vector_b=np.array([ELRB_X-ELR_X,ELRB_Y-ELR_Y])
       cos=vector_a.dot(vector_b)/(np.linalg.norm(vector_a)*np.linalg.norm(vector_b))
       EB_Metric_G=np.degrees(np.arccos(cos))
       #内眼角开合度数-右侧
       #48-50度为宜
       vector_a=np.array([ERLT_X-ERL_X,ERLT_Y-ERL_Y])
       vector_b=np.array([ERRB_X-ERL_X,ERRB_Y-ERL_Y])
       cos=vector_a.dot(vector_b)/(np.linalg.norm(vector_a)*np.linalg.norm(vector_b))
       EB_Metric_H=np.degrees(np.arccos(cos))

       cv2.line(img,(FL_X,FT_Y),(FL_X,FB_Y),FL_Color,3)
       cv2.line(img,(ELL_X,FT_Y),(ELL_X,FB_Y),ELL_Color,3)
       cv2.line(img,(ELR_X,FT_Y),(ELR_X,FB_Y),ELR_Color,3)
       cv2.line(img,(ERL_X,FT_Y),(ERL_X,FB_Y),ERL_Color,3)
       cv2.line(img,(ERR_X,FT_Y),(ERR_X,FB_Y),ERR_Color,3)
       cv2.line(img,(FR_X,FT_Y),(FR_X,FB_Y),FR_Color,3)
       cv2.line(img,(FL_X,FT_Y),(FR_X,FT_Y),FL_Color,3)
       cv2.line(img,(FL_X,FB_Y),(FR_X,FB_Y),FB_Color,3)
      
       #可视化
       #外侧眉峰、外侧眼角、鼻翼应处于同一条直线上-左侧
       cv2.line(img,(EBLL_X,EBLL_Y),(ELL_X,ELL_Y),EBLL_Color,lw)
       cv2.line(img,(ELL_X,ELL_Y),(NL_X,NL_Y),EBLL_Color,lw)
       cv2.line(img,(EBLL_X,EBLL_Y),(NL_X,NL_Y),EBLL_Color,lw)
       #外侧眉峰、外侧眼角、鼻翼应处于同一条直线上-右侧
       cv2.line(img,(EBRR_X,EBRR_Y),(ERR_X,ERR_Y),EBLL_Color,lw)
       cv2.line(img,(ERR_X,ERR_Y),(NR_X,NR_Y),EBLL_Color,lw)
       cv2.line(img,(EBRR_X,EBRR_Y),(NR_X,NR_Y),EBLL_Color,lw)
       

       scaler=1
       img=cv2.putText(img,'Five Eye Metrics: {:.2f}'.format(Five_Eye_Metrics),(25*scaler,50*scaler),cv2.FONT_HERSHEY_SIMPLEX,1.25*scaler,(255,255,255),2)
       img=cv2.putText(img,'Distance1: {:.2f}'.format(Five_Eye_Diff[0]),(25*scaler,100*scaler),cv2.FONT_HERSHEY_SIMPLEX,0.2*scaler,(0,0,255),1)
       img=cv2.putText(img,'Distance2: {:.2f}'.format(Five_Eye_Diff[2]),(25*scaler,150*scaler),cv2.FONT_HERSHEY_SIMPLEX,0.2*scaler,(0,0,255),1)
       img=cv2.putText(img,'Distance3: {:.2f}'.format(Five_Eye_Diff[4]),(25*scaler,200*scaler),cv2.FONT_HERSHEY_SIMPLEX,0.2*scaler,(0,0,255),1)

       img=cv2.putText(img,'Three Section Metric A: {:.2f}'.format(Three_Section_Metric_A),(25*scaler,400*scaler),cv2.FONT_HERSHEY_SIMPLEX,0.2*scaler,(0,0,255),1)
       img=cv2.putText(img,'Three Section Metric B: {:.2f}'.format(Three_Section_Metric_B),(25*scaler,450*scaler),cv2.FONT_HERSHEY_SIMPLEX,0.2*scaler,(0,0,255),1)
       img=cv2.putText(img,'Three Section Metric C: {:.2f}'.format(Three_Section_Metric_C),(25*scaler,500*scaler),cv2.FONT_HERSHEY_SIMPLEX,0.2*scaler,(0,0,255),1)

       img=cv2.putText(img,'Da Vinci: {:.2f}'.format(Da_Vinci),(25*scaler,600*scaler),cv2.FONT_HERSHEY_SIMPLEX,1.25*scaler,(0,0,255),1)
    else:
       img=cv2.putText(img,'No Face Detected',(25*scaler,50*scaler),cv2.FONT_HERSHEY_SIMPLEX,1.25*scaler,(255,255,255),2)
    #记录该帧结束时间
    end_time = time.time()
    #计算每秒处理图像帧数FPS
    fps = 1/(end_time-start_time)
    img=cv2.putText(img,'FPS  '+str(int(fps)),(25*scaler,50*scaler),cv2.FONT_HERSHEY_SIMPLEX,1.25*scaler,(255,255,255),2)
    return img


cap=cv2.VideoCapture(0)
cap.open(0)

while cap.isOpened():
    success,frame=cap.read()
    if not success:
        print("failed to read frame")
        break
    start_time=time.time()
    frame=process_frame(frame)
    cv2.imshow("frame",frame)

    if cv2.waitKey(1) in [ord('q'),27]:
        break
cap.release()
cv2.destroyAllWindows()



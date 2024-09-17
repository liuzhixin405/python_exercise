from deepface import DeepFace

# 分析图片中的情绪
analysis = DeepFace.analyze(img_path="lena_resized.jpg", actions=['emotion'])

# 获取各个情绪的概率分布
emotion_scores = analysis[0]['emotion']
print("情绪分布: ", emotion_scores)

# 判断复杂情绪，结合多个情绪分数
def complex_emotion(emotion_scores):
    if emotion_scores['happy'] > 50 and emotion_scores['surprise'] > 20:
        return "快乐且惊喜"
    elif emotion_scores['sad'] > 30 and emotion_scores['fear'] > 20:
        return "悲伤且焦虑"
    elif emotion_scores['angry'] > 40 and emotion_scores['disgust'] > 30:
        return "愤怒且厌恶"
    else:
        return "情绪比较复杂，无法单一定义"

# 打印分析结果
complex_result = complex_emotion(emotion_scores)
print(f"综合情绪: {complex_result}")

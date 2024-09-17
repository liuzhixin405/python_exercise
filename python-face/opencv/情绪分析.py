from deepface import DeepFace

# 使用 deepface 分析情绪
analysis = DeepFace.analyze(img_path="lena_resized.jpg", actions=['emotion'])

dominant_emotion = analysis[0]['dominant_emotion']
print(f"主要情绪: {dominant_emotion}")

# 简单性格分析，基于主要情绪推断
def predict_personality(emotion):
    if emotion == "happy":
        return "外向型, 乐观积极"
    elif emotion == "sad":
        return "内向型, 更加情感化"
    elif emotion == "angry":
        return "冲动型, 易怒"
    elif emotion == "neutral":
        return "理性型, 稳重冷静"
    else:
        return "性格较难预测"

personality = predict_personality(dominant_emotion)
print(f"推断的性格: {personality}")

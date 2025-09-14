import google.generativeai as genai
import os

# 1. API 키 설정
genai.configure(api_key='')

# 2. 사용 가능한 모델 이름으로 설정
# 당신이 제공한 목록 중, 가장 최신 모델인 'gemini-1.5-pro-latest'를 사용합니다.
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# 3. 모델에 질문 보내기 (프롬프트)
response = model.generate_content("인공지능에 대해 한 문장으로 설명해 줘.")

# 4. 모델의 답변 출력
print(response.text)
from openai import OpenAI

# 환경변수에 API 키 저장하는게 안전함
client = OpenAI(api_key="")  # 테스트용으로만 직접 넣기

def chat_with_gpt(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 모델 선택
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    user_input = input("질문을 입력하세요: ")
    answer = chat_with_gpt(user_input)
    print("ChatGPT:", answer)

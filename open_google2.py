import os
import google.generativeai as genai
import google.api_core.exceptions as g_exceptions

def generate(prompt):
    # 환경 변수에서 API 키를 가져와 설정합니다.
    try:
        genai.configure(api_key=os.environ.get(""))
    except TypeError:
        print("오류: 'GEMINI_API_KEY' 환경 변수가 설정되지 않았습니다.")
        return

    # 안정적인 최신 모델을 사용합니다.
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        # 수정된 부분: tools를 genai.Tool.from_google_search()로 설정
        tools=[genai.Tool.from_google_search()]
    )

    # try-except 블록을 사용하여 오류를 처리합니다.
    try:
        print("응답을 생성 중입니다...")
        response = model.generate_content(
            prompt,
            stream=True  # 스트리밍 방식으로 응답을 받습니다.
        )
        
        # 스트리밍되는 응답을 바로 출력합니다.
        for chunk in response:
            print(chunk.text, end="")
        print("\n")

    except g_exceptions.ResourceExhausted:
        print("오류: API 할당량을 초과했습니다. 요금제 확인 또는 잠시 후 다시 시도해 주세요.")
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # 여기에 당신의 질문을 입력하세요.
    user_prompt = "구글 주식의 현재 가격은 얼마인가요? 구글 검색을 사용해서 찾아줘."
    
    if user_prompt:
        generate(user_prompt)
    else:
        print("generate 함수에 프롬프트를 입력해 주세요.")
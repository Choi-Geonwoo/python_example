from playwright.sync_api import sync_playwright
import time

# --- ChatGPT 자동화 시작 ---
with sync_playwright() as p:
    # 1. Persistent Context로 브라우저 실행 (프로필 재사용)
    user_data_dir = "E:/PlaywrightProfile"  # 독립 프로필 경로
    context = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False
    )

    page = context.pages[0] if context.pages else context.new_page()

    # 2. ChatGPT 웹 열기
    page.goto("https://chat.openai.com/")

    # 3. 로그인 안내
    print("\n[안내] 브라우저가 열리면 ChatGPT에 로그인해주세요.")
    input("로그인 완료 후 엔터(Enter)를 눌러 진행...")

    # 4. 질문 입력
    question = "삼성전자 개요"
    chat_input_selector = 'textarea[data-testid="multimodal-text-input"]'

    page.wait_for_selector(chat_input_selector, timeout=20000)
    page.fill(chat_input_selector, question)
    page.press(chat_input_selector, "Enter")
    print("질문 전송 완료! 답변을 기다리는 중...")

    # 5. 답변 수집
    answer_selector = "div[class*='prose']"
    page.wait_for_selector(answer_selector, timeout=30000)
    time.sleep(2)  # 동적 로딩 안정화

    answer = page.query_selector(answer_selector).inner_text()
    print("\nChatGPT 답변:\n", answer)

    # 6. 브라우저 종료
    context.close()

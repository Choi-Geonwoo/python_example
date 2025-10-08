# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pickle
import os
import time

# ==================== 설정 정보 ====================
COOKIES_FILE = "tistory_cookies.pkl"
TISTORY_MAIN = "https://www.tistory.com"
WRITE_URL = ""  # 본인 블로그 주소로 변경

POST_TITLE = "Selenium 자동 포스팅 제목 테스트 (HTML 직접 삽입)"
# 줄바꿈(\n)을 포함하여 단락을 구분합니다.
POST_CONTENT = "이 글은 Selenium 자동화로 작성되었습니다.\n\nTinyMCE 및 ProseMirror 최신 에디터 테스트 중입니다.\n\n이것은 세 번째 단락이며, JavaScript를 통해 HTML로 변환되어 삽입됩니다."

# ==================== Chrome WebDriver 설정 ====================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # 백그라운드 실행 원하면 주석 해제
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# ==================== 쿠키 저장/로드 함수 ====================
def save_cookies(driver, filename):
    """현재 브라우저 쿠키를 파일로 저장합니다."""
    pickle.dump(driver.get_cookies(), open(filename, "wb"))
    print(f"[✔] 쿠키 저장 완료: {filename}")

def load_cookies(driver, filename):
    """저장된 쿠키를 불러와 드라이버에 추가합니다."""
    driver.get(TISTORY_MAIN)
    try:
        cookies = pickle.load(open(filename, "rb"))
        for cookie in cookies:
            # 도메인 조건 확인: Tistory 메인 도메인 또는 서브 도메인에 적용
            if 'domain' in cookie and (TISTORY_MAIN.replace('https://', '').split('/')[0] in cookie['domain'] or '.tistory.com' in cookie['domain']):
                 driver.add_cookie(cookie)
        print(f"[✔] 쿠키 불러오기 완료: {filename}")
    except Exception as e:
        print(f"[❌] 쿠키 로드 실패: {e}")

# ==================== 텍스트를 HTML 단락으로 변환하는 헬퍼 함수 ====================
def convert_to_html_paragraphs(text):
    """
    일반 텍스트를 HTML <p> 태그로 감싸서 반환합니다.
    \n\n 또는 \n을 기준으로 단락을 나눕니다.
    """
    # 2개 이상의 줄바꿈을 <p>와 </p>로 대체하고, <p> 태그 안에 내용을 넣습니다.
    # 단락이 비어있지 않도록 필터링합니다.
    paragraphs = [f"<p data-ke-size='size16'>{line.strip()}</p>" for line in text.split('\n\n') if line.strip()]
    return "".join(paragraphs)

# ==================== 로그인 처리 ====================
if not os.path.exists(COOKIES_FILE):
    print("\n[🚀] 처음 실행입니다. 브라우저가 열리면 로그인하세요 (카카오 로그인 포함).")
    driver.get(TISTORY_MAIN)
    input("로그인 완료 후 엔터 ➤ ")
    save_cookies(driver, COOKIES_FILE)
else:
    print("[🔑] 저장된 쿠키로 자동 로그인 중...")
    load_cookies(driver, COOKIES_FILE)
    driver.refresh()
    time.sleep(3)

# ==================== 글쓰기 페이지 이동 ====================
print("[📝] 글쓰기 페이지로 이동 중...")
driver.get(WRITE_URL)
time.sleep(7)  # 에디터 로딩 대기

# 3. 카테고리 선택 (선택 사항)
# driver.find_element(By.CSS_SELECTOR, "#category_selector").click()
# time.sleep(1)
# driver.find_element(By.XPATH, "//li[text()='국내주식']").click()

try:
    # 1️⃣ 제목 입력 (기존 로직 유지)
    print("[🖊️] 제목 입력 중...")
    # 이게 동작
    try:
        title_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea#post-title-inp"))
        )
        title_input.clear()
        title_input.send_keys(POST_TITLE)
        print(f"[✔] 제목 입력 완료: {POST_TITLE}")
    except:
        title_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='제목을 입력하세요']"))
        )
        title_input.clear()
        title_input.send_keys(POST_TITLE)
        print(f"[✔] 제목 입력 완료 (fallback): {POST_TITLE}")
    time.sleep(1)

    # 2️⃣ 본문 입력 (ProseMirror → TinyMCE fallback)
    print("[🖊️] 본문 입력 중...")
    
    # -----------------------------------------------------
    # ProseMirror 우선 시도 (iframe title에 '글쓰기' 포함)
    # -----------------------------------------------------
    prosemirror_success = False
    try:
        print("[ℹ️] ProseMirror 에디터 시도 중...")
        # ProseMirror iframe은 title에 '글쓰기'가 포함된 경우가 많음
        # iframe 전환과 동시에 해당 iframe 내의 요소가 로드될 때까지 기다림
        wait.until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title*='글쓰기']"))
        )
        
        # ProseMirror 영역 선택
        content_area = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ProseMirror"))
        )
        
        content_area.click()
        # send_keys 대신 JavaScript로 텍스트 삽입
        driver.execute_script("arguments[0].textContent = arguments[1];", content_area, POST_CONTENT)
        
        print("[✔] ProseMirror 본문 입력 완료.")
        prosemirror_success = True
        
    except Exception as e:
        print(f"[ℹ️] ProseMirror 본문 입력 실패 ({type(e).__name__}). TinyMCE로 시도 중...")
        
    finally:
        # iframe에서 기본 컨텐츠로 복귀 (성공/실패 여부와 관계없이)
        driver.switch_to.default_content()

    # -----------------------------------------------------
    # TinyMCE fallback 시도 (iframe id='editor-tistory')
    # -----------------------------------------------------
    if not prosemirror_success:
        try:
            print("[ℹ️] TinyMCE 에디터 시도 중...")
            # 1️⃣ iframe 로딩 대기 후 전환 (더 안정적인 방법 사용)
            wait.until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#editor-tistory"))
            )
            print("[✔] TinyMCE iframe 전환 성공.")

            # 2️⃣ body#tinymce 로드 확인
            # contenteditable='true' 속성이 생길 때까지 기다려 에디터가 완전히 준비되었는지 확인합니다.
            tiny_body = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "body#tinymce[contenteditable='true']"))
            )
            print("[✔] TinyMCE 본문 요소 로드 성공.")
            
            # 3️⃣ 기존 내용 초기화
            driver.execute_script("arguments[0].innerHTML = '';", tiny_body)

            # 4️⃣ 새 내용을 HTML <p> 태그로 변환
            html_content = convert_to_html_paragraphs(POST_CONTENT)
            
            # 5️⃣ JavaScript를 사용하여 HTML을 직접 삽입
            driver.execute_script("arguments[0].innerHTML = arguments[1];", tiny_body, html_content)
            print("[✔] TinyMCE 본문 (HTML) 입력 완료.")

        except Exception as e:
            print(f"[❌] TinyMCE 본문 입력 실패: {type(e).__name__} - {e}")

        finally:
            # 6️⃣ iframe에서 기본 컨텐츠로 복귀
            driver.switch_to.default_content()

        if not prosemirror_success:
            # 이게 동작
            print("[2] ProseMirror 본문 입력 실패. TinyMCE로 시도 중...")
            # 1️⃣ iframe 로딩 대기 (Tistory는 TinyMCE 기반, iframe이 동적으로 로드됨)
            editor_iframe = wait.until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[id^='editor-tistory_ifr']")
                )
            )

            # 2️⃣ 본문 입력 영역 선택
            content_editable = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body[contenteditable='true']"))
            )

            # 3️⃣ 기존 내용 전체 선택 + 삭제 (초기화)
            content_editable.send_keys(Keys.CONTROL, 'a')
            content_editable.send_keys(Keys.DELETE)

            # 4️⃣ 새 본문 작성
            content = "이 글은 Python + Selenium 으로 자동 작성되었습니다."
            content_editable.send_keys(content)
            print("[✔] 본문 입력 완료")

            driver.switch_to.default_content()

    time.sleep(2)

    # 3️⃣ 발행 버튼 클릭
    publish_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='publish'], button[class*='btn_publish']"))
    )
    publish_btn.click()
    print("[🚀] 1차 발행 버튼 클릭 완료!")
    time.sleep(2)

    # 4️⃣ 발행 확인 모달 클릭
    try:
        # '발행' 텍스트를 포함하는 버튼 찾기
        confirm_publish_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '발행')]"))
        )
        confirm_publish_btn.click()
        print("[🚀] 2차 발행(최종 확인 모달) 버튼 클릭 완료!")
    except Exception as e:
        # 발행 확인 모달이 없을 경우 (바로 발행되거나 UI가 다를 경우)
        print(f"[ℹ️] 최종 발행 확인 모달이 없거나 이미 발행됨 ({type(e).__name__})")

    time.sleep(5)
    print("[✅] 글쓰기 완료! 블로그에서 확인하세요.")

except Exception as e:
    print(f"[❌] 글쓰기 중 오류 발생: {type(e).__name__} - {e}")
    try:
        driver.save_screenshot("tistory_error_screenshot.png")
        print("[📸] 오류 시점 스크린샷 저장 완료")
    except:
        print("[❗] 스크린샷 저장 실패")

finally:
    driver.quit()
    print("[✋] WebDriver 종료.")

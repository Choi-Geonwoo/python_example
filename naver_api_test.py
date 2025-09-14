# 이 스크립트는 Selenium을 사용하여 네이버 블로그에 글을 작성하고 게시합니다.
# requests 라이브러리는 동적인 웹 페이지와 복잡한 로그인 절차를 처리하기 어렵기 때문에
# 브라우저 자동화 라이브러리인 Selenium을 사용하는 것이 더 효율적입니다.

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

# ===== 환경 설정 =====
# 사용자의 네이버 아이디와 비밀번호를 입력하세요.
# 주의: 실제 비밀번호를 코드에 직접 작성하는 것은 보안상 권장되지 않습니다.
# 테스트용으로만 사용하거나 환경 변수 등을 활용하세요.
NAVER_ID = "YOUR_NAVER_ID"
NAVER_PW = "YOUR_NAVER_PASSWORD"

# 글 제목과 내용을 정의합니다.
TITLE = "파이썬 자동화 블로그 포스팅 테스트"
CONTENT = "안녕하세요. 이 글은 Selenium을 사용하여 자동으로 작성되었습니다.\n\n파이썬 스크립트로 블로그 글을 써보는 테스트입니다."

# Chrome WebDriver 경로 설정 (다운로드한 드라이버 경로로 변경)
# service = Service('path/to/chromedriver')
# driver = webdriver.Chrome(service=service)

# 웹 드라이버 초기화 (기본적으로 PATH에 있다고 가정)
driver = webdriver.Chrome()

try:
    # ===== 로그인 절차 =====
    print("네이버 로그인 페이지로 이동합니다.")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(2)

    # JavaScript를 사용하여 아이디와 비밀번호 필드에 값을 입력합니다.
    # Selenium send_keys가 작동하지 않을 수 있는 경우를 대비합니다.
    print("로그인 정보를 입력합니다.")
    driver.execute_script(f'document.getElementById("id").value = "{NAVER_ID}";')
    driver.execute_script(f'document.getElementById("pw").value = "{NAVER_PW}";')
    
    # 로그인 버튼 클릭
    driver.find_element(By.ID, "log.login").click()
    time.sleep(5)  # 로그인 완료를 기다립니다.
    
    # 로그인 성공 여부 확인 (예시)
    if driver.current_url.startswith("https://www.naver.com/"):
        print("로그인에 성공했습니다!")
    else:
        print("로그인에 실패했거나 추가 인증이 필요합니다. 스크립트를 종료합니다.")
        driver.quit()
        # 로그인 실패 시 추가적인 로직을 여기에 구현할 수 있습니다.
        # 예를 들어, CAPTCHA를 해결하는 로직 등.
        exit()

    # ===== 블로그 글쓰기 페이지로 이동 =====
    print("블로그 글쓰기 페이지로 이동합니다.")
    driver.get("https://blog.naver.com/PostWrite.naver")
    time.sleep(5)  # 페이지 로드를 기다립니다.

    # 제목 입력 필드 찾기
    print("제목을 입력합니다.")
    title_field = driver.find_element(By.ID, "title")
    title_field.send_keys(TITLE)
    time.sleep(1)

    # 콘텐츠(내용) 입력 필드 찾기
    print("내용을 입력합니다.")
    # 네이버 블로그 에디터는 iframe 내부에 있는 경우가 많으므로 iframe으로 전환해야 합니다.
    try:
        editor_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe[title="editor"]')
        driver.switch_to.frame(editor_iframe)

        # 내용 입력 필드 (p 태그) 찾기
        content_field = driver.find_element(By.CSS_SELECTOR, "body.se-main-container p")
        content_field.send_keys(CONTENT)

        # 다시 메인 프레임으로 전환
        driver.switch_to.default_content()

    except NoSuchElementException:
        print("블로그 에디터 iframe을 찾을 수 없습니다. HTML 구조가 변경되었을 수 있습니다.")
        driver.quit()
        exit()

    # ===== 게시 버튼 클릭 =====
    print("게시 버튼을 찾아서 클릭합니다.")
    # "발행" 버튼의 CSS 선택자를 찾아야 합니다.
    # 일반적으로 'btn_publish' 또는 유사한 클래스 이름을 가집니다.
    # 이 부분은 네이버 블로그 에디터의 최신 HTML에 따라 수정해야 할 수 있습니다.
    publish_button = driver.find_element(By.CSS_SELECTOR, '#se-footer-post-btn')
    publish_button.click()
    time.sleep(5) # 게시 완료를 기다립니다.

    print("글이 성공적으로 게시되었습니다!")
    print(f"작성된 블로그 글 URL: {driver.current_url}")

except Exception as e:
    print(f"오류가 발생했습니다: {e}")

finally:
    # 드라이버를 닫습니다.
    print("브라우저를 닫습니다.")
    driver.quit()

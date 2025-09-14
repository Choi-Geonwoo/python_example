from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_argument("--start-maximized")

# 크롬 드라이버 경로 (본인 환경에 맞게 수정)
webdriver_path = "E:/파이썬_실행파일/Workspace2/chromedriver-win64/chromedriver.exe"
service = Service(executable_path=webdriver_path)

# 드라이버 실행
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(10)

# 1. 네이버 로그인 페이지 열기
naver_login_url = "https://nid.naver.com/nidlogin.login"
driver.get(naver_login_url)
print("👉 네이버 로그인 페이지가 열렸습니다. 직접 로그인 해주세요.")

# 2. 로그인 완료 후 Enter 입력
input("✅ 네이버 로그인을 완료한 후 콘솔에 Enter를 입력하세요 >> ")

# 3. 블로그 글쓰기 페이지 열기
blog_write_url = "https://blog.naver.com/bibibic__?Redirect=Write&"
driver.get(blog_write_url)

# 4. 글쓰기 창 로딩 대기 (제목 입력창 등장할 때까지)
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.se_textarea"))
)
print("✅ 블로그 글쓰기 페이지 로딩 완료!")

# 5. 제목 입력
title = "자동 업로드 테스트 제목"
title_box = driver.find_element(By.CSS_SELECTOR, "textarea.se_textarea")
title_box.clear()
title_box.send_keys(title)

# 6. 본문 입력 (에디터 iframe 안에 있음)
content = "이 글은 Selenium 자동화로 작성되었습니다.\n발행은 사용자가 직접 클릭해야 합니다."

# 본문 입력용 iframe 찾기
iframe = driver.find_element(By.CSS_SELECTOR, "iframe.se2_input_area")
driver.switch_to.frame(iframe)

# 본문 입력
body = driver.find_element(By.CSS_SELECTOR, "body.se2_inputarea")
body.clear()
body.send_keys(content)

# 다시 기본 문서로 전환
driver.switch_to.default_content()

print("✅ 제목과 본문 입력 완료!")
print("👉 블로그 글쓰기 창에서 [발행] 버튼을 직접 클릭하세요.")

# 7. 브라우저 유지 (사용자가 Ctrl+C 눌러서 종료)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("브라우저를 닫습니다.")
    driver.quit()

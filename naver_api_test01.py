from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# 웹 드라이버 경로 설정 (다운로드한 ChromeDriver의 경로를 입력하세요)
webdriver_path = 'E:/파이썬_실행파일/Workspace2/chromedriver-win64/chromedriver.exe'  # 예시 경로, 실제 경로로 수정 필요

# Service 객체를 사용하여 웹 드라이버 실행
service = Service(executable_path=webdriver_path)
driver = webdriver.Chrome(service=service)

# 네이버 로그인 페이지 URL
naver_login_url = 'https://nid.naver.com/nidlogin.login'

try:
    # 브라우저 열기 및 네이버 로그인 페이지로 이동
    print("네이버 로그인 페이지를 엽니다...")
    driver.get(naver_login_url)
    
    # 페이지 제목 출력 (페이지가 제대로 열렸는지 확인)
    print(f"현재 페이지 제목: {driver.title}")
    
    # 예시: 5초 대기 후 브라우저 닫기
    import time
    time.sleep(5)
    
finally:
    # 모든 작업이 끝나면 브라우저 닫기
    driver.quit()
    print("브라우저를 닫습니다.")

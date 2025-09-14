import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===== 날짜 계산 =====
def get_last_week_range(upload_date: datetime.date):
    monday = upload_date - datetime.timedelta(days=upload_date.weekday())
    friday = monday + datetime.timedelta(days=4)
    if upload_date.weekday() in [5, 6]:  # 토/일이면 이전 주
        monday -= datetime.timedelta(days=7)
        friday -= datetime.timedelta(days=7)
    return monday, friday

# ===== 글쓰기 템플릿 생성 =====
def generate_post_content(monday, friday):
    return f"""
{monday.strftime('%Y년%m월%d일')} ~ {friday.strftime('%Y년%m월%d일')} 배당 일지 입니다.
-------------------------------------------
1. 배당내역
(배당내역 이미지 첨부 예정)
- 상세내역
(상세내역 이미지 첨부 예정)
-------------------------------------------
2. 캘린더
(캘린더 이미지 첨부 예정)
-------------------------------------------
3. 그래프
(배당 그래프 이미지 첨부 예정)
-------------------------------------------
4. 누적 배당금
(누적배당금 이미지 첨부 예정)
"""

# ===== 블로그 포스팅 함수 =====
def post_to_naver(upload_date: datetime.date, img_dir: str, chrome_profile_dir: str):
    monday, friday = get_last_week_range(upload_date)
    title = f"{monday.strftime('%Y년%m월%d일')} ~ {friday.strftime('%Y년%m월%d일')} 배당 일지"
    content = generate_post_content(monday, friday)

    # ===== Chrome 실행 =====
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={chrome_profile_dir}")  # 로그인 상태 유지
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    # options.add_argument("--headless")  # 브라우저 표시하려면 주석

    driver = webdriver.Chrome(options=options)

    # ===== 블로그 글쓰기 페이지 접속 =====
    driver.get("https://blog.naver.com/PostWriteForm.naver")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "subject"))
    )

    # ===== 제목 입력 =====
    title_box = driver.find_element(By.ID, "subject")
    title_box.send_keys(title)

    # ===== 본문 입력 =====
    driver.switch_to.frame("se2_iframe")
    body = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    body.send_keys(content)
    driver.switch_to.default_content()

    # ===== 이미지 업로드 =====
    image_files = [
        "dividend.png",
        "dividend_detail1.png",  # 상세내역 다중 가능
        "calendar.png",
        "graph.png",
        "total.png"
    ]

    for img in image_files:
        file_path = os.path.join(img_dir, img)
        if os.path.exists(file_path):
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(file_path)
            time.sleep(2)

    # ===== 미리보기 =====
    try:
        preview_btn = driver.find_element(By.ID, "btn_preview")  # UI에 따라 ID 확인 필요
        preview_btn.click()
        time.sleep(3)
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        driver.save_screenshot("preview.png")
        print("✅ 미리보기 캡처 저장 완료 (preview.png)")
        driver.switch_to.window(windows[0])
    except Exception as e:
        print("⚠️ 미리보기 실행 실패:", e)

    # ===== 발행 버튼 클릭 =====
    publish_btn = driver.find_element(By.ID, "btn_submit")
    publish_btn.click()
    time.sleep(5)

    print("✅ 블로그 글 작성 완료")
    driver.quit()


# ===== 실행 =====
if __name__ == "__main__":
    today = datetime.date.today()
    img_dir = f"D:/naver/blog/{today.year}/{today.month:02}/{today.day:02}"
    # 새로운 빈 프로필 경로 추천 (기존 Chrome과 충돌 방지)
    chrome_profile_dir = r"E:\Path\To\9\NewProfile"

    print("➡️ Chrome이 열리면 수동으로 로그인 상태 확인 후 글쓰기 페이지로 이동하세요.")
    input("로그인 완료 후 Enter를 눌러 계속 진행...")

    post_to_naver(today, img_dir, chrome_profile_dir)

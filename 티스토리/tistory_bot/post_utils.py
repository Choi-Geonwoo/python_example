import os
import time
import random
import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from upload_image import upload_image

from file_utils import parse_title_and_tags, read_html_file

def write_post(driver, file_name, folder_path, blog_url, category_name, hour_minute, idx):
    wait = WebDriverWait(driver, 20)
    posting_title, tag_list = parse_title_and_tags(file_name)
    file_path = os.path.join(folder_path, file_name)

    driver.get(f"{blog_url}/manage/newpost")
    time.sleep(7)

    # 이어서 작성 팝업 제거
    try:
        alert = driver.switch_to.alert
        alert.dismiss()  # 취소(X)
        print("[ℹ️] 이어서 작성 팝업 닫기 완료")
    except:
        pass

    try:
        wait = WebDriverWait(driver, 2)
        modal = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.modal-content")
        ))
        close_btn = modal.find_element(By.CSS_SELECTOR, "button.modal-close")
        close_btn.click()
        print("[ℹ️] 이어서 작성 모달 닫기 완료")
    except:
        pass

    # 제목 입력
    try:
        title_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea#post-title-inp, input#post-title-inp"))
        )
        title_input.clear()
        pyperclip.copy(posting_title.replace('_', ':'))
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        print(f"[✔] 제목 입력 완료: {posting_title}")
    except TimeoutException:
        print("[❌] 제목 입력란을 찾지 못했습니다.")
        return

    # HTML 모드 전환 (예외 시 무시)
    try:
        driver.find_element(By.ID, "editor-mode-layer-btn-open").click()
        time.sleep(1)
        driver.find_element(By.ID, "editor-mode-html").click()
        time.sleep(1)
        driver.switch_to.alert.accept()
        print("[✔] HTML 모드 전환 완료")
    except Exception:
        pass

    # 카테고리 선택
    try:
        driver.find_element(By.ID, "category-btn").click()
        time.sleep(1)
        driver.find_element(By.XPATH, f"//span[normalize-space()='{category_name}']").click()
        print(f"[✔] 카테고리 선택 완료: {category_name}")
    except NoSuchElementException:
        print("[⚠️] 카테고리 선택 실패 — 기본값으로 진행")

    # 본문 입력
    post_body = read_html_file(file_path)
    driver.find_element(By.CLASS_NAME, "CodeMirror-lines").click()
    pyperclip.copy(post_body)
    ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
    print("[✔] 본문 입력 완료")


    # 이미지 업로드
    #image_path = "./img/stock_chart.jpg"  # 업로드할 이미지 경로
    #upload_image(driver, image_path)


    # 태그 입력
    try:
        tag_input = driver.find_element(By.ID, "tagText")
        tag_input.click()
        for tag in tag_list:
            tag_input.send_keys(tag)
            tag_input.send_keys(Keys.RETURN)
            time.sleep(0.3)
        print(f"[✔] 태그 입력 완료: {', '.join(tag_list)}")
    except Exception as e:
        print(f"[⚠️] 태그 입력 실패: {e}")

    # 발행 설정
    driver.find_element(By.ID, "publish-layer-btn").click()
    time.sleep(1)
    driver.find_element(By.ID, "open20").click()
    time.sleep(1)

    # 댓글 비활성화

    try:
        # 1️⃣ 댓글 허용 버튼 클릭 (드롭다운 열기)
        comment_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.select_btn"))
        )
        driver.execute_script("arguments[0].click();", comment_btn)
        time.sleep(0.5)

        # 2️⃣ '댓글 비허용' 메뉴 클릭
        no_comment_item = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[contains(@class,'mce-menu-item')]//span[text()='댓글 비허용']"
            ))
        )
        driver.execute_script("arguments[0].click();", no_comment_item)
        time.sleep(0.5)

        print("[🚫] 댓글 비활성화 완료")

    except Exception as e:
        print(f"[⚠️] 댓글 비활성화 실패 (무시): {e}")

    except Exception as e:
        print(f"[⚠️] 댓글 비활성화 실패 (무시): {e}")

    # 예약 발행 설정
    reserve_buttons = driver.find_elements(By.CLASS_NAME, "btn_date")
    reserve_buttons[1].click()
    time.sleep(1)

    hour, minute = hour_minute[idx]
    hour_input = driver.find_element(By.XPATH, "(//div[@class='box_date']/input[@type='number'])[1]")
    minute_input = driver.find_element(By.XPATH, "(//div[@class='box_date']/input[@type='number'])[2]")
    hour_input.clear(); hour_input.send_keys(str(hour))
    minute_input.clear(); minute_input.send_keys(str(minute))
    print(f"[⏰] 예약 발행: {hour}:{minute:02d}")

    driver.find_element(By.ID, "publish-btn").click()
    print(f"[🚀] 발행 완료: {posting_title}")
    time.sleep(3)

from selenium.webdriver.common.by import By
import time

def upload_image(driver, image_path):
    """
    티스토리 신에디터 사진 업로드
    """
    try:
        # 1️⃣ input[type='file'] 요소 찾기
        file_input = driver.find_element(By.ID, "attach-image")
        
        # 2️⃣ 이미지 선택
        file_input.send_keys(image_path)
        
        # 3️⃣ 업로드 완료 대기 (필요 시 sleep)
        time.sleep(2)
        
        print(f"[📷] 이미지 업로드 완료: {image_path}")
        
    except Exception as e:
        print(f"[⚠️] 이미지 업로드 실패: {e}")

import os
import pickle
import time

def tistory_login(driver):
    TISTORY_MAIN = "https://www.tistory.com"
    COOKIES_FILE = "tistory_cookies.pkl"

    if not os.path.exists(COOKIES_FILE):
        print("[🚀] 처음 실행입니다. 브라우저가 열리면 로그인하세요 (카카오 로그인 포함).")
        driver.get(TISTORY_MAIN)
        input("로그인 완료 후 엔터 ➤ ")
        pickle.dump(driver.get_cookies(), open(COOKIES_FILE, "wb"))
        print(f"[✔] 쿠키 저장 완료: {COOKIES_FILE}")
    else:
        print("[🔑] 저장된 쿠키로 로그인 복원 중...")
        driver.get(TISTORY_MAIN)
        cookies = pickle.load(open(COOKIES_FILE, "rb"))
        for cookie in cookies:
            if "domain" in cookie and ".tistory.com" in cookie["domain"]:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(3)
        print("[✔] 로그인 복원 완료")

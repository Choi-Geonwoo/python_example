from fetch_yahoo_history.run_fetch import run_html_generation
from driver_utils import init_driver
from login_utils import tistory_login
from post_utils import write_post
from file_utils import get_html_files, delete_all_html

def tistory_write():
    # ① HTML 자동 생성
    html_path = run_html_generation()
    print(f"[🧩] 새 HTML 파일 생성 완료: {html_path}")

    # ② 티스토리 포스팅
    driver = init_driver()
    tistory_login(driver)

    TISTORY_BLOG = "https://disgust.tistory.com"
    CATEGORY_NAME = "국내주식"
    FOLDER_PATH = "./data/tistory/"

    files = get_html_files(FOLDER_PATH)
    for idx, file_name in enumerate(files):
        write_post(driver, file_name, FOLDER_PATH, TISTORY_BLOG, CATEGORY_NAME, [(10, 5)], idx)

    driver.quit()
    print(delete_all_html(FOLDER_PATH))

if __name__ == "__main__":
    tistory_write()

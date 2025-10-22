import webbrowser
import tkinter as tk
import threading
import time
import keyboard
import pyautogui
from PIL import Image, ImageTk, ImageSequence

# ================= 설정 =================
company = "AT&T"
keywords = [
    "개요"
   ,"특징"
   ,"사업동향"
]

urls = [
    "https://gemini.google.com/app?hl=ko",
    "https://www.perplexity.ai/",
    "https://grok.com/",
    "https://chatgpt.com/"
]

# ================= GIF 함수 =================
def open_gif(filename):
    """GIF 파일을 Tkinter 창에서 안정적으로 표시"""
    try:
        root = tk.Tk()
        root.title("GIF 보기")
        root.resizable(False, False)
        root.bind("<Escape>", lambda e: root.destroy())

        img = Image.open(filename)
        frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(img)]

        # 창 크기 중앙 배치
        window_width, window_height = img.size
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        label = tk.Label(root)
        label.pack()

        def get_delay(frame_index):
            delay = img.info.get('duration', 100)
            return max(delay, 20)

        def update(frame_index=0):
            label.config(image=frames[frame_index])
            root.after(get_delay(frame_index), update, (frame_index + 1) % len(frames))

        root.after(0, update)
        root.mainloop()

    except FileNotFoundError:
        print(f"파일 {filename}을 찾을 수 없습니다.")
    except Exception as e:
        print(f"이미지 로드 중 오류: {e}")

def show_gif_threaded(filename):
    """GIF를 별도 스레드로 표시"""
    threading.Thread(target=open_gif, args=(filename,), daemon=True).start()

# ================= 브라우저 탭 열기 =================
def open_chatbot_tabs(url_list):
    for idx, url in enumerate(url_list, start=1):
        print(f"{idx}번째 챗봇 열기: {url}")
        webbrowser.open_new_tab(url)
        time.sleep(2)
    time.sleep(5)  # 로딩 대기

# ================= 마우스 이동/클릭 =================
def move_and_tab(x, y, bool, duration=2):
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click()
    time.sleep(0.5)
    if bool : 
        print("동작여부 " , bool)
        keyboard.press_and_release("tab")

# ================= GIF 관련 함수    =================

def open_gif_with_timer(filename, duration=28):
    """
    GIF를 Tkinter 창에서 표시하면서 남은 시간도 보여줌.
    :param filename: GIF 파일 경로
    :param duration: 표시 시간(초)
    """
    try:
        root = tk.Tk()
        root.title("GIF 보기")
        root.resizable(False, False)
        root.bind("<Escape>", lambda e: root.destroy())

        # 항상 최상위에 표시
        root.attributes('-topmost', True)

        img = Image.open(filename)
        frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(img)]

        window_width, window_height = img.size
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3
        root.geometry(f"{window_width}x{window_height + 30}+{x}+{y}")  # 타이머 공간 확보

        label_img = tk.Label(root)
        label_img.pack()
        label_timer = tk.Label(root, text=f"남은 시간: {duration}s", font=("Arial", 12))
        label_timer.pack()

        start_time = time.time()

        def get_delay(frame_index):
            delay = img.info.get('duration', 100)
            return max(delay, 20)

        def update(frame_index=0):
            elapsed = int(time.time() - start_time)
            remaining = max(duration - elapsed, 0)
            label_timer.config(text=f"남은 시간: {remaining}s")
            if remaining <= 0:
                root.destroy()
                return

            label_img.config(image=frames[frame_index])
            root.after(get_delay(frame_index), update, (frame_index + 1) % len(frames))

        root.after(0, update)
        root.mainloop()

    except Exception as e:
        print(f"GIF 표시 오류: {e}")


def show_gif_threaded(filename, duration=28):
    threading.Thread(target=open_gif_with_timer, args=(filename, duration), daemon=True).start()


# ================= 탭별 키워드 입력 =================
def input_keywords_to_tabs(urls, company, keywords):
    clicked_tab2_first_time = True

    for keyword_text in keywords:
        keyboard.press_and_release("esc")  # ESC로 팝업 닫기

        for tab_index in range(1, len(urls) + 1):
            time.sleep(1)
            keyboard.press_and_release(f"ctrl+{tab_index}")
            time.sleep(2)

            # 특정 탭에서 마우스 클릭
            if tab_index == 2:
                time.sleep(1)
                if clicked_tab2_first_time:
                    move_and_tab(401, 196, clicked_tab2_first_time)
                    clicked_tab2_first_time = False
                else:
                    move_and_tab(659, 632, clicked_tab2_first_time)

            # 키워드 입력
            keyword = f"{company} {keyword_text}"
            print(f"{tab_index}번째 탭에 입력: {keyword}")
            time.sleep(1)
            keyboard.write(keyword)
            time.sleep(1)
            keyboard.press_and_release("enter")

            # 마지막 탭에서 GIF 표시
            if tab_index == len(urls):
                show_gif_threaded("./img/loading.gif")
                time.sleep(30)  # GIF 표시 후 대기

# ================= 메인 =================
if __name__ == "__main__":
    open_chatbot_tabs(urls)
    input_keywords_to_tabs(urls, company, keywords)

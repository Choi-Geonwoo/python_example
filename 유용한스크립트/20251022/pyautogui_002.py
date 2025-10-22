import sys
import threading
import time
import webbrowser
import pyautogui
import keyboard
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QObject

# ================= GIF 함수 =================
def open_gif(filename, duration=28):
    """GIF 파일을 Tkinter 창에서 안정적으로 표시 (상단 중앙, 항상 위)"""
    try:
        root = tk.Tk()
        root.title("GIF 보기")
        root.resizable(False, False)
        root.bind("<Escape>", lambda e: root.destroy())

        # 항상 최상단
        root.attributes('-topmost', True)

        img = Image.open(filename)
        frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(img)]

        # 화면 상단 중앙 배치
        window_width, window_height = img.size
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        x = (screen_width - window_width) // 2  # 화면 가로 중앙
        y = 50  # 화면 상단에서 50px 아래
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        root.geometry(f"{window_width}x{window_height + duration}+{x}+{y}")  # 타이머 공간 확보

        # label = tk.Label(root)
        # label.pack()
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
            label_img.config(image=frames[frame_index])

            if remaining <= 0:
                root.destroy()  # 타이머 종료 시 GIF 창 종료
                return
            
            root.after(get_delay(frame_index), update, (frame_index + 1) % len(frames))

        root.after(0, update)
        root.mainloop()
    except Exception as e:
        print(f"GIF 표시 오류: {e}")


def show_gif_threaded(filename):
    """GIF를 백그라운드 스레드에서 표시"""
    print("호출중")
    threading.Thread(target=open_gif, args=(filename,), daemon=True).start()

# ================= 안전한 메시지 전달용 시그널 =================
class WorkerSignals(QObject):
    finished = pyqtSignal(str, str)  # title, message

# ================= 마우스 이동/클릭 =================
def move_and_tab(x, y, do_tab, duration=2):
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click()
    time.sleep(0.5)
    if do_tab:
        keyboard.press_and_release("tab")

# ================= 브라우저 탭 열기 =================
def open_chatbot_tabs(url_list):
    for url in url_list:
        webbrowser.open_new_tab(url)
        time.sleep(2)
    time.sleep(5)

# ================= 키워드 입력 =================
def input_keywords_to_tabs(urls, company, keywords, mouse_pos1, mouse_pos2):
    clicked_tab2_first_time = True
    for keyword_text in keywords:
        keyboard.press_and_release("esc")
        for tab_index in range(1, len(urls)+1):
            time.sleep(1)
            keyboard.press_and_release(f"ctrl+{tab_index}")
            time.sleep(2)

            if tab_index == 2:
                time.sleep(1)
                if clicked_tab2_first_time:
                    move_and_tab(*mouse_pos1, clicked_tab2_first_time)
                    clicked_tab2_first_time = False
                else:
                    move_and_tab(*mouse_pos2, clicked_tab2_first_time)

            keyword = f"{company} {keyword_text}"
            keyboard.write(keyword)
            time.sleep(1)
            keyboard.press_and_release("enter")

            # ================== 마지막 탭 처리 ==================
            if tab_index == len(urls):
                # GIF 백그라운드 표시
                show_gif_threaded("./img/loading.gif")
                # GIF 표시 시간만큼 대기
                time.sleep(30)  # 필요시 조정


# ================= 백그라운드 작업 스레드 =================
def automation_worker(urls, company, keywords, mouse_pos1, mouse_pos2, signals):
    try:
        open_chatbot_tabs(urls)
        input_keywords_to_tabs(urls, company, keywords, mouse_pos1, mouse_pos2)
        # GIF 표시
        # show_gif_threaded("./img/loading.gif")  # GIF 경로 설정
        signals.finished.emit("완료", "자동화가 완료되었습니다.")
    except Exception as e:
        signals.finished.emit("오류", f"자동화 중 오류 발생: {e}")

# ================= PyQt GUI =================
class ChatbotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("챗봇 자동화 GUI")
        self.setGeometry(200, 200, 600, 500)

        layout = QVBoxLayout()

        # 회사명
        layout.addWidget(QLabel("회사명:"))
        self.company_input = QLineEdit()
        layout.addWidget(self.company_input)

        # 키워드
        layout.addWidget(QLabel("키워드 (콤마로 구분):"))
        self.keywords_input = QLineEdit()
        self.keywords_input.setText("개요,특징,사업동향")
        layout.addWidget(self.keywords_input)

        # 마우스 위치
        layout.addWidget(QLabel("마우스 위치 (x,y) - 첫 번째 클릭:"))
        self.mouse_input1 = QLineEdit()
        self.mouse_input1.setText("401,196")
        layout.addWidget(self.mouse_input1)

        layout.addWidget(QLabel("마우스 위치 (x,y) - 두 번째 클릭:"))
        self.mouse_input2 = QLineEdit()
        self.mouse_input2.setText("659,635")
        layout.addWidget(self.mouse_input2)

        # URL 입력
        layout.addWidget(QLabel("챗봇 URL (줄바꿈으로 구분):"))
        self.urls_input = QTextEdit()
        self.urls_input.setPlainText(
            "https://gemini.google.com/app?hl=ko\nhttps://www.perplexity.ai/\nhttps://grok.com/\nhttps://chatgpt.com/"
        )
        layout.addWidget(self.urls_input)

        # 실행 버튼
        self.run_button = QPushButton("자동화 실행")
        self.run_button.clicked.connect(self.run_automation)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

        # 시그널 객체
        self.signals = WorkerSignals()
        self.signals.finished.connect(self.show_message)

    def run_automation(self):
        company = self.company_input.text().strip()
        keywords = [k.strip() for k in self.keywords_input.text().split(",") if k.strip()]
        urls = [u.strip() for u in self.urls_input.toPlainText().splitlines() if u.strip()]

        try:
            mouse_pos1 = tuple(map(int, self.mouse_input1.text().split(",")))
            mouse_pos2 = tuple(map(int, self.mouse_input2.text().split(",")))
        except:
            QMessageBox.warning(self, "입력 오류", "마우스 위치는 x,y 형식으로 입력해주세요.")
            return

        if not company or not keywords or not urls:
            QMessageBox.warning(self, "입력 오류", "회사명, 키워드, URL을 모두 입력해주세요.")
            return

        threading.Thread(
            target=automation_worker,
            args=(urls, company, keywords, mouse_pos1, mouse_pos2, self.signals),
            daemon=True
        ).start()

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)

        # 항상 최상단
        msg_box.setWindowFlag(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg_box.setWindowModality(Qt.WindowModality.ApplicationModal)
        msg_box.exec()  # 모달로 띄우기


# ================= 실행 =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatbotGUI()
    window.show()
    sys.exit(app.exec())

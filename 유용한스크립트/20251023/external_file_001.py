import time
import pyperclip
import pyautogui
import keyboard
from pywinauto import Desktop

urls = [
    "https://gemini.google.com/app?hl=ko",
    "https://www.perplexity.ai/",
    "https://chatgpt.com/"
]

# ================= 마우스 이동 및 클릭 =================
def move_and_tab(x: int, y: int, press_tab: bool = False, duration: float = 2):
    """
    마우스를 이동하고 클릭 후, 필요 시 Tab 키 입력
    """
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click()
    print(f"마우스 클릭 완료 at ({x}, {y})")
    time.sleep(1.5)
    if press_tab:
        keyboard.press_and_release("tab")
        print(f"Tab 키 입력 완료 {press_tab}")

# ================= 클립보드 복사 및 붙여넣기 =================
def copy_and_paste(value: str, x: int = 1018, y: int = 933):
    """
    클립보드에 복사 후, 마우스 클릭 및 키보드 입력
    """
    pyperclip.copy(value)
    time.sleep(0.5)  # 클립보드 안정화 대기

    press_tab = True
    for tab_index, url in enumerate(urls, start=1):

        if url == "https://www.perplexity.ai/":
            press_tab = False
        else:
            x=740
            y=910
            #press_tab = True
        time.sleep(2)
        keyboard.press_and_release(f"ctrl+{tab_index}")
        # 마우스 이동 및 클릭
        move_and_tab(x, y, press_tab, duration=1)
        print(f"Ctrl+{tab_index} 키 입력 완료 ({value}) url: {url}\n")
        time.sleep(1)
        # 키보드로 붙여넣기
        keyboard.write(value)
        
        time.sleep(1.5)  # 입력 안정화 대기
        #keyboard.press_and_release("enter")
    

    # 붙여넣기 결과 확인
    pasted_text = pyperclip.paste()
    # print("Pasted Text:", pasted_text)

# ================= 브라우저(Edge) 체크 =================
def browser_check(window_title: str = "Edge") -> bool:
    """
    현재 데스크톱의 Edge 창을 찾고, 포커스 및 최대화
    """
    windows = Desktop(backend="uia").windows()
    
    for w in windows:
        if window_title in w.window_text():
            w.set_focus()
            w.restore()   # 최소화 복원
            w.maximize()  # 최대화
            print(f"{window_title} 창으로 포커스 이동 완료")
            return True

    print(f"{window_title} 실행 중 아님")
    return False

# ================= 파일 섹션 로드 =================
def load_sections(file_path: str, separator: str = "------------------") -> list:
    """
    파일을 섹션 단위로 나누어 리스트 반환
    """
    sections = []
    with open(file_path, 'r', encoding='utf-8') as f:
        current_section = []
        for line in f:
            line = line.strip()
            if line == separator:
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []
            else:
                current_section.append(line)
        if current_section:
            sections.append("\n".join(current_section))
    return sections

# ================= 메인 실행 =================
if __name__ == "__main__":
    file_path = "example.templates"
    sections = load_sections(file_path)
    
    edge_ready = False
    for i, section in enumerate(sections, 1):
        print("================= 섹션 출력 =================")
        print(f"Section {i}:\n{section}\n")
        time.sleep(1)  # 섹션 출력 후 대기
        
        if i == 1:
            # 첫 섹션 처리 전 브라우저 체크
            edge_ready = browser_check()
        
        if edge_ready:
            # 섹션 내용을 클립보드에 복사 및 붙여넣기
            copy_and_paste(section)
        print("================= 섹션 종료 =================")

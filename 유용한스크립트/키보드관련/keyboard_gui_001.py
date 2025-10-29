import tkinter as tk
from tkinter import messagebox
import keyboard
import pyperclip
import json
import time
import os

CONFIG_FILE = 'custom_values.json'

# ------------------------------
# 1. 파일에서 값 불러오기
# ------------------------------
def load_custom_values():
    global custom_values
    default_values = {f'ctrl+{i}': '' for i in range(10)}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                custom_values = json.load(f)
        except Exception as e:
            print(f"설정 파일 로드 실패: {e}")
            custom_values = default_values
    else:
        custom_values = default_values

load_custom_values()
custom_values = custom_values
entries = {}

# ------------------------------
# 2. 값 저장 및 파일에 쓰기
# ------------------------------
def update_custom_values():
    global custom_values
    for i in range(10):
        key = f'ctrl+{i}'
        custom_values[key] = entries[key].get()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(custom_values, f, indent=4)
        messagebox.showinfo("저장 완료", f"사용자 정의 값이 {CONFIG_FILE}에 저장되었습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"값 저장 중 오류 발생: {e}")

# ------------------------------
# 3. 초기화 함수
# ------------------------------
def reset_custom_values():
    for i in range(10):
        key = f'ctrl+{i}'
        custom_values[key] = ''
        entries[key].delete(0, tk.END)
    update_custom_values()    
    messagebox.showinfo("초기화 완료", "모든 값이 초기화되었습니다.")

# ------------------------------
# 4. 붙여넣기 함수
# ------------------------------
def paste_custom_value(key_combination):
    text_to_paste = custom_values.get(key_combination)
    if not text_to_paste:
        return
    pyperclip.copy(text_to_paste)
    time.sleep(0.05)
    keyboard.press_and_release('ctrl+v')
    print(f"[{key_combination}] - '{text_to_paste}' 붙여넣기 완료.")

# ------------------------------
# 5. 핫키 등록
# ------------------------------
def setup_hotkeys():
    for i in range(10):
        key = f'ctrl+{i}'
        keyboard.add_hotkey(key, paste_custom_value, args=(key,), suppress=True)
    print("✅ 핫키 (Ctrl+0 ~ Ctrl+9) 등록 완료.")

# ------------------------------
# 6. GUI 생성
# ------------------------------
def create_gui():
    root = tk.Tk()
    root.title("자동 붙여넣기 설정")
    root.geometry("330x365")
    root.resizable(False, False)

    # Entry와 Label 생성
    for i in range(10):
        tk.Label(root, text=f"Ctrl + {i} 값:").grid(row=i, column=0, padx=10, pady=5, sticky='e')
        entry = tk.Entry(root, width=30)
        entry.insert(0, custom_values.get(f'ctrl+{i}', ''))
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[f'ctrl+{i}'] = entry

    # 버튼 프레임
    button_frame = tk.Frame(root)
    button_frame.grid(row=10, column=0, columnspan=2, pady=15)

    save_button = tk.Button(button_frame, text="값 저장", command=update_custom_values, width=15)
    save_button.pack(side=tk.LEFT, padx=10)

    reset_button = tk.Button(button_frame, text="초기화", command=reset_custom_values, width=15)
    reset_button.pack(side=tk.LEFT, padx=10)

    setup_hotkeys()
    
    # ------------------------------
    # Enter 키 눌렀을 때 저장
    # ------------------------------
    def save_on_enter(event):
        update_custom_values()

    root.bind('<Return>', save_on_enter)  # Enter 키 바인딩


    root.protocol("WM_DELETE_WINDOW", lambda: root.quit())
    root.mainloop()

if __name__ == "__main__":
    create_gui()

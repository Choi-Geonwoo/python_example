import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import pyperclip
import json
import time
import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

CONFIG_FILE = 'secure_data.json'
KEY_FILE = 'secret.key'

# ------------------------------
# 1. AES-GCM 암호화 관련 함수
# ------------------------------
def generate_key():
    """AES-GCM용 256비트 키 생성 및 저장"""
    key = get_random_bytes(32)
    with open(KEY_FILE, 'wb') as f:
        f.write(key)
    return key

def load_key():
    """저장된 키 불러오기 (없으면 새로 생성)"""
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, 'rb') as f:
        return f.read()

def encrypt_data(data, key):
    """데이터(AES-GCM 암호화 후 Base64 인코딩)"""
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(json.dumps(data).encode('utf-8'))
    return {
        'nonce': base64.b64encode(cipher.nonce).decode(),
        'tag': base64.b64encode(tag).decode(),
        'ciphertext': base64.b64encode(ciphertext).decode()
    }

def decrypt_data(json_data, key):
    """암호화된 JSON을 복호화"""
    nonce = base64.b64decode(json_data['nonce'])
    tag = base64.b64decode(json_data['tag'])
    ciphertext = base64.b64decode(json_data['ciphertext'])
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return json.loads(plaintext.decode('utf-8'))

# ------------------------------
# 2. 설정 로드
# ------------------------------
def load_custom_values():
    default_values = {f'ctrl+{i}': '' for i in range(10)}
    key = load_key()

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                encrypted_json = json.load(f)
            return decrypt_data(encrypted_json, key)
        except Exception as e:
            print(f"⚠️ 설정 파일 복호화 실패: {e}")
            return default_values
    return default_values

custom_values = load_custom_values()
entries = {}
key = load_key()

# ------------------------------
# 3. 파일 저장 함수
# ------------------------------
def save_to_file():
    try:
        encrypted_json = encrypt_data(custom_values, key)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(encrypted_json, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("오류", f"값 저장 중 오류 발생: {e}")
        return False

# ------------------------------
# 4. custom_values 갱신
# ------------------------------
def update_custom_values():
    for i in range(10):
        key_comb = f'ctrl+{i}'
        custom_values[key_comb] = entries[key_comb].get()

# ------------------------------
# 5. 버튼 함수들
# ------------------------------
def save_button_clicked():
    update_custom_values()
    if save_to_file():
        messagebox.showinfo("저장 완료", f"값이 {CONFIG_FILE}에 안전하게 암호화되어 저장되었습니다.")

def reset_custom_values():
    for i in range(10):
        key_comb = f'ctrl+{i}'
        custom_values[key_comb] = ''
        entries[key_comb].delete(0, tk.END)
    if save_to_file():
        messagebox.showinfo("초기화 완료", "모든 값이 초기화되었습니다.")

def del_function(i):
    key_comb = f'ctrl+{i}'
    custom_values[key_comb] = ''
    entries[key_comb].delete(0, tk.END)
    if save_to_file():
        messagebox.showinfo(f"{i} 삭제 완료", f"Ctrl+{i} 값이 삭제되었습니다.")

# ------------------------------
# 6. 붙여넣기 기능
# ------------------------------
def paste_custom_value(key_combination):
    text_to_paste = custom_values.get(key_combination)
    if not text_to_paste:
        return
    pyperclip.copy(text_to_paste)
    time.sleep(0.05)
    keyboard.press_and_release('ctrl+v')
    print(f"[{key_combination}] '{text_to_paste}' 붙여넣기 완료.")

def setup_hotkeys():
    for i in range(10):
        key_comb = f'ctrl+{i}'
        keyboard.add_hotkey(key_comb, paste_custom_value, args=(key_comb,), suppress=True)
    print("✅ 핫키 등록 완료 (Ctrl+0~9)")

# ------------------------------
# 7. GUI 생성
# ------------------------------
def create_gui():
    root = tk.Tk()
    root.title("🔐 자동 붙여넣기 설정 (AES-GCM 보안 저장)")
    root.geometry("460x525")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=('Segoe UI', 10), padding=6)
    style.configure("TLabel", font=('Segoe UI', 10))
    style.configure("TEntry", padding=3)

    main_frame = ttk.Frame(root, padding=15)
    main_frame.pack(fill='both', expand=True)

    ttk.Label(main_frame, text="Ctrl+숫자 단축키 자동 붙여넣기", font=('Segoe UI Semibold', 12)).grid(
        row=0, column=0, columnspan=3, pady=(0, 10)
    )

    for i in range(10):
        ttk.Label(main_frame, text=f"Ctrl + {i}:").grid(row=i+1, column=0, sticky='e', padx=5, pady=3)
        entry = ttk.Entry(main_frame, width=35)
        entry.insert(0, custom_values.get(f'ctrl+{i}', ''))
        entry.grid(row=i+1, column=1, padx=5, pady=3)
        entries[f'ctrl+{i}'] = entry

        del_btn = ttk.Button(main_frame, text="삭제", command=lambda i=i: del_function(i))
        del_btn.grid(row=i+1, column=2, padx=5, pady=3)

    # 버튼 프레임
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=12, column=0, columnspan=3, pady=15)

    ttk.Button(button_frame, text="💾 값 저장", command=save_button_clicked).pack(side='left', padx=10)
    ttk.Button(button_frame, text="🔄 초기화", command=reset_custom_values).pack(side='left', padx=10)

    setup_hotkeys()

    root.bind('<Return>', lambda e: save_button_clicked())
    root.bind('<Control-s>', lambda e: save_button_clicked())

    # 창 중앙 배치
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()

if __name__ == "__main__":
    create_gui()

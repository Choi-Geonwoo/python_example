import tkinter as tk
from tkinter import messagebox
import secrets
import string

# -------------------------
DEFAULT_USERNAME_LENGTH = 8
DEFAULT_PASSWORD_LENGTH = 14

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SPECIAL = "!@#$%&_+=-"
PASSWORD_POOL = LOWER + UPPER + DIGITS + SPECIAL
# -------------------------

def generate_username(length=DEFAULT_USERNAME_LENGTH):
    return ''.join(secrets.choice(string.ascii_lowercase) for _ in range(length))

def generate_password(length=DEFAULT_PASSWORD_LENGTH):
    if length < 4:
        raise ValueError("비밀번호 길이는 최소 4 이상이어야 합니다.")
    parts = [
        secrets.choice(LOWER),
        secrets.choice(UPPER),
        secrets.choice(DIGITS),
        secrets.choice(SPECIAL),
    ]
    remaining = length - len(parts)
    parts += [secrets.choice(PASSWORD_POOL) for _ in range(remaining)]
    secrets.SystemRandom().shuffle(parts)
    return ''.join(parts)

def generate_credentials():
    try:
        uname_len = int(username_len_var.get())
        pwd_len = int(password_len_var.get())
        if uname_len < 1:
            messagebox.showwarning("입력 오류", "아이디 길이는 1 이상이어야 합니다.")
            return
        if pwd_len < 4:
            messagebox.showwarning("입력 오류", "비밀번호 길이는 4 이상이어야 합니다.")
            return
    except ValueError:
        messagebox.showwarning("입력 오류", "길이는 숫자로 입력해야 합니다.")
        return
    
    username_var.set(generate_username(uname_len))
    password_var.set(generate_password(pwd_len))

# -------------------------
root = tk.Tk()
root.title("랜덤 아이디/비밀번호 생성기")
root.geometry("500x210")

username_var = tk.StringVar()
password_var = tk.StringVar()
username_len_var = tk.StringVar(value=str(DEFAULT_USERNAME_LENGTH))
password_len_var = tk.StringVar(value=str(DEFAULT_PASSWORD_LENGTH))

LABEL_FONT = ("Arial", 14)
PAD_X = 10
PAD_Y = 10

# Grid 배치
tk.Label(root, text="아이디 길이:", font=LABEL_FONT).grid(row=0, column=0, padx=PAD_X, pady=PAD_Y, sticky="e")
tk.Entry(root, textvariable=username_len_var, width=6, font=LABEL_FONT).grid(row=0, column=1, padx=PAD_X, pady=PAD_Y)

tk.Label(root, text="비밀번호 길이:", font=LABEL_FONT).grid(row=0, column=2, padx=PAD_X, pady=PAD_Y, sticky="e")
tk.Entry(root, textvariable=password_len_var, width=6, font=LABEL_FONT).grid(row=0, column=3, padx=PAD_X, pady=PAD_Y)

tk.Label(root, text="아이디:", font=LABEL_FONT).grid(row=1, column=0, padx=PAD_X, pady=PAD_Y, sticky="e")
tk.Entry(root, textvariable=username_var, width=32, font=LABEL_FONT, state='readonly').grid(row=1, column=1, columnspan=3, padx=PAD_X, pady=PAD_Y)

tk.Label(root, text="비밀번호:", font=LABEL_FONT).grid(row=2, column=0, padx=PAD_X, pady=PAD_Y, sticky="e")
tk.Entry(root, textvariable=password_var, width=32, font=LABEL_FONT, state='readonly').grid(row=2, column=1, columnspan=3, padx=PAD_X, pady=PAD_Y)

tk.Button(root, text="생성", font=LABEL_FONT, command=generate_credentials).grid(row=3, column=0, columnspan=4, pady=PAD_Y)

for i in range(4):
    root.grid_columnconfigure(i, weight=1)

root.mainloop()

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# 한글 인코딩 설정
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def folder_select():
    global dir_path
    dir_path = filedialog.askdirectory(initialdir="/", title="폴더를 선택 해 주세요")
    if not dir_path:
        messagebox.showwarning("경고", "폴더를 선택 하세요")
    else:
        res = list_files(dir_path)
        ent2.delete(0, tk.END)
        if not res:
            messagebox.showwarning("경고", "폴더 내에 파일이 없습니다.")
        else:
            ent2.insert(0, dir_path)
            for file in res:
                treeview.insert("", "end", values=[dir_path, file], iid=file)

def list_files(startpath):
    file_list = []
    for root, dirs, files in os.walk(startpath):
        for file in files:
            file_list.append(file)
    return file_list

def fileNm_search():
    fileNm = ent1.get()
    if not dir_path:
        messagebox.showwarning("경고", "폴더를 먼저 선택하세요.")
        return

    found = False
    for child in treeview.get_children():
        values = treeview.item(child, 'values')
        if fileNm.lower() in values[1].lower():
            treeview.selection_set(child)
            found = True
            break

    if not found:
        messagebox.showinfo("알림", f"'{fileNm}' 파일을 찾을 수 없습니다.")

root = tk.Tk()
root.title("Camp Lee Python")
root.geometry("815x290")
root.resizable(False, False)  # 수평 및 수직 크기 조절 비활성화

dir_path = None
treeview = ttk.Treeview(root, columns=["path", "fileName"], displaycolumns=["path", "fileName"])
treeview.column("path", width=400, anchor="center")
treeview.heading("path", text="경로", anchor="center")
treeview.column("fileName", width=400, anchor="center")
treeview.heading("fileName", text="파일명", anchor="center")
treeview["show"] = "headings"

ent1 = tk.Entry(font=('맑은 고딕', 10, 'bold'), bg='white', width=20)
ent2 = tk.Entry(font=('맑은 고딕', 10, 'bold'), bg='white', width=20)

ent1.grid(row=2, column=2)
tk.Button(root, text="파일명검색", width=10, command=fileNm_search).grid(row=2, column=3)
ent2.grid(row=1, column=2)
tk.Button(root, text="경로선택", width=10, command=folder_select).grid(row=1, column=3)
treeview.grid(row=3, column=2, columnspan=2, padx=5, pady=5)

root.mainloop()

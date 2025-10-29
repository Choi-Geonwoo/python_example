import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# 한글 인코딩 설정
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

class MyWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('Excel Viewer')
        self.root.geometry('600x700')

        self.df_list = [] # DataFrame을 저장할 리스트
        self.header_options = [] # 헤더 옵션 목록


        # 검색 프레임 생성
        self.search_frame = ttk.Frame(root)
        self.search_frame.pack(fill='x')
        
        # 전체 항목과 헤더 옵션을 포함한 드롭다운 목록 생성
        self.dropdown_var = tk.StringVar(root)
        self.dropdown = ttk.Combobox(self.search_frame, textvariable=self.dropdown_var, state='readonly')
        self.dropdown.pack(side='left', padx=5, pady=5)
        self.dropdown.bind("<<ComboboxSelected>>", self.onDropdownSelect)

        # 검색 입력 상자 생성
        self.search_entry = ttk.Entry(self.search_frame)
        self.search_entry.pack(side='left', padx=5, pady=5, fill='x', expand=True)
        

        # 검색 버튼 생성
        self.search_btn = ttk.Button(self.search_frame, text='검색', command=self.searchData)
        self.search_btn.pack(side='left', padx=5, pady=5)
        
        # 엑셀 버튼
        self.open_btn = ttk.Button(self.search_frame, text='엑셀 파일', command=self.clickOpenBtn)
        self.open_btn.pack(side='right', padx=5, pady=5)
        

        # 엑셀 파일 열기 버튼에 이벤트 바인딩
        self.open_btn.bind('<Button-1>', self.clickOpenBtn)

        # 테이블 프레임 생성
        self.table_frame = ttk.Frame(root)
        self.table_frame.pack(expand=True, fill='both')

        # 테이블 생성
        self.table = ttk.Treeview(self.table_frame)
        self.table.pack(side='left', expand=True, fill='both')

        # 수직 스크롤바 생성
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient='vertical', command=self.table.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.table.configure(yscrollcommand=self.scrollbar.set)

    # 엑셀 파일 열기 버튼 클릭 시 실행될 함수
    def clickOpenBtn(self, event=None):
        # 파일 선택 대화 상자 열기
        file_path = filedialog.askopenfilename(filetypes=[('Excel files', '*.xls *.xlsx')])
        if file_path:
            # 선택한 파일의 데이터를 불러와 리스트에 저장
            self.df_list = self.loadData(file_path)
            # 첫 번째 시트의 데이터로 테이블 초기화
            self.initTableWidget(0)
            # 헤더 옵션 목록 설정
            self.setHeaderOptions()

    # 엑셀 파일 데이터 로드 함수
    def loadData(self, file_name):
        df_list = []
        with pd.ExcelFile(file_name) as wb:
            for i, sn in enumerate(wb.sheet_names):
                try:
                    df = pd.read_excel(wb, sheet_name=sn)
                except Exception as e:
                    print('File read error:', e)
                else:
                    df = df.fillna(0)
                    df.name = sn
                    df_list.append(df)
        return df_list

    # 테이블 위젯 초기화 함수
    def initTableWidget(self, id):
        # 기존 테이블 데이터 삭제
        self.table.delete(*self.table.get_children())
        # 선택한 데이터프레임 가져오기
        df = self.df_list[id]
        # 테이블 열 설정
        self.table['columns'] = list(df.columns)
        self.table.heading('#0', text='Index') # 인덱스 열 설정
        # 각 열의 제목과 너비 설정
        for col in df.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=50, minwidth=50)
        # 각 행의 데이터 추가
        for i, row in df.iterrows():
            self.table.insert('', 'end', text=i, values=list(row))

    # 헤더 옵션 목록 설정 함수
    def setHeaderOptions(self):
        # 첫 번째 데이터프레임에서 열 이름 가져오기
        df = self.df_list[0]
        self.header_options = ['전체'] + list(df.columns)
        # 드롭다운 목록에 헤더 옵션 설정
        self.dropdown['values'] = self.header_options
        # 첫 번째 항목 선택
        self.dropdown_var.set(self.header_options[0])

    # 드롭다운 선택 시 실행되는 함수
    def onDropdownSelect(self, event=None):
        # 드롭다운에서 선택된 항목 가져오기
        selected_option = self.dropdown_var.get()
        # 검색 입력 상자에 선택된 항목 설정
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, selected_option)

    # 검색 버튼 클릭 시 실행되는 함수
    def searchData(self):
        # 검색어와 선택된 항목 가져오기
        search_text = self.search_entry.get().lower()
        selected_option = self.dropdown_var.get()
        if search_text:
            for item in self.table.get_children():
                # 선택된 항목에 따라 검색 수행
                if selected_option == '전체':
                    found = False
                    for value in self.table.item(item, 'values'):
                        if search_text in str(value).lower():
                            found = True
                            break
                    if found:
                        self.table.selection_add(item)  # 검색 결과가 있는 행 선택
                    else:
                        self.table.selection_remove(item)  # 검색 결과가 없는 행 선택 해제
                else:
                    value = str(self.table.item(item, 'values')[self.header_options.index(selected_option) - 1]).lower()
                    if search_text in value:
                        self.table.selection_add(item)  # 검색 결과가 있는 행 선택
                    else:
                        self.table.selection_remove(item)  # 검색 결과가 없는 행 선택 해제

if __name__ == '__main__':
    root = tk.Tk()
    app = MyWindow(root)
    root.mainloop()

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
# 인베스팅 닷컴 전체 지수를 가져오는 것을 화면에 버튼을 이용해서 다운로드할 수 있도록 하는 코드
def fetch_and_save():
    today = datetime.now().strftime("%Y-%m-%d")
    url = "https://kr.investing.com/"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            messagebox.showerror("오류", f"페이지 요청 실패: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            messagebox.showerror("오류", "테이블을 찾을 수 없습니다. 페이지가 JS로 렌더링될 수 있습니다.")
            return

        # 데이터 추출 함수
        def extract_investing_data(html):
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table')
            if not table:
                return pd.DataFrame()
            
            thead = table.find('thead')
            headers = [th.get_text(strip=True) for th in thead.find_all('th')] if thead else ["종목명","종가","고가","저가","변동","변동 %","시간"]
            
            tbody = table.find('tbody')
            data_rows = []
            for row in tbody.find_all('tr'):
                cols = row.find_all('td')
                if not cols:
                    continue
                name_element = cols[0].find('a')
                stock_name = name_element.get('title') if name_element else cols[0].get_text(strip=True)
                values = [col.get_text(strip=True) for col in cols[1:]]
                time_text = cols[-1].find('time').get_text(strip=True) if cols[-1].find('time') else values[-1]
                row_data = [stock_name] + values[:-1] + [time_text]
                data_rows.append(row_data)
            
            df = pd.DataFrame(data_rows, columns=headers)
            return df

        df = extract_investing_data(response.text)
        filename = f"investing_indices_{today}.xlsx"

        # 엑셀로 저장 및 마지막 행에 실행일자 추가
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Indices')
            worksheet = writer.sheets['Indices']
            last_row = len(df) + 2
            worksheet.cell(row=last_row, column=1, value=f"실행일자: {today}")
        
        messagebox.showinfo("완료", f"{filename} 파일로 저장 완료!")
    except Exception as e:
        messagebox.showerror("오류", str(e))

# GUI 생성
root = tk.Tk()
root.title("Investing.com 데이터 저장")
root.geometry("400x200")

label = tk.Label(root, text="Investing.com 지수 데이터를 엑셀로 저장합니다", font=("Arial", 12))
label.pack(pady=20)

btn = tk.Button(root, text="데이터 가져오기", font=("Arial", 14), bg="skyblue", command=fetch_and_save)
btn.pack(pady=20)

root.mainloop()

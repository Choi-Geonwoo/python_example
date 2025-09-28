import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
# 인베스팅 닷컴의 전체 지수 가져오고 엑셀로 저장하는 코드
# 오늘 날짜 구하기
today = datetime.now().strftime("%Y-%m-%d")

url = "https://kr.investing.com/indices/major-indices/"
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if table:
        def extract_investing_data(html):
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table')
            if not table:
                return pd.DataFrame()
            
            # 헤더 추출
            thead = table.find('thead')
            headers = [th.get_text(strip=True) for th in thead.find_all('th')] if thead else ["종목명","종가","고가","저가","변동","변동 %","시간"]
            
            # 데이터 추출
            tbody = table.find('tbody')
            data_rows = []
            for row in tbody.find_all('tr'):
                cols = row.find_all('td')
                if not cols:
                    continue
                # 종목명
                name_element = cols[0].find('a')
                stock_name = name_element.get('title') if name_element else cols[0].get_text(strip=True)
                # 나머지 값
                values = [col.get_text(strip=True) for col in cols[1:]]
                # 시간
                time_text = cols[-1].find('time').get_text(strip=True) if cols[-1].find('time') else values[-1]
                row_data = [stock_name] + values[:-1] + [time_text]
                data_rows.append(row_data)
            
            df = pd.DataFrame(data_rows, columns=headers)
            return df
        
        df = extract_investing_data(response.text)
        print("📊 투자 지수 데이터:\n", df)
        
        # 파일명에 실행일자 포함
        filename = f"investing_indices_{today}.xlsx"
        
        # 엑셀로 저장 (마지막에 실행일자 한 줄 추가)
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Indices')
            
            # 마지막 행 추가
            workbook = writer.book
            worksheet = writer.sheets['Indices']
            last_row = len(df) + 2  # 엑셀 기준, 헤더 + 데이터
            worksheet.cell(row=last_row, column=1, value=f"기준일자: {today}")
        
        print(f"✅ {filename} 파일로 저장 완료")
    else:
        print("❌ 테이블을 찾을 수 없습니다. 페이지가 JS로 렌더링될 가능성이 있습니다.")

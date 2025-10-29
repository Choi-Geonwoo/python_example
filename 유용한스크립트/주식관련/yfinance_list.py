from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import html
import time
from datetime import datetime, timedelta

def fetch_yahoo_history(tickers):
    headers = ["날짜(KST)", "시가", "고가", "저가", "종가", "조정 종가", "거래량"]
    header_widths = [11, 7, 8, 8, 8, 7, 14]
    body_widths = [12, 10, 10, 10, 10, 12, 14]

    result = {}  # 모든 종목 데이터 저장 (종목별 문자열 리스트)

    # 크롬 헤드리스 옵션 설정
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)

    for ticker in tickers:
        print(f"\n📈 {ticker} 과거 데이터 가져오는 중...\n")
        url = f"https://finance.yahoo.com/quote/{ticker}/history"
        driver.get(url)
        time.sleep(5)  # JS 데이터 로딩 대기

        parser = html.fromstring(driver.page_source)
        rows = parser.xpath('//table[contains(@class, "table yf-1jecxey")]/tbody/tr')

        if not rows:
            print("⚠️ 테이블을 찾을 수 없습니다.")
            result[ticker] = []
            continue

        # 헤더 출력
        header_line = " | ".join([h.center(w) for h, w in zip(headers, header_widths)])
        print(header_line)
        print("-" * len(header_line))

        ticker_data = []
        for r in rows[:10]:  # 상위 10행만
            cols = [c.text_content().strip() for c in r.xpath('./td')]
            if len(cols) == 7:
                # 날짜 변환
                dt = datetime.strptime(cols[0], "%b %d, %Y")
                dt_kst = dt + timedelta(hours=9)
                cols[0] = dt_kst.strftime("%Y-%m-%d")

                # 거래량 처리 없이 그대로 유지
                # cols[6] = cols[6].replace(',', '')

                # 콘솔 출력
                row_line = " | ".join([col.rjust(w) for col, w in zip(cols, body_widths)])
                print(row_line)

                # 문자열 그대로 리스트에 저장
                ticker_data.append(" | ".join(cols))

        result[ticker] = ticker_data

    driver.quit()
    return result

if __name__ == "__main__":
    tickers = ["AAPL", "TSLA", "GOOGL"]
    result = fetch_yahoo_history(tickers)
    
    # 확인용 출력
    # for ticker, rows in result.items():
    #     print(f"\n=== {ticker} 데이터 확인 ===")
    #     for row in rows:
    #         print(row)
